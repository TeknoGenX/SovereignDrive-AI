# /home/andi-liani/code/awan/storage/models/profile.py

from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    """
    Model ekstensi untuk User bawaan Django.
    Menyimpan informasi kuota penyimpanan dan foto profil (avatar).
    """
    # OneToOneField memastikan 1 User hanya memiliki 1 Profil
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')

    # Default kuota 15 GB (dalam ukuran Bytes)
    storage_limit = models.BigIntegerField(default=15 * 1024 * 1024 * 1024)  
    storage_used = models.BigIntegerField(default=0)

    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    def __str__(self):
        return f"Profil: {self.user.username}"