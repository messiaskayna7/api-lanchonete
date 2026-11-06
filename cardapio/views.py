from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .ibge import UFS_VALIDAS, IBGEIndisponivel, listar_municipios
from .models import AreaEntrega, Categoria, Produto
from .serializers import AreaEntregaSerializer, CategoriaSerializer, ProdutoSerializer


# ModelViewSet já entrega as 5 ações do CRUD prontas:
#   list (GET /), retrieve (GET /{id}/), create (POST /),
#   update (PUT /{id}/), partial_update (PATCH /{id}/), destroy (DELETE /{id}/)
# Só precisamos dizer QUAIS dados (queryset) e COMO converter (serializer_class).


class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    # SearchFilter: permite ?search=lanche
    filter_backends = [filters.SearchFilter]
    search_fields = ['nome']

    # @action cria uma rota extra dentro do viewset.
    # detail=True -> a rota usa o id: /api/categorias/{id}/produtos/
    @action(detail=True, methods=['get'])
    def produtos(self, request, pk=None):
        categoria = self.get_object()  # busca a categoria ou devolve 404
        # related_name='produtos' permite acessar os produtos assim:
        produtos = categoria.produtos.all()

        # Usa a mesma paginação das outras listagens
        pagina = self.paginate_queryset(produtos)
        if pagina is not None:
            serializer = ProdutoSerializer(pagina, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = ProdutoSerializer(produtos, many=True)
        return Response(serializer.data)


@extend_schema(
    parameters=[
        OpenApiParameter('disponivel', bool, description='Filtra por disponibilidade (true/false)'),
    ]
)
class ProdutoViewSet(viewsets.ModelViewSet):
    serializer_class = ProdutoSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['nome']
    # Necessário para o router descobrir o nome da rota, já que usamos get_queryset
    queryset = Produto.objects.all()

    def get_queryset(self):
        # select_related busca a categoria na mesma consulta (evita uma query por produto)
        queryset = Produto.objects.select_related('categoria')

        # Lê o parâmetro da URL: /api/produtos/?disponivel=true
        disponivel = self.request.query_params.get('disponivel')
        if disponivel is not None:
            valor = disponivel.lower()
            if valor in ('true', '1', 'sim'):
                queryset = queryset.filter(disponivel=True)
            elif valor in ('false', '0', 'nao', 'não'):
                queryset = queryset.filter(disponivel=False)
        return queryset


class AreaEntregaViewSet(viewsets.ModelViewSet):
    """Extra C5: CRUD das áreas de entrega (o código IBGE é validado no serializer)."""

    queryset = AreaEntrega.objects.all()
    serializer_class = AreaEntregaSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['municipio']


class MunicipiosView(APIView):
    """Extra C2: consulta os municípios de uma UF na API do IBGE.

    Aqui a nossa API CONSOME outra API (o IBGE) e repassa só o necessário.
    """

    permission_classes = [AllowAny]  # é só leitura, qualquer um pode consultar

    @extend_schema(
        parameters=[OpenApiParameter('uf', str, required=True, description='Sigla do estado, ex.: PE')],
        responses={200: dict, 400: dict, 503: dict},
    )
    def get(self, request):
        uf = request.query_params.get('uf', '').strip().upper()

        # 400 Bad Request: o erro é de quem fez a requisição
        if not uf:
            return Response(
                {'erro': 'Informe a sigla do estado no parâmetro "uf". Ex.: /api/municipios/?uf=PE'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if uf not in UFS_VALIDAS:
            return Response(
                {'erro': f'UF inválida: "{uf}". Use uma sigla de estado brasileiro, como PE, SP ou RJ.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            municipios = listar_municipios(uf)
        except IBGEIndisponivel:
            # 503 Service Unavailable: o problema não é do cliente, é de um serviço
            # que dependemos e que está fora do ar ou lento.
            return Response(
                {'erro': 'O serviço do IBGE está indisponível ou demorou demais para responder. Tente novamente em alguns minutos.'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        return Response({'uf': uf, 'total': len(municipios), 'municipios': municipios})
