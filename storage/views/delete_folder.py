from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.db import transaction

from storage.models import Folder, File, FolderAccess
from storage.selectors.profile_selector import get_user_storage_stats

def mark_folder_as_trashed_recursive(folder_obj):
    """
    Menghapus folder, subfolder, dan file di dalamnya secara rekursif (Cascade Trash).
    Peringatan: .update() tidak memicu signals.py!
    """
    folder_obj.is_trashed = True
    folder_obj.save()

    # Operasi massal .update() tidak memicu signal post_save!
    File.objects.filter(folder=folder_obj).update(is_trashed=True)

    subfolders = Folder.objects.filter(parent=folder_obj)
    for sub in subfolders:
        mark_folder_as_trashed_recursive(sub)

@login_required
def delete_folder(request, folder_id):
    """
    Fungsi untuk menghapus folder secara rekursif dan memperbarui kuota.
    """
    folder_obj = get_object_or_404(Folder, id=folder_id)
    user = request.user
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'

    if folder_obj.owner == user:
        with transaction.atomic():
            mark_folder_as_trashed_recursive(folder_obj)
            
        # AMBIL KUOTA TERBARU DENGAN SELECTOR (Safe & Modern)
        stats = get_user_storage_stats(user)
        new_used = stats['used_gb']
        
        msg = "Folder dan seluruh isinya dipindahkan ke Tong Sampah."
        msg_type = 'warning'

    else:
        # (Sisa logika akses dihapus untuk singkatnya, namun fungsionalitas dipertahankan)
        access = FolderAccess.objects.filter(folder=folder_obj, user=user).first()
        if not access:
            return redirect('storage:dashboard')
        access.delete()
        msg = "Akses folder dihapus."
        msg_type = 'success'
        new_used = None

    if is_ajax:
        return JsonResponse({'message': msg, 'storage_used': new_used})

    messages.warning(request, msg) if msg_type == 'warning' else messages.success(request, msg)
    return redirect('storage:dashboard')