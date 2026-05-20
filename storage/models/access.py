# /home/andi-liani/code/awan/storage/models/access.py

from django.db import models
from django.contrib.auth.models import User
from .file import File
from .folder import Folder

class FileAccess(models.Model):
    """
    Tabel perantara untuk mencatat siapa saja yang memiliki akses ke sebuah File
    beserta peran (role) mereka.
    """
    ROLE_CHOICES = (
        ('viewer', 'Viewer'),
        ('editor', 'Editor')
    )

    file = models.ForeignKey(File, on_delete=models.CASCADE, related_name='accesses')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='file_accesses')

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='viewer')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Mencegah 1 user diberikan akses berulang-ulang pada file yang sama
        unique_together = ('file', 'user')

class FolderAccess(models.Model):
    """
    Tabel perantara untuk mencatat siapa saja yang memiliki akses ke sebuah Folder.
    Jika user memiliki akses folder, ia otomatis memiliki akses ke isi di dalamnya.
    """
    ROLE_CHOICES = (
        ('viewer', 'Viewer'),
        ('editor', 'Editor')
    )

    folder = models.ForeignKey(Folder, on_delete=models.CASCADE, related_name='accesses')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='folder_accesses')

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='viewer')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('folder', 'user')