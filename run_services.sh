#!/bin/bash

# 1. Pastikan kita di direktori project
BASE_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$BASE_DIR"

echo "🚀 Memulai Infrastruktur AwanDrive X (Docker)..."

# 2. Jalankan Database, Redis, dan ES lewat docker-compose
if command -v docker-compose >/dev/null 2>&1; then
    docker-compose up -d
else
    docker compose up -d
fi

echo "✅ Infrastruktur AKTIF."

# 3. Jalankan Celery Worker (Background)
echo "✅ Menjalankan Celery Worker (Background)..."
pkill -f "celery worker" > /dev/null 2>&1
# Set host ke localhost agar worker bisa konek ke Redis di Docker
export REDIS_HOST=127.0.0.1
export DB_HOST=127.0.0.1
export ES_HOST=127.0.0.1

celery -A core worker --loglevel=info > celery.log 2>&1 &
echo "   (Log Celery tersedia di: celery.log)"

# 4. Jalankan Django Server
echo "✅ Menjalankan Django Development Server..."
# Gunakan daphne jika ingin mendukung WebSockets secara penuh
python3 manage.py runserver 0.0.0.0:8000
