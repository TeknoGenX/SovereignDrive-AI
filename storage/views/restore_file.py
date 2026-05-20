from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse

from storage.models import File

@login_required
def restore_file(request, file_id):
    """
    Mengembalikan file dari Tong Sampah dengan logika cerdas (Smart Restore).
    Pembaruan kuota ditangani secara otomatis oleh Signals saat is_trashed diubah.
    """
    file_obj = get_object_or_404(
        File,
        id=file_id,
        owner=request.user,
        is_trashed=True
    )

    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'

    # =========================
    # 1. SMART RESTORE LOGIC
    # =========================
    if file_obj.folder and file_obj.folder.is_trashed:
        file_obj.folder = None
        messages.info(request, f"File '{file_obj.name}' dikembalikan ke Root karena folder induknya masih di Tong Sampah.")

    # Mengubah is_trashed akan memicu Signal untuk menambah kembali storage_used
    file_obj.is_trashed = False
    file_obj.save()

    msg = f"File '{file_obj.name}' berhasil dikembalikan."

    # =========================
    # 2. RESPONSE
    # =========================
    if is_ajax:
        return JsonResponse({
            'message': msg,
            'id': str(file_obj.id)
        })

    messages.success(request, msg)
    return redirect('storage:trash_bin')