from django.db import models
from django.contrib.auth.models import User
from .file import File
import uuid

class FileComment(models.Model):
    """
    Fitur Komentar & Mentions pada File.
    Mendukung threading (balasan komentar).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file = models.ForeignKey(File, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    
    # Isi Komentar
    content = models.TextField()
    
    # Pendukung Mentions (Bisa disimpan sebagai daftar ID user yang dimention)
    mentions = models.ManyToManyField(User, related_name='comment_mentions', blank=True)
    
    # Threading (Parent-Child)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.author.username}: {self.content[:30]}..."
