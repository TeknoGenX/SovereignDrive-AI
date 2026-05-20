MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # --- TAMBAHAN PENTING UNTUK PRODUKSI (DOCKER) ---
    'whitenoise.middleware.WhiteNoiseMiddleware',
    
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

CSRF_TRUSTED_ORIGINS = ['http://minicloud.com', 'https://minicloud.com', '100.92.144.96']
CSRF_TRUSTED_ORIGINS = [
    'http://minicloud.com', 
    'https://minicloud.com', 
    'http://100.92.144.96',   # Tambahkan http:// di sini
    'https://100.92.144.96'   # Opsional: tambahkan https:// untuk berjaga-jaga
]
import os 

# Kunci rahasia 32-byte untuk AES-256...
AES_MASTER_KEY = os.environ.get('AES_MASTER_KEY', 'Rahasiacore256bitkunciku!!!').encode('utf-8')

import os
import hashlib # Tambahkan library ini untuk teknik Hashing

# Ambil kunci dari .env atau gunakan fallback
raw_key = os.environ.get('AES_MASTER_KEY', 'Rahasiacore256bitkunciku!!!').encode('utf-8')

# Gunakan SHA-256 untuk mengubah password apapun menjadi kunci yang ukurannya
# PASTI TEPAT 32-byte (256-bit). Mesin AES tidak akan pernah crash lagi!
AES_MASTER_KEY = hashlib.sha256(raw_key).digest()

# Di dalam settings.py
ALLOWED_HOSTS = ['*']

# Pastikan juga CSRF exempt untuk URL webhook bekerja
CSRF_TRUSTED_ORIGINS = ['https://*.loca.lt']

ALLOWED_HOSTS = ['*']
CSRF_TRUSTED_ORIGINS = ['https://*.loca.lt', 'https://*.lhr.life']

ALLOWED_HOSTS = ['*']
CSRF_TRUSTED_ORIGINS = ['https://*.loca.lt', 'https://*.lhr.life']

ALLOWED_HOSTS = ['*']
CSRF_TRUSTED_ORIGINS = ['https://*.pinggy.link', 'https://*.loca.lt']

# Tambahkan '*' di bagian paling belakang agar semua URL public tunnel diizinkan
ALLOWED_HOSTS = ['minicloud.com', 'www.minicloud.com', 'localhost', '127.0.0.1', '100.92.144.96', '.ts.net', '*'] 

CSRF_TRUSTED_ORIGINS = [
    'http://minicloud.com', 
    'https://minicloud.com', 
    'http://100.92.144.96',
    'https://100.92.144.96',
    # --- Tambahan untuk Tunneling Publik Hackathon ---
    'https://*.pinggy.link', 
    'https://*.loca.lt',
    'https://*.lhr.life'
]

# DI DALAM settings.py

# Gunakan '*' agar Django menerima SEMUA domain tunnel yang berubah-ubah
ALLOWED_HOSTS = ['*'] 

# Tambahkan juga ini agar Telegram tidak terkena blokir CSRF
CSRF_TRUSTED_ORIGINS = [
    'https://*.pinggy.link',
    'https://*.loca.lt',
    'https://minicloud.com',
    'http://127.0.0.1',
    'http://localhost',
]

ELASTICSEARCH_DSL = {
    'default': {
        'hosts': 'elasticsearch:9200' # <--- INI BIANG KEROKNYA
    },
}
ELASTICSEARCH_DSL = {
    'default': {
        'hosts': 'localhost:9200'
    },
}
ELASTICSEARCH_DSL = {
    'default': {
        'hosts': 'elasticsearch:9200' # <--- Kembalikan ke 'elasticsearch'
    },
}
ELASTICSEARCH_DSL = {
    'default': {
        'hosts': 'http://elasticsearch:9200'
    },
}

# settings.py

# ... konfigurasi lain ...

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles') # Penting untuk Docker

# KUNCI: Konfigurasi MEDIA
MEDIA_URL = '/media/'
# Di Docker, BASE_DIR biasanya '/app'. Pastikan folder 'media' ada di sana.
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')