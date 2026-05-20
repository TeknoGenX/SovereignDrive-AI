"""
Django settings for core project (Aplikasi Awan).
"""

import os
import hashlib
import subprocess
from pathlib import Path
from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-fallback-key')

# ==========================================
# 🔐 ENCRYPTION KEY (AES-256 HASHING)
# ==========================================
raw_key = config('AES_MASTER_KEY', default='fallback-encryption-key').encode('utf-8')
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
    'social_django',  # SSO / Social Auth
    
    # --- Aplikasi Kita ---
    'storage.apps.StorageConfig', 
]

AUTHENTICATION_BACKENDS = (
    'social_core.backends.google.GoogleOAuth2', # Contoh SSO Google
    'social_core.backends.azuread.AzureADOAuth2', # Contoh SSO Azure AD (Microsoft)
    'django.contrib.auth.backends.ModelBackend', # Login standar Django
)

# --- SSO / OAuth2 CONFIGURATION ---
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = os.environ.get('GOOGLE_KEY', '')
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = os.environ.get('GOOGLE_SECRET', '')

SOCIAL_AUTH_AZUREAD_OAUTH2_KEY = os.environ.get('AZURE_KEY', '')
SOCIAL_AUTH_AZUREAD_OAUTH2_SECRET = os.environ.get('AZURE_SECRET', '')

# Mapping field agar data dari SSO masuk ke model User kita
SOCIAL_AUTH_PIPELINE = (
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.auth_allowed',
    'social_core.pipeline.social_auth.social_user',
    'social_core.pipeline.user.get_username',
    'social_core.pipeline.user.create_user',
    'social_core.pipeline.social_auth.associate_user',
    'social_core.pipeline.social_auth.load_extra_data',
    'social_core.pipeline.user.user_details',
)

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
        'NAME': config('DB_NAME', default='cloud_db'),
        'USER': config('DB_USER', default='cloud_user'),
        'PASSWORD': config('DB_PASSWORD', default='@Sukaslamet123'),
        'HOST': config('DB_HOST', default=DB_HOST),
        'PORT': config('DB_PORT', default='5432'),
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
TELEGRAM_BOT_TOKEN = config('TELEGRAM_BOT_TOKEN', default='YOUR_REAL_BOT_TOKEN_HERE')
TELEGRAM_API_URL = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}'

# ==========================================
# 🔐 SOVEREIGN LICENSE GATEKEEPER
# ==========================================
# Proyek ini memerlukan License Key yang valid untuk dijalankan.
# Jika Anda mendapatkan kode ini dari GitHub, silakan hubungi:
# teknogenx@gmail.com untuk mendapatkan kunci akses.
SOVEREIGN_LICENSE_KEY = config('SOVEREIGN_LICENSE_KEY', default='')

if not SOVEREIGN_LICENSE_KEY:
    import sys
    print("\n" + "!"*60)
    print("ERROR: SOVEREIGN_LICENSE_KEY TIDAK DITEMUKAN!")
    print("SovereignDrive AI memerlukan lisensi untuk dijalankan.")
    print("Silakan hubungi teknogenx@gmail.com untuk meminta akses.")
    print("!"*60 + "\n")
    # sys.exit(1) # Uncomment ini di produksi untuk menghentikan server jika tanpa lisensi
LOGIN_REDIRECT_URL = 'storage:dashboard'
LOGOUT_REDIRECT_URL = 'storage:landing'
