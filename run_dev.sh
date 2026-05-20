#!/bin/bash

# Aktifkan virtual environment
# Pastikan path ini sesuai dengan lokasi venv di mesin kamu
source /home/andi-liani/virtual/venv/bin/activate

# Masuk ke project Django
cd /home/andi-liani/code/python_django/awan1

echo "🚀 Memulai Infrastruktur Mesin (Docker)..."

# Jalankan Infrastruktur Utama
# Kita hanya menjalankan service pendukung, sementara App berjalan di host lokal
docker start private-cloud-db-1 private-cloud-redis-1 private-cloud-elasticsearch-1

# Hentikan container aplikasi jika sedang berjalan agar tidak bentrok port
docker stop private-cloud-web-1 private-cloud-celery-1 > /dev/null 2>&1

echo "✅ Database, Redis, dan Elasticsearch AKTIF."

# Jalankan Celery Worker
echo "✅ Menjalankan Celery Worker (Background)..."
# Membersihkan worker lama jika masih menggantung
pkill -f "celery worker" > /dev/null 2>&1
# Menjalankan worker di background dan membuang log ke file
celery -A core worker --loglevel=info > celery.log 2>&1 &
echo "   (Log Celery: celery.log)"

# Jalankan Django Development Server
echo "✅ Menjalankan Django Development Server..."
# Menggunakan 0.0.0.0 agar bisa diakses dari jaringan lokal atau tunnel
python manage.py runserver 0.0.0.0:8000
