from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseForbidden

from storage.models import File, FileAccessLog
from storage.selectors.access_selector import get_file_access_role

@login_required
def file_detail(request, file_id):
    """
    Halaman detail file (UI + Share Link).
    Menampilkan informasi file dan statistik penggunaan.
    """
    # =========================
    # 1. AMBIL FILE
    # =========================
    file_obj = get_object_or_404(File, id=file_id, is_trashed=False)

    # =========================
    # 2. CEK AKSES
    # =========================
    role = get_file_access_role(file_obj, request.user)
    if not role:
        return HttpResponseForbidden("Akses Ditolak.")

    # =========================
    # 3. LOG AKSES
    # =========================
    FileAccessLog.objects.create(user=request.user, file=file_obj)

    # =========================
    # 4. PUBLIC LINK
    # =========================
    public_url = None
    if file_obj.is_public:
        public_url = request.build_absolute_uri(f'/p/{file_obj.public_id}/')

    # =========================
    # 5. DETEKSI TIPE FILE
    # =========================
    ext = file_obj.name.split('.')[-1].lower() if '.' in file_obj.name else ''

    is_image = ext in ['jpg', 'jpeg', 'png', 'gif', 'webp']
    is_pdf = ext == 'pdf'
    is_video = ext in ['mp4', 'webm', 'ogg']

    # =========================
    # 6. CONTEXT & RENDER
    # =========================
    context = {
        'file': file_obj,
        'role': role,
        'public_url': public_url,

        'is_image': is_image,
        'is_pdf': is_pdf,
        'is_video': is_video,
        'extension': ext,
    }

    return render(request, 'storage/file_detail.html', context)