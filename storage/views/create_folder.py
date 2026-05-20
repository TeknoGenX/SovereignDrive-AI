# /home/andi-liani/code/awan/storage/views/create_folder.py

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages

from storage.models import Folder

@login_required
def create_folder(request):
    """
    Fungsi untuk membuat folder baru, baik di root (halaman utama) 
    maupun di dalam folder lain (sub-folder).
    """
    if request.method != 'POST':
        return redirect('storage:dashboard')

    folder_name = request.POST.get('folder_name', '').strip()
    parent_id = request.POST.get('parent_id')

    # =========================
    # 1. VALIDASI NAMA
    # =========================
    if not folder_name:
        messages.error(request, "Nama folder tidak boleh kosong.")
        # Jika ada parent_id, kembalikan ke dalam folder tersebut
        if parent_id:
            return redirect('storage:dashboard_folder', folder_id=parent_id)
        return redirect('storage:dashboard')

    # =========================
    # 2. PARENT FOLDER (OPTIONAL)
    # =========================
    parent_folder = None
    if parent_id:
        parent_folder = get_object_or_404(
            Folder,
            id=parent_id,
            owner=request.user,
            is_trashed=False
        )

    # =========================
    # 3. CEK DUPLIKASI (COLLISION)
    # =========================
    if Folder.objects.filter(name=folder_name, parent=parent_folder, owner=request.user).exists():
        messages.warning(request, f'Folder "{folder_name}" sudah ada di lokasi ini.')
        if parent_id:
            return redirect('storage:dashboard_folder', folder_id=parent_id)
        return redirect('storage:dashboard')

    # =========================
    # 4. BUAT FOLDER
    # =========================
    try:
        Folder.objects.create(
            name=folder_name,
            parent=parent_folder,
            owner=request.user
        )
        messages.success(request, f'Folder "{folder_name}" berhasil dibuat.')
    except Exception as e:
        messages.error(request, f"Gagal membuat folder: {str(e)}")

    # =========================
    # 4. REDIRECT (ALIHKAN HALAMAN)
    # =========================
    if parent_id:
        return redirect('storage:dashboard_folder', folder_id=parent_id)

    return redirect('storage:dashboard')