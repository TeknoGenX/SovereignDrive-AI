
import uuid
from django.test import TestCase
from django.contrib.auth.models import User
from storage.models import File, UserProfile
from django.core.files.uploadedfile import SimpleUploadedFile

class BugReproductionTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        # UserProfile should be created by signal
        self.profile = self.user.profile

    def test_quota_tracking_leak(self):
        """Reproduce the bug where storage_used leaks when a file is trashed then deleted."""
        file_size = 1000
        
        # 1. Create file (Quota increases)
        file_obj = File.objects.create(
            name="test.txt",
            owner=self.user,
            size=file_size,
            is_trashed=False
        )
        
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.storage_used, file_size)

        # 2. Move to trash
        file_obj.is_trashed = True
        file_obj.save()
        
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.storage_used, 0, "Quota should be 0 after moving to trash")

        # 3. Hard delete while in trash
        file_obj.delete()
        
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.storage_used, 0, "Quota should stay 0 after hard delete")

    def test_download_pdf_http_response_bug(self):
        """Reproduce the bug where download_file returns a BytesIO object in HttpResponse."""
        from django.test import Client
        from django.urls import reverse
        
        # Minimal valid PDF
        pdf_content = (
            b"%PDF-1.4\n"
            b"1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n"
            b"2 0 obj << /Type /Pages /Count 1 /Kids [ 3 0 R ] >> endobj\n"
            b"3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [ 0 0 612 792 ] /Resources << >> >> endobj\n"
            b"xref\n0 4\n0000000000 65535 f\n0000000009 00000 n\n0000000056 00000 n\n0000000111 00000 n\n"
            b"trailer << /Size 4 /Root 1 0 R >>\n"
            b"startxref\n190\n%%EOF"
        )
        uploaded_file = SimpleUploadedFile("test.pdf", pdf_content)
        file_obj = File.objects.create(
            name="test.pdf",
            owner=self.user,
            file=uploaded_file,
            size=len(pdf_content),
            is_trashed=False
        )
        
        client = Client()
        client.force_login(self.user)
        
        try:
            response = client.get(reverse('storage:download_file', args=[file_obj.id]))
            
            if response.status_code != 200:
                print(f"DEBUG: Response content: {getattr(response, 'content', 'No content attribute')}")
            
            self.assertEqual(response.status_code, 200)
            
            # FileResponse uses streaming_content
            if hasattr(response, 'streaming_content'):
                content = b"".join(response.streaming_content)
            else:
                content = response.content

            print(f"DEBUG: Response content start: {content[:100]}")
            self.assertIn(b"%PDF", content, "Response should contain PDF data")
        except Exception as e:
            self.fail(f"PDF download failed with error: {e}")
