from django.db import models
from django.contrib.auth.models import User
from .file import File
import uuid

class FileVersion(models.Model):
    """
    Menyimpan riwayat versi file. 
    Setiap kali file diupdate, versi lama dipindahkan ke sini.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file_record = models.ForeignKey(File, on_delete=models.CASCADE, related_name='versions')
    
    # File fisik untuk versi ini
    file = models.FileField(upload_to='versions/')
    
    version_number = models.PositiveIntegerField()
    size = models.BigIntegerField()
    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Metadata opsional: apa yang berubah?
    comment = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-version_number']
        unique_together = ('file_record', 'version_number')

    def __str__(self):
        return f"{self.file_record.name} - v{self.version_number}"
