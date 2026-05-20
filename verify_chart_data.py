import os
import django

# 1. Setup Django environment agar script mengenali pengaturan project
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

# Import model dan fungsi selector setelah setup selesai
from django.contrib.auth.models import User
from storage.selectors.dashboard_selector import get_activity_chart_data

def verify_chart_data():
    # 2. Ambil user 'testuser' yang datanya sudah kita buat di script sebelumnya
    user = User.objects.get(username='testuser')
    
    # 3. Ambil data grafik menggunakan fungsi dari selector
    data = get_activity_chart_data(user)
    
    # 4. Tampilkan hasilnya ke terminal untuk memastikan formatnya sesuai
    print("=== Hasil Pengujian Data Grafik ===")
    print(f"Labels : {data['labels']}")
    print(f"Data   : {data['data']}")
    print(f"Total  : {data['total_count']}")
    print("===================================")

if __name__ == "__main__":
    verify_chart_data()
