# storage/services/upload_service.py

import os
import tempfile
from django.db import transaction
from django.core.files.base import ContentFile
from storage.models import File, UserProfile
from .encryption import encrypt_stream

class EncryptedStreamWrapper(object):
    """
    Wrapper sederhana untuk mengubah generator encrypt_stream menjadi 
    objek yang bisa dibaca oleh Django FileField.
    """
    def __init__(self, stream_gen):
        self.gen = stream_gen
        self.buffer = b''

    def read(self, size=-1):
        try:
            while size == -1 or len(self.buffer) < size:
                self.buffer += next(self.gen)
        except StopIteration:
            pass
        
        if size == -1:
            res, self.buffer = self.buffer, b''
        else:
            res, self.buffer = self.buffer[:size], self.buffer[size:]
        return res

def upload_file(user, uploaded_file, target_folder=None):
    """
    Layanan untuk mengunggah file dengan enkripsi AES-256 GCM.
    Dioptimalkan untuk mengurangi Disk I/O ganda.
    """
    original_size = uploaded_file.size
    
    with transaction.atomic():
        # 1. Pessimistic Locking untuk Kuota
        profile, _ = UserProfile.objects.select_for_update().get_or_create(user=user)
        
        if profile.storage_used + original_size > profile.storage_limit:
            raise ValueError("Kuota penyimpanan penuh! Gagal mengunggah file.")

        # 2. TAHAP ENKRIPSI & SIMPAN
        # Kita gunakan ContentFile dengan wrapper generator agar Django 
        # melakukan streaming enkripsi langsung saat menulis ke media storage.
        uploaded_file.seek(0)
        encrypted_wrapper = EncryptedStreamWrapper(encrypt_stream(uploaded_file))
        
        new_file = File.objects.create(
            name=uploaded_file.name,
            owner=user,
            folder=target_folder,
            size=original_size,
            is_trashed=False
        )
        
        # Simpan file secara streaming (mengurangi 1x siklus write ke /tmp)
        new_file.file.save(
            uploaded_file.name,
            encrypted_wrapper,
            save=True
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
