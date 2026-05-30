
import os
import tempfile
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from storage.models import File
from django.core.files.uploadedfile import SimpleUploadedFile

class DiskLeakFixTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        
        # Minimal valid PDF
        self.pdf_content = (
            b"%PDF-1.4\n"
            b"1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n"
            b"2 0 obj << /Type /Pages /Count 1 /Kids [ 3 0 R ] >> endobj\n"
            b"3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [ 0 0 612 792 ] /Resources << >> >> endobj\n"
            b"xref\n0 4\n0000000000 65535 f\n0000000009 00000 n\n0000000056 00000 n\n0000000111 00000 n\n"
            b"trailer << /Size 4 /Root 1 0 R >>\n"
            b"startxref\n190\n%%EOF"
        )
        self.uploaded_file = SimpleUploadedFile("test.pdf", self.pdf_content)
        self.file_obj = File.objects.create(
            name="test.pdf",
            owner=self.user,
            file=self.uploaded_file,
            size=len(self.pdf_content),
            is_trashed=False
        )

    def test_pdf_download_cleanup(self):
        """Verify that temporary files are deleted after PDF download."""
        client = Client()
        client.force_login(self.user)
        
        # We need to monkeypatch tempfile.NamedTemporaryFile to capture the paths
        # OR we can just check the /tmp directory before and after if we knew the prefix/suffix.
        # But download_file uses suffix=".pdf".
        
        # A better way is to track all files created in /tmp during the request
        import glob
        tmp_files_before = set(glob.glob(os.path.join(tempfile.gettempdir(), "*.pdf")))
        
        response = client.get(reverse('storage:download_file', args=[self.file_obj.id]))
        self.assertEqual(response.status_code, 200)
        
        # Close the response to trigger cleanup
        response.close()
        
        tmp_files_after = set(glob.glob(os.path.join(tempfile.gettempdir(), "*.pdf")))
        
        # New files might have been created by other processes, but our files should NOT be there
        new_files = tmp_files_after - tmp_files_before
        
        # If our cleanup works, there should be no leaked PDF files from this request.
        # Note: some files might stay if they were created but NOT deleted by our code.
        # But we want to ensure OUR files are gone.
        
        # Since we don't know the exact names, let's look for files that might have been leaked.
        # This is a bit flaky if other things are happening, but in a test environment it should be stable.
        self.assertEqual(len(new_files), 0, f"Leaked PDF files found: {new_files}")
