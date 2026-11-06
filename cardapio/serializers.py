from rest_framework import serializers

from .ibge import IBGEIndisponivel, municipio_existe
from .models import AreaEntrega, Categoria, Produto


# Serializer = "tradutor" entre objetos Python (models) e JSON.
# - Serializar:    Produto (objeto)  -> JSON  (resposta de um GET)
# - Desserializar: JSON -> Produto (objeto), com validação  (corpo de um POST/PUT)
# O ModelSerializer lê o model e cria os campos automaticamente.


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ['id', 'nome', 'descricao']


class ProdutoSerializer(serializers.ModelSerializer):
    # Campo extra, só de leitura: pega o nome através do relacionamento
    # (produto.categoria.nome). No envio (POST) basta mandar o id em "categoria".
    categoria_nome = serializers.CharField(source='categoria.nome', read_only=True)

    class Meta:
        model = Produto
        fields = ['id', 'nome', 'preco', 'disponivel', 'categoria', 'categoria_nome']

    # Métodos com o nome validate_<campo> são chamados automaticamente
    # pelo DRF quando chamamos serializer.is_valid().
    def validate_preco(self, valor):
        if valor < 0:
            # Gera resposta 400 com: {"preco": ["O preço não pode ser negativo."]}
            raise serializers.ValidationError('O preço não pode ser negativo.')
        return valor


class AreaEntregaSerializer(serializers.ModelSerializer):
    class Meta:
        model = AreaEntrega
        fields = ['id', 'municipio', 'codigo_ibge', 'taxa_entrega']

    def validate_taxa_entrega(self, valor):
        if valor < 0:
            raise serializers.ValidationError('A taxa de entrega não pode ser negativa.')
        return valor

    def validate_codigo_ibge(self, valor):
        # Extra C5: confere no IBGE se o código existe de verdade
        try:
            existe = municipio_existe(valor)
        except IBGEIndisponivel:
            raise serializers.ValidationError(
                'Não foi possível validar o código agora: o IBGE não respondeu. Tente mais tarde.'
            )
        if not existe:
            raise serializers.ValidationError(
                f'O código {valor} não corresponde a nenhum município do IBGE.'
            )
        return valor
