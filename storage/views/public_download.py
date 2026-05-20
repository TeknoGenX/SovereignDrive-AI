import mimetypes
from django.http import Http404, StreamingHttpResponse
from django.shortcuts import get_object_or_404

from storage.models import File
from storage.services.encryption import decrypt_stream

# PERHATIKAN: Tidak ada @login_required di sini karena ini akses publik
def public_download(request, public_id):
    """
    Fungsi untuk mengunduh file melalui tautan publik tanpa perlu login.
    Mendukung unduhan file besar tanpa menguras RAM (Streaming AES-GCM).
    """
    file_obj = get_object_or_404(
        File,
        public_id=public_id,
        is_public=True,
        is_trashed=False
    )

    try:
        file_obj.file.seek(0)
        content_type = mimetypes.guess_type(file_obj.name)[0] or 'application/octet-stream'
        
        response = StreamingHttpResponse(
            decrypt_stream(file_obj.file),
            content_type=content_type
        )
        response['Content-Disposition'] = f'attachment; filename="{file_obj.name}"'
        if file_obj.size:
            response['Content-Length'] = file_obj.size
            
        return response
    except Exception as e:
        raise Http404(f"File tidak bisa dibaca: {str(e)}")