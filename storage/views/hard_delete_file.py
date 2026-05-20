# /home/andi-liani/code/awan/storage/views/hard_delete_file.py

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.db import transaction

from storage.models import File
from .get_user_profile import get_user_profile

@login_required
def hard_delete_file(request, file_id):
    """
    Menghapus file secara permanen dari server dan database.
    Pembaruan kuota ditangani secara otomatis oleh Signals saat file dihapus (is_trashed=True).
    """
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'

    # Menggunakan atomic transaction agar jika terjadi error, database tidak rusak
    with transaction.atomic():
        file_obj = get_object_or_404(
            File,
            id=file_id,
            owner=request.user,
            is_trashed=True
        )

        # Hapus file: post_delete signal akan otomatis mengembalikan kuota
        # jika file tersebut tidak dihitung dalam kuota saat is_trashed=True.
        # Catatan: Di signals.py kita sudah mengabaikan file is_trashed=True.
        file_obj.delete()

    msg = "File berhasil dihapus permanen!"

    # =========================
    # 3. RESPONSE
    # =========================
    if is_ajax:
        return JsonResponse({'message': msg})

    messages.success(request, msg)
    return redirect('storage:trash_bin')