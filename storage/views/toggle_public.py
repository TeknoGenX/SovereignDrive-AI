# /home/andi-liani/code/awan/storage/views/toggle_public.py

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages

from storage.models import File

@login_required
def toggle_public(request, file_id):
    """
    Mengubah status is_public pada file. Jika aktif, file bisa diakses via public_url.
    """
    file_obj = get_object_or_404(File, id=file_id, owner=request.user)

    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'

    # =========================
    # 1. TOGGLE STATUS
    # =========================
    file_obj.is_public = not file_obj.is_public
    file_obj.save()

    status = "diaktifkan" if file_obj.is_public else "dinonaktifkan"

    # =========================
    # 2. GENERATE PUBLIC URL
    # =========================
    public_url = None
    if file_obj.is_public:
        # Menghasilkan URL lengkap (contoh: https://domainmu.com/p/abc123xyz/)
        public_url = request.build_absolute_uri(f'/p/{file_obj.public_id}/')

    msg = f"Tautan publik berhasil {status}."

    # =========================
    # 3. RESPONSE
    # =========================
    if is_ajax:
        return JsonResponse({
            'message': msg,
            'is_public': file_obj.is_public,
            'public_url': public_url
        })

    messages.success(request, msg)
    return redirect('storage:file_detail', file_id=file_id)