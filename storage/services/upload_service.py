# storage/services/upload_service.py

from django.db import transaction
from storage.models import File, UserProfile

def upload_file(user, uploaded_file, target_folder=None):
    """
    Layanan untuk mengunggah file dan menyimpannya ke database.
    Pembaruan kuota ditangani secara otomatis oleh signals (storage/signals.py).
    Trigger Celery tasks juga ditangani secara otomatis oleh signals.
    """
    with transaction.atomic():
        # 1. Pastikan profil pengguna ada
        profile, _ = UserProfile.objects.get_or_create(user=user)
        
        # 2. Cek kuota sebelum upload (Safety Layer)
        if profile.storage_used + uploaded_file.size > profile.storage_limit:
            raise Exception("Kuota penyimpanan penuh! Gagal mengunggah file.")
            
        # 3. Simpan file ke database
        # Post-save signal akan otomatis:
        # - Menambah profile.storage_used (kuota inkremental)
        # - Memicu Celery task (Thumbnail & AI Indexing) di storage/signals.py
        new_file = File.objects.create(
            name=uploaded_file.name,
            file=uploaded_file,
            owner=user,
            folder=target_folder,
            size=uploaded_file.size,
            is_trashed=False
        )
        
        return new_file

def delete_file_and_update_quota(user, file_obj):
    """
    Hapus file secara permanen.
    Signal post_delete akan otomatis mengembalikan kuota.
    """
    with transaction.atomic():
        file_obj.delete()
    return True
