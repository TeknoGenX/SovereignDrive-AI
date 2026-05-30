from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.db import transaction
from django.db.models import Sum, F
from storage.models import Folder, File, UserProfile
from .delete_folder import get_all_descendant_folder_ids

def restore_folder_bulk(folder_obj, user):
    """
    Memulihkan folder dan seluruh isinya menggunakan BULK UPDATE.
    """
    # 1. Dapatkan semua ID folder dalam hirarki
    all_folder_ids = get_all_descendant_folder_ids(folder_obj)

    # 2. Hitung total size file yang akan di-restore (untuk update kuota)
    files_to_restore = File.objects.filter(folder_id__in=all_folder_ids, is_trashed=True)
    total_size = files_to_restore.aggregate(total=Sum('size'))['total'] or 0
    
    # Simpan ID file untuk re-indexing nanti
    file_ids = list(files_to_restore.values_list('id', flat=True))

    with transaction.atomic():
        # 3. Bulk Update Folders
        Folder.objects.filter(id__in=all_folder_ids).update(is_trashed=False)

        # 4. Bulk Update Files
        files_to_restore.update(is_trashed=False)

        # 5. Update Kuota User sekaligus (Atomic)
        if total_size > 0:
            UserProfile.objects.filter(user=user).update(
                storage_used=F('storage_used') + total_size
            )
            
    # 6. Trigger Re-indexing asinkron
    from storage.tasks import update_elasticsearch_index_task
    for f_id in file_ids:
        update_elasticsearch_index_task.delay(str(f_id))

@login_required
def restore_folder(request, folder_id):
    """
    Mengembalikan folder dari tong sampah beserta seluruh file dan subfolder di dalamnya.
    """
    folder_obj = get_object_or_404(Folder, id=folder_id, owner=request.user)
    
    restore_folder_bulk(folder_obj, request.user)
    
    messages.success(request, f"Folder '{folder_obj.name}' dan seluruh isinya berhasil dipulihkan.")
    return redirect('storage:trash_bin')
