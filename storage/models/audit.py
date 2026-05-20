from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
import uuid

class AuditLog(models.Model):
    """
    Sistem Jejak Audit (Enterprise).
    Mencatat setiap tindakan penting yang terjadi dalam sistem menggunakan GenericForeignKey.
    """
    ACTION_CHOICES = (
        ('upload', 'Upload File'),
        ('download', 'Download File'),
        ('delete', 'Hapus File'),
        ('share', 'Berbagi Link'),
        ('view', 'Lihat File'),
        ('approval', 'Review Approval'),
        ('edit', 'Edit File'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='audit_logs')
    
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    
    # Generic Foreign Key setup
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.CharField(max_length=255, null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    description = models.TextField()
    
    # Keamanan & Lokasi
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
        ]

    def __str__(self):
        return f"{self.user} - {self.action} - {self.created_at}"

    @property
    def target_id(self):
        return str(self.object_id) if self.object_id else None

    @property
    def target_type(self):
        return self.content_type.model if self.content_type else None
