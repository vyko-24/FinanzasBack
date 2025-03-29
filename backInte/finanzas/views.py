from django.shortcuts import render
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import *
from .serializers import *
from rest_framework import viewsets
from rest_framework.renderers import JSONRenderer

#Clase adicional para obtener el par de tokens
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomUserTokenObtainPairSerializer

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication 

#pa la peticion personalizada
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

# Create your views here.
class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    renderer_classes = [JSONRenderer]
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    
    def get_permissions(self):
        if self.request.method in ['POST','PUT','DELETE']:
            #retornar la funcion que checa si tenemos sesión
            return[IsAuthenticated()]
        #Da acceso al otro método
        return []

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomUserTokenObtainPairSerializer

class CuentaViewSet(viewsets.ModelViewSet):
    queryset = Cuenta.objects.all()
    serializer_class=CuentaSerializer
    renderer_classes=[JSONRenderer]
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'], url_path='mis-cuentas')
    def mis_cuentas_y_gastos(self, request):
        """Obtiene todas las cuentas del usuario autenticado"""
        user = request.user
        
        # Filtra las cuentas y gastos del usuario autenticado
        cuentas = Cuenta.objects.filter(usuario=user)

        # Serializa las cuentas y gastos
        cuenta_serializer = CuentaSerializer(cuentas, many=True)

        return Response({
            "cuentas": cuenta_serializer.data
        }, status=status.HTTP_200_OK)

class GastoViewSet(viewsets.ModelViewSet):
    queryset = Gasto.objects.all()
    serializer_class=GastoSerializer
    renderer_classes=[JSONRenderer]
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    
    @action(detail=False, methods=['get'], url_path='mis-gastos')
    def mis_cuentas_y_gastos(self, request):
        """Obtiene todas las cuentas del usuario autenticado"""
        user = request.user
        
        # Filtra las cuentas y gastos del usuario autenticado
        gastos = Gasto.objects.filter(cuenta__usuario=user)

        # Serializa las cuentas y gastos
        gasto_serializer = GastoSerializer(gastos, many=True)

        return Response({
            "gastos": gasto_serializer.data
        }, status=status.HTTP_200_OK)
    
    def create(self, request, *args, **kwargs):
        """Crea un gasto y actualiza la cuenta asociada"""
        gasto_data = request.data
        cuenta_id = gasto_data.get('cuenta')

        # Verifica que la cuenta exista
        try:
            cuenta = Cuenta.objects.get(id=cuenta_id, usuario=request.user)
        except Cuenta.DoesNotExist:
            return Response({"error": "Cuenta no encontrada"}, status=status.HTTP_404_NOT_FOUND)

        # Resta el gasto del saldo de la cuenta
        gasto_monto = float(gasto_data.get('monto', 0))
        cuenta.saldo -= gasto_monto
        cuenta.save()

        # Llama al método original para crear el gasto
        response = super().create(request, *args, **kwargs)

        # Retorna la respuesta con el gasto creado y el saldo actualizado
        return Response({
            "gasto": response.data,
            "nuevo_saldo": cuenta.saldo
        }, status=status.HTTP_201_CREATED)
    
    def update(self, request, *args, **kwargs):
        """Actualiza un gasto y ajusta el saldo de la cuenta"""
        gasto = self.get_object()
        cuenta_anterior = gasto.cuenta  # Guarda la cuenta original
        monto_anterior = gasto.monto  # Guarda el monto original

        gasto_data = request.data
        nueva_cuenta_id = gasto_data.get('cuenta', cuenta_anterior.id)
        nuevo_monto = float(gasto_data.get('monto', monto_anterior))

        try:
            nueva_cuenta = Cuenta.objects.get(id=nueva_cuenta_id, usuario=request.user)
        except Cuenta.DoesNotExist:
            return Response({"error": "Cuenta no encontrada"}, status=status.HTTP_404_NOT_FOUND)

        # Si la cuenta cambió, revertimos la cuenta anterior
        if cuenta_anterior != nueva_cuenta:
            cuenta_anterior.saldo += monto_anterior  # Revertir el saldo en la cuenta anterior
            cuenta_anterior.save()

            nueva_cuenta.saldo -= nuevo_monto  # Aplicar el nuevo gasto a la nueva cuenta
            nueva_cuenta.save()

        else:
            # Ajustamos el saldo si solo cambia el monto
            diferencia = nuevo_monto - monto_anterior
            nueva_cuenta.saldo -= diferencia
            nueva_cuenta.save()

        # Llama al método original para actualizar el gasto
        response = super().update(request, *args, **kwargs)

        return Response({
            "gasto": response.data,
            "nuevo_saldo": nueva_cuenta.saldo
        }, status=status.HTTP_200_OK)
