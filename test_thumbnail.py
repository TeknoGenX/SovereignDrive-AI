import os
import django
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from storage.models import File
from storage.tasks import generate_thumbnail_task

def test_thumbnail_generation():
    # Cari file gambar atau PDF
    valid_exts = ('.png', '.jpg', '.jpeg', '.gif', '.webp', '.pdf')
    file_obj = None
    for f in File.objects.all():
        if f.name.lower().endswith(valid_exts):
            file_obj = f
            break
    
    if not file_obj:
        print("Tidak ada file Gambar atau PDF ditemukan di database.")
        return

    print(f"Menguji pembuatan thumbnail untuk file: {file_obj.name} (ID: {file_obj.id})")
    
    # Jalankan task secara sinkron (panggil fungsinya langsung, bukan .delay())
    result = generate_thumbnail_task(str(file_obj.id))
    print(f"Hasil Task: {result}")
    
    # Refresh dari DB
    file_obj.refresh_from_db()
    if file_obj.thumbnail:
        print(f"SUKSES! Thumbnail dibuat: {file_obj.thumbnail.path}")
        print(f"URL: {file_obj.thumbnail.url}")
    else:
        print("GAGAL! Thumbnail tetap kosong.")

if __name__ == "__main__":
    test_thumbnail_generation()
