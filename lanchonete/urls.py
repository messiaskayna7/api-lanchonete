"""URLs principais do projeto: é aqui que o Django decide para onde vai cada requisição."""
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    # Painel administrativo
    path('admin/', admin.site.urls),
    # Todas as rotas da API ficam sob o prefixo /api/ (ver cardapio/urls.py)
    path('api/', include('cardapio.urls')),
    # POST com {"username": "...", "password": "..."} devolve {"token": "..."}
    path('api/token/', obtain_auth_token, name='api-token'),
    # Login/logout na interface navegável da DRF
    path('api-auth/', include('rest_framework.urls')),
    # Documentação automática (drf-spectacular)
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
