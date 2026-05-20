"""
Django settings for core project (Aplikasi Awan).
"""

import os
import hashlib
import subprocess
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-g$3ia0ohwoo0(u+#hvd1=s#&k)okt$77%=++x!$*34v0@nj@!5'

# ==========================================
# 🔐 ENCRYPTION KEY (AES-256 HASHING)
# ==========================================
raw_key = os.environ.get('AES_MASTER_KEY', 'Rahasiacore256bitkunciku!!!').encode('utf-8')
AES_MASTER_KEY = hashlib.sha256(raw_key).digest() # Pasti 32-byte (256-bit)
ENCRYPTION_KEY = SECRET_KEY 

# ==========================================
# 🌐 KEAMANAN & DOMAIN
# ==========================================
DEBUG = True 

ALLOWED_HOSTS = ['*'] # Izinkan semua domain (Localhost, IP, Tunnel) sementara

# Agar form dan webhook via Tunnel publik tidak terkena blokir CSRF
CSRF_TRUSTED_ORIGINS = [
    'http://minicloud.com', 
    'https://minicloud.com', 
    'http://127.0.0.1',
    'http://localhost',
    'http://100.92.144.96',
    'https://100.92.144.96',
    'https://*.pinggy.link', 
    'https://*.loca.lt',
    'https://*.lhr.life'
]

# ==========================================
# ⚙️ DOCKER UTILS (Helper for IP discovery)
# ==========================================
def get_docker_ip(container_name, default='127.0.0.1'):
    try:
        result = subprocess.run(
            ['docker', 'inspect', '-f', '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}', container_name],
            capture_output=True, text=True, check=True
        )
        ip = result.stdout.strip()
        return ip if ip else default
    except Exception:
        return default

REDIS_HOST = os.environ.get('REDIS_HOST', get_docker_ip('private-cloud-redis-1'))
DB_HOST = os.environ.get('DB_HOST', get_docker_ip('private-cloud-db-1'))
ES_HOST = os.environ.get('ES_HOST', get_docker_ip('private-cloud-elasticsearch-1', 'localhost'))

# ==========================================
# 📦 INSTALLED APPS
# ==========================================
INSTALLED_APPS = [
    'daphne', # Daphne harus di atas admin agar ASGI server berjalan di dev
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # --- Pihak Ketiga ---
    'rest_framework',
    'rest_framework_simplejwt',
    'django_elasticsearch_dsl',
    'channels',
    
    # --- Aplikasi Kita ---
    'storage.apps.StorageConfig', 
]

ASGI_APPLICATION = 'core.asgi.application'

# ==========================================
# ⚡ CHANNEL LAYERS (REDIS)
# ==========================================
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [(REDIS_HOST, 6379)],
        },
    },
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # WhiteNoise untuk produksi
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'storage' / 'templates'], 
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

# ==========================================
# 🗄️ DATABASE
# ==========================================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'cloud_db'),
        'USER': os.environ.get('DB_USER', 'cloud_user'),
        'PASSWORD': os.environ.get('DB_PASSWORD', '@Sukaslamet123'),
        'HOST': DB_HOST,
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'id-ID' 
TIME_ZONE = 'Asia/Jakarta' 
USE_I18N = True
USE_TZ = True

# ==========================================
# 📁 STATIC & MEDIA FILES
# ==========================================
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / "storage" / "static"]

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ==========================================
# 🔍 ELASTICSEARCH SETTINGS
# ==========================================
ELASTICSEARCH_DSL = {
    'default': {
        'hosts': f'http://{ES_HOST}:9200'
    },
}
ELASTICSEARCH_DSL_AUTOSYNC = False
ELASTICSEARCH_DSL_SIGNAL_PROCESSOR = 'django_elasticsearch_dsl.signals.BaseSignalProcessor'

# ==========================================
# ⚙️ CELERY SETTINGS
# ==========================================
CELERY_BROKER_URL = f'redis://{REDIS_HOST}:6379/0'
CELERY_RESULT_BACKEND = f'redis://{REDIS_HOST}:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

# ==========================================
# 🤖 TELEGRAM BOT SETTINGS
# ==========================================
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', 'YOUR_REAL_BOT_TOKEN_HERE')
TELEGRAM_API_URL = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}'

# ==========================================
# 🔐 AUTHENTICATION SETTINGS
# ==========================================
LOGIN_REDIRECT_URL = 'storage:dashboard'
LOGOUT_REDIRECT_URL = 'storage:landing'
