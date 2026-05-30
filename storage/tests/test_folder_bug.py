
from django.test import TestCase
from django.contrib.auth.models import User
from storage.models import Folder, File, UserProfile

class FolderRestoreBugTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.root = Folder.objects.create(name="Root", owner=self.user)
        self.sub = Folder.objects.create(name="Sub", owner=self.user, parent=self.root)
        self.file = File.objects.create(name="file.txt", owner=self.user, folder=self.sub, size=100)

    def test_recursive_restore_bug(self):
        from storage.views.delete_folder import mark_folder_as_trashed_bulk
        
        # 1. Delete root folder
        mark_folder_as_trashed_bulk(self.root, self.user)
        
        self.root.refresh_from_db()
        self.sub.refresh_from_db()
        self.file.refresh_from_db()
        
        self.assertTrue(self.root.is_trashed)
        self.assertTrue(self.sub.is_trashed)
        self.assertTrue(self.file.is_trashed)

        # 2. Restore root folder using the view
        from django.test import Client
        from django.urls import reverse
        client = Client()
        client.force_login(self.user)
        response = client.get(reverse('storage:restore_folder', args=[self.root.id]))
        self.assertEqual(response.status_code, 302)
            
        self.sub.refresh_from_db()
        self.file.refresh_from_db()
        
        # The bug: subfolder and its files are still trashed
        print(f"Sub trashed: {self.sub.is_trashed}")
        print(f"File trashed: {self.file.is_trashed}")
        
        self.assertFalse(self.sub.is_trashed, "Subfolder should be restored")
        self.assertFalse(self.file.is_trashed, "File in subfolder should be restored")
