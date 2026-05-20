# test_quota.py

import os
import django
from django.conf import settings

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth.models import User
from storage.models import File, UserProfile
from django.core.files.uploadedfile import SimpleUploadedFile

def test_quota_issue():
    # 1. Setup User
    user, _ = User.objects.get_or_create(username='testuser')
    profile, _ = UserProfile.objects.get_or_create(user=user)
    
    # Reset storage_used
    profile.storage_used = 0
    profile.save()
    
    print(f"Initial storage_used: {profile.storage_used}")

    # 2. Upload File
    file_content = b"hello world"
    file_size = len(file_content)
    test_file = File.objects.create(
        name='test_restore.txt',
        owner=user,
        file=SimpleUploadedFile('test_restore.txt', file_content),
        size=file_size
    )
    
    profile.refresh_from_db()
    print(f"After upload - storage_used: {profile.storage_used} (Expected: {file_size})")

    # 3. Move to Trash
    test_file.is_trashed = True
    test_file.save()
    
    profile.refresh_from_db()
    print(f"After move to trash - storage_used: {profile.storage_used} (Expected: 0)")

    # 4. Restore
    test_file.is_trashed = False
    test_file.save()
    
    profile.refresh_from_db()
    print(f"After restore - storage_used: {profile.storage_used} (Expected: {file_size})")

    # 5. Hard Delete from Active (Not from trash)
    test_file.delete()
    
    profile.refresh_from_db()
    print(f"After hard delete (active) - storage_used: {profile.storage_used} (Expected: 0)")

if __name__ == "__main__":
    test_quota_issue()
