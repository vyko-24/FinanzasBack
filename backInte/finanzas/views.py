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
        if self.request.method in ['POST','PUT','DELETE','GET']:
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

        from decimal import Decimal
         # Convertir monto a Decimal
        gasto_monto = Decimal(str(gasto_data.get('monto', 0)))
    # Resta el gasto del saldo de la cuenta
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
        nuevo_monto = Decimal(str(gasto_data.get('monto', monto_anterior)))

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





#Importaciones para enviar correo y recuperación de contraseña
import secrets
from django.core.mail import send_mail
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password

@csrf_exempt
def send_reset_email(request):
    if request.method == "POST":
        #LLega del request de React información del email del usuario que quiere restablecer la contraseña
        email = request.POST.get("email")
        #Busquemos al usuario porque puede ser que no exista en el sistema
        user = CustomUser.objects.filter(email=email).first()

        if user:
            # Generar un token aleatorio de 20 caracteres
            token = secrets.token_urlsafe(20)

            # Las siguientes 2 lineas guarda el token en la BD
            user.token = token
            user.save()

            # Queremos que desde el correo electronica exista un link que incluya el token para que desde gmail (u otro) el usuario pueda regresar al sistema
            # y cambie su conraseña (debemos revisar que el token sea igual al que esta la BD para ello)
            # Construir el enlace de recuperación, en este caso lo dejamos en localhost pero deberia cambiar en producción
            reset_link = f"http://localhost:5173/reset-password/{token}"

            #Envio de correo
            send_mail(
                subject="🔐 Recuperación de contraseña",
                message=f"Hola, usa este enlace para restablecer tu contraseña: {reset_link}",  # Texto plano (fallback)
                from_email="no-reply@errorpages.com",
                recipient_list=[email],
                fail_silently=False,
                html_message=f"""
                <html>
  <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px; margin: 0;">
    <div style="max-width: 600px; margin: auto; background-color: #ffffff; padding: 30px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
      
      <!-- Encabezado -->
      <div style="text-align: center; padding-bottom: 20px;">
        <h2 style="color: #0066cc; margin-bottom: 10px;">Recuperación de contraseña</h2>
      </div>
      
      <!-- Mensaje principal -->
      <div style="color: #555; font-size: 16px; line-height: 1.6;">
        <p>Hola,</p>
        <p>Has solicitado restablecer tu contraseña. Para continuar, haz clic en el siguiente botón:</p>
      </div>
      
      <!-- Botón de acción -->
      <div style="text-align: center; margin: 30px 0;">
        <a href="{reset_link}" 
           style="display: inline-block; padding: 12px 24px; background-color: #0066cc; color: #ffffff; 
                  text-decoration: none; font-weight: bold; border-radius: 5px; font-size: 16px;">
          Restablecer contraseña
        </a>
      </div>

      <!-- Enlace como texto plano -->
      <div style="color: #555; font-size: 14px;">
        <p>O copia y pega este enlace en tu navegador:</p>
        <p><a href="{reset_link}" style="color: #0066cc;">{reset_link}</a></p>
        <p>Si no solicitaste este cambio, puedes ignorar este mensaje con seguridad.</p>
      </div>
      
      <!-- Pie de página -->
      <div style="margin-top: 30px; font-size: 12px; color: #999; text-align: center;">
        <p>Este es un mensaje automático, por favor no respondas a este correo.</p>
        <p>© 2025 Camila. Todos los derechos reservados.</p>
      </div>
    </div>
  </body>
</html>
                """
            )
            #Regresamos mensaje de exito a React
            return JsonResponse({"message": "Correo de recuperación enviado."}, status=200)
        #Regresamos mensaje de error a React
        return JsonResponse({"error": "Usuario no encontrado"}, status=404)


#Vista que verificara que el token del usuario sea correcto y realiza el cambio de contraseña
@csrf_exempt
def reset_password(request):
    #Llega información desde el front con react
    if request.method == "POST":
        token = request.POST.get("token")
        new_password = request.POST.get("password")
        #Buscamos al usuario por token (ya que deberia ser unico y debe ser correcto, si no nos estan hackeando 0_0)
        user = CustomUser.objects.filter(token=token).first()

        if user:
            user.password = make_password(new_password)  # Encripta la nueva contraseña
            user.token = None  # Eliminar el token después de usarlo
            user.save()

            #Envio de correo
            send_mail(
                subject="🔐 Recuperación de contraseña",
                message=f"Tu contraseña fue cambiada con exito!",  # Texto plano (fallback)
                from_email="no-reply@errorpages.com",
                recipient_list=[user.email],
                fail_silently=False,
                html_message=f"""
                <html>
                <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px; margin: 0;">
                  <div style="max-width: 600px; margin: auto; background-color: #ffffff; padding: 30px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
                    
                    <!-- Encabezado -->
                    <div style="text-align: center; padding-bottom: 20px;">
                      <h2 style="color: #0066cc; margin-bottom: 10px;">Contraseña actualizada</h2>
                    </div>
                    
                    <!-- Mensaje principal -->
                    <div style="color: #555; font-size: 16px; line-height: 1.6;">
                      <p>Hola,</p>
                      <p>Tu contraseña ha sido cambiada con éxito. Si fuiste tú quien hizo este cambio, no se requiere ninguna otra acción.</p>
                      <p>Para volver a acceder al sistema, haz clic en el siguiente botón:</p>
                    </div>
                    
                    <!-- Botón de acción -->
                    <div style="text-align: center; margin: 30px 0;">
                      <a href="http://localhost:5173/login/" 
                         style="display: inline-block; padding: 12px 24px; background-color: #0066cc; color: #ffffff; 
                                text-decoration: none; font-weight: bold; border-radius: 5px; font-size: 16px;">
                        Iniciar sesión
                      </a>
                    </div>
        
                    <!-- Enlace como texto plano -->
                    <div style="color: #555; font-size: 14px;">
                      <p>O copia y pega este enlace en tu navegador:</p>
                      <p><a href="http://localhost:5173/login/" style="color: #0066cc;">http://localhost:5173/login/</a></p>
                      <p>Si tú no solicitaste este cambio, tu cuenta podría estar comprometida. Por favor contáctanos inmediatamente en <strong>admin@errorpages.com</strong>.</p>
                    </div>
                    
                    <!-- Pie de página -->
                    <div style="margin-top: 30px; font-size: 12px; color: #999; text-align: center;">
                      <p>Este es un mensaje automático, por favor no respondas a este correo.</p>
                      <p>© 2025 Camila. Todos los derechos reservados.</p>
                    </div>
                  </div>
                </body>
                </html>
                """
            )

            return JsonResponse({"message": "Contraseña restablecida exitosamente."})
        return JsonResponse({"error": "Token inválido"}, status=400)
