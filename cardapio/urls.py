from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import AreaEntregaViewSet, CategoriaViewSet, MunicipiosView, ProdutoViewSet

# O Router olha os ViewSets e cria as URLs sozinho. Para "produtos", por exemplo:
#   /produtos/        -> GET (listar) e POST (criar)
#   /produtos/{id}/   -> GET (detalhar), PUT/PATCH (editar) e DELETE (excluir)
# O DefaultRouter ainda cria a página raiz (/api/) com links para tudo.
router = DefaultRouter()
router.register('categorias', CategoriaViewSet)
router.register('produtos', ProdutoViewSet)
router.register('areas-entrega', AreaEntregaViewSet)

urlpatterns = [
    # APIView não usa router, então registramos a rota manualmente
    path('municipios/', MunicipiosView.as_view(), name='municipios'),
    path('', include(router.urls)),
]
