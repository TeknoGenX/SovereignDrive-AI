import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from .file import File
from .folder import Folder
from django.contrib.auth.hashers import make_password, check_password

class SharedLink(models.Model):
    """
    Sistem Berbagi File/Folder SUPER (Link Sharing).
    Mendukung Password, Expiry Date, dan Roles.
    """
    ROLE_CHOICES = (
        ('viewer', 'Viewer'),
        ('editor', 'Editor'),
    )

    # Unik ID untuk URL sharing (awan.com/s/xyz-123)
    share_id = models.UUIDField(default=uuid.uuid4, unique=True, db_index=True)
    
    # Target (Bisa File atau Folder)
    file = models.ForeignKey(File, on_delete=models.CASCADE, null=True, blank=True, related_name='shared_links')
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE, null=True, blank=True, related_name='shared_links')
    
    # Pembuat Link
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # Keamanan & Kontrol
    password = models.CharField(max_length=255, null=True, blank=True, help_text="Hashed password for protection")
    expiry_date = models.DateTimeField(null=True, blank=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='viewer')
    
    # Statistik
    view_count = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        if not self.password:
            return True
        return check_password(raw_password, self.password)

    @property
    def is_expired(self):
        if self.expiry_date and timezone.now() > self.expiry_date:
            return True
        return False

    def __str__(self):
        target = self.file.name if self.file else self.folder.name
        return f"Share: {target} ({self.role})"
