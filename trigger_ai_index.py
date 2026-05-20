import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from storage.models import File
from storage.tasks import process_file_and_index

def run_ai_indexing():
    files = File.objects.all()
    print(f"Memulai pemrosesan AI untuk {files.count()} file...")
    
    for f in files:
        print(f"Memproses: {f.name} (ID: {f.id})...")
        try:
            # Panggil task secara sinkron untuk pengujian/inisialisasi
            result = process_file_and_index(str(f.id))
            print(f"Hasil: {result}")
        except Exception as e:
            print(f"Gagal memproses {f.name}: {e}")

if __name__ == "__main__":
    run_ai_indexing()
