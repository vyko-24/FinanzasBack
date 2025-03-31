from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils.timezone import now

# Create your models here.

# Usuario: correo, contrasena, token, nombre_completo, edad
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password, name, surname, age, **extrafields):
        if not email:
            raise ValueError('El correo eectrónico es obligatorio')
        email = self.normalize_email(email)
        user = self.model(email=email, **extrafields)
        user.set_password(password)
        user.name = name
        user.surname = surname
        user.age = age
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    token = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    age = models.PositiveIntegerField()
    join_date = models.DateTimeField(default=now)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'surname', 'age']

    def __str__(self):
        return self.email

# Cuenta: Usuario, banco, is_favorita, saldo, fecha_ultimo_deposito
class Cuenta(models.Model):
    usuario = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True)
    banco = models.CharField(max_length=50)
    saldo = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_ultimo_deposito = models.DateField(auto_now=True)
    esFavorito = models.BooleanField(default=False)

    def __str__(self):
        return self.banco

#Gastos: Usuario, monto, fecha, descripcion, titulo
class Gasto(models.Model):
    usuario = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True)
    cuenta = models.ForeignKey(
        Cuenta,
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateField(default=now)
    descripcion = models.TextField(blank=True, null=True)
    titulo= models.CharField(max_length=50)
