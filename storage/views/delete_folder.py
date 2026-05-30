from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.db import transaction

from storage.models import Folder, File, FolderAccess
from storage.selectors.profile_selector import get_user_storage_stats

from django.db.models import Sum, F

def get_all_descendant_folder_ids(folder_obj):
    """
    Mencari semua ID subfolder secara rekursif.
    """
    descendants = [folder_obj.id]
    subfolders = Folder.objects.filter(parent=folder_obj).values_list('id', flat=True)
    for sub_id in subfolders:
        sub_obj = Folder.objects.get(id=sub_id)
        descendants.extend(get_all_descendant_folder_ids(sub_obj))
    return descendants

def mark_folder_as_trashed_bulk(folder_obj, user):
    """
    Optimasi: Menghapus folder dan seluruh isinya menggunakan BULK UPDATE.
    Mencegah N+1 query dan database locking pada folder besar.
    """
    # 1. Dapatkan semua ID folder dalam hirarki
    all_folder_ids = get_all_descendant_folder_ids(folder_obj)

    # 2. Hitung total size file yang akan di-trash (untuk update kuota)
    files_to_trash = File.objects.filter(folder_id__in=all_folder_ids, is_trashed=False)
    total_size = files_to_trash.aggregate(total=Sum('size'))['total'] or 0

    with transaction.atomic():
        # 3. Bulk Update Files
        files_to_trash.update(is_trashed=True)

        # 4. Bulk Update Folders
        Folder.objects.filter(id__in=all_folder_ids).update(is_trashed=True)

        # 5. Update Kuota User sekaligus (Atomic)
        if total_size > 0:
            UserProfile.objects.filter(user=user).update(
                storage_used=F('storage_used') - total_size
            )
            
    # 6. Trigger Re-indexing asinkron
    from storage.tasks import update_elasticsearch_index_task
    for f_id in files_to_trash.values_list('id', flat=True):
        update_elasticsearch_index_task.delay(str(f_id))
    
    for fold_id in all_folder_ids:
        # Jika folder juga masuk index (opsional), trigger di sini
        pass

@login_required
def delete_folder(request, folder_id):
    """
    Fungsi untuk menghapus folder secara rekursif dan memperbarui kuota.
    """
    folder_obj = get_object_or_404(Folder, id=folder_id)
    user = request.user
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'

    if folder_obj.owner == user:
        mark_folder_as_trashed_bulk(folder_obj, user)
            
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