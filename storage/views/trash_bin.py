# /home/andi-liani/code/awan/storage/views/trash_bin.py

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Sum

from storage.models import File, Folder

@login_required
def trash_bin(request):
    """
    Menampilkan halaman Tong Sampah.
    Berisi daftar file dan folder yang dihapus sementara (is_trashed=True).
    """
    # =========================
    # 1. AMBIL DATA YANG DIHAPUS
    # =========================
    trashed_files = File.objects.filter(
        owner=request.user,
        is_trashed=True
    ).order_by('-created_at')

    trashed_folders = Folder.objects.filter(
        owner=request.user,
        is_trashed=True
    ).order_by('-created_at')

    # =========================
    # 2. HITUNG UKURAN TOTAL
    # =========================
    total_size = trashed_files.aggregate(
        total=Sum('size')
    )['total'] or 0

    # =========================
    # 3. CONTEXT & RENDER
    # =========================
    context = {
        'files': trashed_files,
        'folders': trashed_folders,
        'total_files': trashed_files.count(),
        'total_folders': trashed_folders.count(),
        'total_size': total_size,
    }

    return render(request, 'storage/trash_bin.html', context)