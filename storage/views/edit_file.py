# /home/andi-liani/code/awan/storage/views/edit_file.py

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponseForbidden
from django.contrib import messages

from storage.models import File
from .get_file_access_role import get_file_access_role

@login_required
def edit_file(request, file_id):
    """
    Fungsi untuk mengubah nama file. Hanya bisa dilakukan oleh Owner / Editor.
    """
    file_obj = get_object_or_404(File, id=file_id, is_trashed=False)

    # =========================
    # 1. CEK AKSES
    # =========================
    if get_file_access_role(file_obj, request.user) != 'editor':
        return HttpResponseForbidden("Hanya Editor atau Pemilik yang bisa mengubah nama file.")

    # =========================
    # 2. POST → UPDATE NAMA
    # =========================
    if request.method == 'POST':
        new_name = request.POST.get('new_name', '').strip()

        if not new_name:
            messages.error(request, "Nama file tidak boleh kosong.")
        else:
            file_obj.name = new_name
            file_obj.save()
            messages.success(request, "Nama file berhasil diperbarui.")
            
    # Balik ke halaman detail baik sukses maupun gagal/bukan POST
    return redirect('storage:file_detail', file_id=file_id)