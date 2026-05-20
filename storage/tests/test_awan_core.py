import uuid
from django.test import TestCase
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from storage.models import File, Folder, FileAccess, FolderAccess, AuditLog
from storage.selectors.access_selector import get_file_access_role
from storage.services.audit_service import log_action

class AwanCoreTest(TestCase):
    def setUp(self):
        # 1. Setup Users
        self.owner = User.objects.create_user(username='owner', password='password123')
        self.editor = User.objects.create_user(username='editor', password='password123')
        self.viewer = User.objects.create_user(username='viewer', password='password123')
        self.stranger = User.objects.create_user(username='stranger', password='password123')

        # 2. Setup Folder Hierarchy: Root -> Sub1 -> Sub2
        self.root_folder = Folder.objects.create(name="Root", owner=self.owner)
        self.sub1 = Folder.objects.create(name="Sub1", owner=self.owner, parent=self.root_folder)
        self.sub2 = Folder.objects.create(name="Sub2", owner=self.owner, parent=self.sub1)

        # 3. Setup File in Sub2
        self.file = File.objects.create(name="DeepFile.txt", owner=self.owner, folder=self.sub2)

    def test_access_inheritance(self):
        """Uji apakah izin folder induk diwariskan ke file di dalamnya."""
        # Berikan akses Editor pada 'Root' folder untuk si 'editor'
        FolderAccess.objects.create(folder=self.root_folder, user=self.editor, role='editor')
        
        # Cek apakah 'editor' punya akses editor ke file yang ada jauh di dalam (Sub2)
        role = get_file_access_role(self.file, self.editor)
        self.assertEqual(role, 'editor', "Editor harusnya mewarisi akses dari folder Root")

        # Berikan akses Viewer pada 'Sub1' untuk si 'viewer'
        FolderAccess.objects.create(folder=self.sub1, user=self.viewer, role='viewer')
        
        role = get_file_access_role(self.file, self.viewer)
        self.assertEqual(role, 'viewer', "Viewer harusnya mewarisi akses dari folder Sub1")

        # Stranger tidak boleh punya akses
        role = get_file_access_role(self.file, self.stranger)
        self.assertIsNone(role, "Stranger tidak boleh memiliki akses")

    def test_audit_log_polymorphic(self):
        """Uji apakah AuditLog baru (GenericForeignKey) bekerja dengan baik."""
        # 1. Log aksi pada File
        log_f = log_action(self.owner, 'upload', target_object=self.file, description="Upload via test")
        self.assertEqual(log_f.content_object, self.file)
        self.assertEqual(log_f.target_type, 'file')

        # 2. Log aksi pada Folder
        log_d = log_action(self.owner, 'edit', target_object=self.root_folder, description="Edit root folder")
        self.assertEqual(log_d.content_object, self.root_folder)
        self.assertEqual(log_d.target_id, str(self.root_folder.id))

        # 3. Verifikasi query balik dari AuditLog
        all_logs = AuditLog.objects.filter(user=self.owner)
        self.assertEqual(all_logs.count(), 2)
        
        # Cek apakah target_type property bekerja
        targets = [log.target_type for log in all_logs]
        self.assertIn('file', targets)
        self.assertIn('folder', targets)

    def test_direct_file_access(self):
        """Izin langsung pada file harus mengalahkan izin folder (jika ada)."""
        # Viewer punya akses Folder viewer
        FolderAccess.objects.create(folder=self.root_folder, user=self.viewer, role='viewer')
        
        # Tapi berikan akses Editor langsung pada file tersebut
        FileAccess.objects.create(file=self.file, user=self.viewer, role='editor')
        
        role = get_file_access_role(self.file, self.viewer)
        self.assertEqual(role, 'editor', "Direct File Access harus diprioritaskan")
