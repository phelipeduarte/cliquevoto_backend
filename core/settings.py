"""
Django settings for core project.
"""

from pathlib import Path
import os
from dotenv import load_dotenv # NOVO: Carrega variáveis secretas

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Carrega o arquivo .env (onde ficam as senhas de verdade)
load_dotenv(BASE_DIR / '.env')

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-chave-padrao-local')

# SECURITY WARNING: don't run with debug turned on in production!
# Se no .env estiver DEBUG=True, ele fica True. Caso contrário, assume False (Segurança).
DEBUG = os.getenv('DEBUG', 'True') == 'True'

# Lê os domínios permitidos do .env. Na AWS, não podemos usar '*'
allowed_hosts_env = os.getenv('ALLOWED_HOSTS', '127.0.0.1,localhost,*')
ALLOWED_HOSTS = allowed_hosts_env.split(',')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Ferramentas
    'corsheaders',
    # Nosso App Principal
    'votacao',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware', 
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://192.168.18.129:5173",
    "https://cliquevoto-saas.vercel.app",
    "https://cliquevoto.com.br",
    "https://www.cliquevoto.com.br",
]

CSRF_TRUSTED_ORIGINS = [
    "http://192.168.18.129:5173",
    "http://192.168.18.129:8000",
    "https://cliquevoto-saas.vercel.app",
    "https://api.cliquevoto.com.br",
    "https://cliquevoto.com.br",
    "https://www.cliquevoto.com.br",
]

ROOT_URLCONF = 'core.urls'

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

WSGI_APPLICATION = 'core.wsgi.application'

# TRUQUE DE ARQUITETURA: Separação por Ambiente (DEBUG)
if DEBUG: 
    # Ambiente Local: usa o banco local SQLite
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    # Produção (AWS): usa o banco PostgreSQL, lendo as credenciais do .env
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('DB_NAME'),
            'USER': os.getenv('DB_USER'),
            'PASSWORD': os.getenv('DB_PASSWORD'),
            'HOST': os.getenv('DB_HOST'), 
            'PORT': os.getenv('DB_PORT', '5432'),
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
# NOVO: Pasta onde a AWS vai compilar os arquivos CSS do painel de Admin
STATIC_ROOT = BASE_DIR / 'staticfiles' 

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
CORS_ALLOW_ALL_ORIGINS = True