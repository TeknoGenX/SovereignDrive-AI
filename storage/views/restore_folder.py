from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from storage.models import Folder, File

@login_required
def restore_folder(request, folder_id):
    """
    Mengembalikan folder dari tong sampah beserta seluruh file di dalamnya.
    """
    folder_obj = get_object_or_404(Folder, id=folder_id, owner=request.user)
    
    # 1. Pulihkan Folder
    folder_obj.is_trashed = False
    folder_obj.save()
    
    # 2. Pulihkan Semua File di Dalamnya secara Otomatis
    files_restored = File.objects.filter(folder=folder_obj, owner=request.user).update(is_trashed=False)
    
    messages.success(request, f"Folder '{folder_obj.name}' dan {files_restored} file di dalamnya berhasil dipulihkan.")
    return redirect('storage:trash_bin')
