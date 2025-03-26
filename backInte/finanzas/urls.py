from django.urls import path, include 
from rest_framework.routers import SimpleRouter
from .views import *
from rest_framework_simplejwt.views import TokenRefreshView

router = SimpleRouter()
router.register(r'usuarios', UserViewSet, basename='usuarios')
router.register(r'cuentas', CuentaViewSet, basename='cuentas')
router.register(r'gastos', GastoViewSet, basename='gastos')

urlpatterns = [
    path('',include(router.urls)),
    path('token/', CustomTokenObtainPairView.as_view(), name='obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='refresh_token'),
    
]