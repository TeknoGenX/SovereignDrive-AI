# /home/andi-liani/code/awan/storage/views/file_detail.py

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseForbidden

from storage.models import File, FileAccessLog
from .get_file_access_role import get_file_access_role

# Coba import fungsi insight jika ada, jika tidak abaikan
try:
    from storage.insight import get_data_insight
except ImportError:
    get_data_insight = None

@login_required
def file_detail(request, file_id):
    """
    Halaman detail file (UI + Insight + Share Link).
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
    # 4. DATA INSIGHT (AI / ANALISIS FILE)
    # =========================
    stats, chart_labels, chart_data = {}, [], []
    if get_data_insight:
        try:
            stats, chart_labels, chart_data = get_data_insight(file_obj.file.path)
        except Exception as e:
            print(f"Gagal memuat insight: {e}")

    # =========================
    # 5. PUBLIC LINK
    # =========================
    public_url = None
    if file_obj.is_public:
        public_url = request.build_absolute_uri(f'/p/{file_obj.public_id}/')

    # =========================
    # 6. DETEKSI TIPE FILE
    # =========================
    ext = file_obj.name.split('.')[-1].lower() if '.' in file_obj.name else ''

    is_image = ext in ['jpg', 'jpeg', 'png', 'gif', 'webp']
    is_pdf = ext == 'pdf'
    is_video = ext in ['mp4', 'webm', 'ogg']

    # =========================
    # 7. CONTEXT & RENDER
    # =========================
    context = {
        'file': file_obj,
        'role': role,
        'public_url': public_url,
        
        'is_image': is_image,
        'is_pdf': is_pdf,
        'is_video': is_video,
        'extension': ext,
        
        'data_stats': stats,
        'chart_labels': chart_labels,
        'chart_data': chart_data,
    }

    return render(request, 'storage/file_detail.html', context)