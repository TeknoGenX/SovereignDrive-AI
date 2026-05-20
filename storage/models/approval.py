from django.db import models
from django.contrib.auth.models import User
from .file import File
import uuid

class ApprovalRequest(models.Model):
    """
    Sistem Workflow Approval (Enterprise).
    File yang baru diunggah perlu disetujui sebelum bisa diakses publik atau tim.
    """
    STATUS_CHOICES = (
        ('pending', 'Menunggu Persetujuan'),
        ('approved', 'Disetujui'),
        ('rejected', 'Ditolak'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file = models.OneToOneField(File, on_delete=models.CASCADE, related_name='approval')
    
    requester = models.ForeignKey(User, on_delete=models.CASCADE, related_name='approval_requests')
    approver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approvals_to_review')
    
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    note = models.TextField(blank=True, null=True, help_text="Catatan dari penyetuju")
    
    requested_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Approval: {self.file.name} [{self.status}]"
