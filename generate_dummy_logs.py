import os
import django
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import random

# 1. Setup Django environment agar script bisa mengenali model Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

# Import model setelah setup environment selesai
from django.contrib.auth.models import User
from storage.models import AuditLog

def generate_dummy_logs():
    # 2. Cari atau buat user untuk pengujian
    user = User.objects.filter(username='testuser').first()
    if not user:
        user = User.objects.create_user(username='testuser', password='password123')
        
    print(f"Generating dummy logs for {user.username}...")
        
    actions = ['upload', 'download', 'delete', 'view', 'share']
        
    # 3. Buat log untuk 7 hari terakhir
    for i in range(7):
        date = timezone.now() - timedelta(days=i)
        num_logs = random.randint(2, 10) # 2 hingga 10 log per hari
        
        for _ in range(num_logs):
            # Buat record awal
            log_entry = AuditLog.objects.create(
                user=user,
                action=random.choice(actions),
                description="Dummy activity for testing chart",
            )
            # 4. Timpa created_at secara manual karena auto_now_add=True mencegah input tanggal custom saat .create()
            AuditLog.objects.filter(id=log_entry.id).update(created_at=date)

    print("Successfully generated dummy logs.")

if __name__ == "__main__":
    generate_dummy_logs()
