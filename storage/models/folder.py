# /home/andi-liani/code/awan/storage/models/folder.py

import uuid
from django.db import models
from django.contrib.auth.models import User

class Folder(models.Model):
    """
    Model untuk menyimpan informasi folder.
    Mendukung hirarki folder bersarang (nested folders) menggunakan field 'parent'.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)

    # 'self' memungkinkan folder ini berada di dalam folder lain (sub-folder)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subfolders'
    )

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='folders')

    size = models.BigIntegerField(default=0)
    is_trashed = models.BooleanField(default=False)
    is_public = models.BooleanField(default=False)

    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('name', 'parent', 'owner')
        ordering = ['name']

    def __str__(self):
        return self.name
    