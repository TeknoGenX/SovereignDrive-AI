# /home/andi-liani/code/awan/storage/models/file.py

import uuid
from django.db import models
from django.contrib.auth.models import User
from storage.utils.paths import user_directory_path
from .mixins import ThumbnailMixin
from .folder import Folder

class File(models.Model, ThumbnailMixin):
    """
    Model utama untuk menyimpan informasi file milik pengguna.
    Menggunakan UUID sebagai Primary Key untuk keamanan ekstra.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.CharField(max_length=255)
    file = models.FileField(upload_to=user_directory_path)
    thumbnail = models.ImageField(upload_to='thumbnails/', null=True, blank=True)

    folder = models.ForeignKey(
        Folder,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='files'
    )

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='my_files')

    size = models.BigIntegerField(default=0)
    is_trashed = models.BooleanField(default=False, db_index=True)
    is_public = models.BooleanField(default=False, db_index=True)

    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True)

    # Field Baru: Menyimpan hasil ekstraksi & preprocessing AI
    extracted_text = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # 1. Rekam ukuran file jika belum ada
        if self.file and not self.size:
            try:
                self.size = self.file.size
            except Exception:
                pass

        # Pemanggilan save berlebih dan blocking generate_thumbnail()
        # telah dihapus untuk performa maksimal. Thumbnail kini dibuat via Celery.
        super().save(*args, **kwargs)


class FileChunk(models.Model):
    """
    Menyimpan sementara potongan file (chunk) sebelum digabungkan.
    """
    upload_id = models.UUIDField(default=uuid.uuid4, unique=True, db_index=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    filename = models.CharField(max_length=255)
    total_chunks = models.IntegerField()
    received_chunks = models.IntegerField(default=0)
    total_size = models.BigIntegerField()
    folder = models.ForeignKey(Folder, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def get_chunk_path(self, chunk_index):
        import os
        from django.conf import settings
        directory = os.path.join(settings.MEDIA_ROOT, 'chunks', str(self.upload_id))
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
        return os.path.join(directory, f'part_{chunk_index}')

    def __str__(self):
        return f"{self.filename} ({self.received_chunks}/{self.total_chunks})"

