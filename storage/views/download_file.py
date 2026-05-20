import mimetypes
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.http import HttpResponseForbidden, StreamingHttpResponse

from storage.models import File
from .get_file_access_role import get_file_access_role
from storage.services.encryption import decrypt_stream

@login_required
def download_file(request, file_id):
    """
    Fungsi untuk mengunduh file secara aman.
    Melakukan dekripsi data streaming sebelum dikirim ke pengguna.
    """
    file_obj = get_object_or_404(File, id=file_id, is_trashed=False)

    # =========================
    # 1. CEK AKSES
    # =========================
    if not get_file_access_role(file_obj, request.user):
        return HttpResponseForbidden("Akses Ditolak.")

    # =========================
    # 2. BACA & DEKRIPSI FILE STREAMING
    # =========================
    try:
        file_obj.file.seek(0)
        content_type = mimetypes.guess_type(file_obj.name)[0] or 'application/octet-stream'
        
        # --- FITUR DLP (DATA LOSS PREVENTION) ---
        # Jika file adalah PDF, tambahkan watermark identitas pengunduh
        if file_obj.name.lower().endswith('.pdf'):
            from storage.services.dlp_service import add_pdf_watermark
            from django.http import HttpResponse
            
            # Kita perlu mengumpulkan stream ke memori untuk diproses PDF library
            decrypted_chunks = list(decrypt_stream(file_obj.file))
            watermarked_pdf = add_pdf_watermark(
                decrypted_chunks, 
                request.user.get_full_name() or request.user.username,
                request.user.email
            )
            
            response = HttpResponse(watermarked_pdf, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{file_obj.name}"'
            return response

        # Untuk file non-PDF, gunakan streaming standar
        response = StreamingHttpResponse(
            decrypt_stream(file_obj.file),
            content_type=content_type
        )
        response['Content-Disposition'] = f'attachment; filename="{file_obj.name}"'
        if file_obj.size:
            response['Content-Length'] = file_obj.size
            
        return response
    except Exception as e:
        return HttpResponseForbidden(f"Gagal membaca file: {str(e)}")