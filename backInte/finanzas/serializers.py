from .models import *
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class CustomUserTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        #Agregar más atributos
        return token
    # Agrega los datos del usuario a la respuesta
    def validate(self, attrs):
        data = super().validate(attrs)

        # Obtiene el usuario autenticado
        user = self.user

        # Agrega datos del usuario a la respuesta
        data.update({
            'user': {
                'id': user.id,
                'email': user.email,
                'name': user.name,
                'surname': user.surname,
                'age': user.age,
                'is_active': user.is_active,
                'is_staff': user.is_staff,
                'join_date': user.join_date.strftime('%Y-%m-%d %H:%M:%S')  # Formato legible
            }
        })
        
        return data

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = '__all__'

class CuentaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cuenta
        fields = '__all__'

class GastoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gasto
        fields = '__all__'