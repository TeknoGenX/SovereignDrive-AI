# /home/andi-liani/code/awan/storage/models/logs.py

from django.db import models
from django.contrib.auth.models import User
from .file import File

class FileAccessLog(models.Model):
    """
    Mencatat jejak (log) kapan seorang pengguna membuka/mengunduh file.
    Berguna untuk fitur 'Recent Files' atau 'Suggested Files'.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='access_logs')
    file = models.ForeignKey(File, on_delete=models.CASCADE, related_name='access_logs')

    accessed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Menampilkan log terbaru di urutan teratas
        ordering = ['-accessed_at']

    def __str__(self):
        return f"{self.user.username} mengakses {self.file.name}"