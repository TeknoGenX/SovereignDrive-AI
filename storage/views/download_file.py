import mimetypes
import os
import tempfile
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.http import HttpResponseForbidden, StreamingHttpResponse, FileResponse

from storage.models import File
from storage.selectors.access_selector import get_file_access_role
from storage.services.encryption import decrypt_stream

from django.core.cache import cache
from storage.tasks import process_pdf_watermark_task

class CleanupFileResponse(FileResponse):
    """
    Kustom FileResponse yang menjamin penghapusan file sementara setelah dikirim.
    """
    def __init__(self, *args, **kwargs):
        self._cleanup_paths = kwargs.pop('cleanup_paths', [])
        super().__init__(*args, **kwargs)

    def close(self):
        super().close()
        for path in self._cleanup_paths:
            if os.path.exists(path):
                try:
                    os.remove(path)
                except Exception as e:
                    # Logging sederhana jika gagal menghapus
                    print(f"⚠️ Gagal menghapus file sementara {path}: {e}")

@login_required
def download_file(request, file_id):
    """
    Fungsi untuk mengunduh file secara aman.
    Melakukan dekripsi data streaming sebelum dikirim ke pengguna.
    Menggunakan Celery untuk PDF besar agar tidak memblokir server.
    """
    file_obj = get_object_or_404(File, id=file_id, is_trashed=False)

    # =========================
    # 1. CEK AKSES
    # =========================
    if not get_file_access_role(file_obj, request.user):
        return HttpResponseForbidden("Akses Ditolak.")

    # =========================
    # 2. STRATEGI DOWNLOAD (ASYNC vs SYNC)
    # =========================
    is_pdf = file_obj.name.lower().endswith('.pdf')
    # Batas ukuran untuk proses asinkron (misal > 2MB)
    ASYNC_THRESHOLD = 2 * 1024 * 1024 

    if is_pdf and file_obj.size > ASYNC_THRESHOLD:
        return handle_async_pdf_download(request, file_obj)

    # --- PROSES SYNC (Untuk file kecil/non-PDF) ---
    try:
        file_obj.file.seek(0)
        content_type = mimetypes.guess_type(file_obj.name)[0] or 'application/octet-stream'

        if is_pdf:
            from storage.services.dlp_service import add_pdf_watermark
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_input:
                for chunk in decrypt_stream(file_obj.file):
                    tmp_input.write(chunk)
                input_path = tmp_input.name

            try:
                watermarked_path = add_pdf_watermark(
                    input_path, 
                    request.user.get_full_name() or request.user.username,
                    request.user.email
                )

                response = CleanupFileResponse(
                    open(watermarked_path, 'rb'), 
                    content_type='application/pdf',
                    cleanup_paths=[input_path, watermarked_path]
                )
                response['Content-Disposition'] = f'attachment; filename="{file_obj.name}"'
                return response
            except Exception as dlp_err:
                if os.path.exists(input_path): os.remove(input_path)
                raise dlp_err

        # Non-PDF Streaming
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

def handle_async_pdf_download(request, file_obj):
    """
    Mengelola flow download asinkron via Celery.
    """
    from django.shortcuts import render

    cache_key = f"download_task_{request.user.id}_{file_obj.id}"
    task_info = cache.get(cache_key)

    # 1. Jika sudah selesai, langsung serve
    if task_info and task_info.get('status') == 'completed':
        file_path = task_info.get('file_path')
        if os.path.exists(file_path):
            response = FileResponse(open(file_path, 'rb'), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{file_obj.name}"'
            return response
        else:
            task_info = None

    # 2. Jika belum ada task, jalankan Celery
    if not task_info:
        task = process_pdf_watermark_task.delay(
            str(file_obj.id),
            request.user.id,
            request.user.get_full_name() or request.user.username,
            request.user.email
        )
        task_info = {'status': 'processing', 'task_id': task.id}
        cache.set(cache_key, task_info, 300)

    # 3. Tampilkan halaman "Menyiapkan Download"
    return render(request, 'storage/preparing_download.html', {
        'file': file_obj,
        'task_id': task_info.get('task_id')
    })

@login_required
def check_download_status(request, file_id):
    """
    Endpoint AJAX untuk mengecek status task Celery.
    """
    from django.http import JsonResponse
    from celery.result import AsyncResult

    cache_key = f"download_task_{request.user.id}_{file_id}"
    task_info = cache.get(cache_key)

    if not task_info:
        return JsonResponse({'status': 'not_found'})

    if task_info.get('status') == 'completed':
        return JsonResponse({'status': 'completed'})

    res = AsyncResult(task_info.get('task_id'))
    if res.ready():
        try:
            result_data = res.result
            if isinstance(result_data, dict) and result_data.get('status') == 'success':
                task_info['status'] = 'completed'
                task_info['file_path'] = result_data.get('file_path')
                cache.set(cache_key, task_info, 300)
                return JsonResponse({'status': 'completed'})
            else:
                return JsonResponse({'status': 'failed', 'error': str(result_data)})
        except Exception as e:
            return JsonResponse({'status': 'failed', 'error': str(e)})

    return JsonResponse({'status': 'processing'})