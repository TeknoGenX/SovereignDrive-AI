# /home/andi-liani/code/awan/storage/views/view_file.py

import mimetypes
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.http import HttpResponseForbidden, Http404, StreamingHttpResponse

from storage.models import File, FileAccessLog
from .get_file_access_role import get_file_access_role
from storage.services.encryption import decrypt_stream

@login_required
def view_file(request, file_id):
    """
    Preview file di browser (inline) secara streaming + dekripsi + access control.
    Mencegah RAM server penuh (OOM) dengan tidak membaca seluruh file sekaligus.
    """
    # =========================
    # 1. AMBIL FILE & CEK AKSES
    # =========================
    file_obj = get_object_or_404(File, id=file_id, is_trashed=False)

    if not get_file_access_role(file_obj, request.user):
        return HttpResponseForbidden("Akses Ditolak.")

    # =========================
    # 2. LOG AKSES
    # =========================
    FileAccessLog.objects.create(user=request.user, file=file_obj)

    # =========================
    # 3. DETEKSI MIME TYPE
    # =========================
    content_type, _ = mimetypes.guess_type(file_obj.name)
    if not content_type:
        content_type = 'application/octet-stream'

    # =========================
    # 4. STREAMING RESPONSE
    # =========================
    try:
        file_obj.file.seek(0)
        
        # Menggunakan StreamingHttpResponse agar file dikirim per chunk (64KB)
        response = StreamingHttpResponse(
            decrypt_stream(file_obj.file), 
            content_type=content_type
        )
    except Exception as e:
        raise Http404(f"Gagal memproses stream file: {str(e)}")

    # 🔥 KUNCI UTAMA AGAR TAMPIL DI BROWSER (INLINE)
    response['Content-Disposition'] = f'inline; filename="{file_obj.name}"'

    # 🔒 Security & Performance Headers
    response['X-Content-Type-Options'] = 'nosniff'
    response['Cache-Control'] = 'no-store'
    if file_obj.size:
        response['Content-Length'] = file_obj.size

    return response