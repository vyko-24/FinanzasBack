"""
Django settings for backInte project.

Generated by 'django-admin startproject' using Django 5.1.5.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

import pymysql
pymysql.install_as_MySQLdb()

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-&w7l*p-5rd72r81w^)q56^ugr!7!ic5j(jfecv$xv0qv15e6kk'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'finanzas',
    'corsheaders',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
]

CORS_ALLOW_ALL_ORIGINS = True

"""CORS_ALLOWED_ORIGINS = [
    # IPs de las cuales tengo confianza
    "http://127.0.0.1:5173/",
    "http://localhost:5173",
    "http://127.0.0.1:8000/",
    "http://127.0.0.1:8000",
]"""

ROOT_URLCONF = 'backInte.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'backInte.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases
# mysql://root::/railway

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'railway',
        'USER':'root',
        'PASSWORD':'stfpqVrNQTdMuOONUSyxqPmbogrPRYlX',
        'HOST':'switchback.proxy.rlwy.net',
        'PORT':'18290',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL = 'finanzas.CustomUser'
LOGIN_URL = '/users/login/'

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES":(
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}

from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=7),  # Duración del access token
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),  # Duración del refresh token (opcional)
    'ROTATE_REFRESH_TOKENS': False,  # Si deseas rotar los refresh tokens
    'BLACKLIST_AFTER_ROTATION': False,  # Si deseas poner en lista negra los refresh tokens rotados
    # Otros parámetros que puedas necesitar configurar
}

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
#Configuración para Gmail
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
# Usar su correo de UTEZ
EMAIL_HOST_USER = "20223tn008@utez.edu.mx"
# Obtener de https://myaccount.google.com/apppasswords
EMAIL_HOST_PASSWORD = "akwe hkcq kief fgim"