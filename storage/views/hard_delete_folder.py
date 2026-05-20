from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from storage.models import Folder

@login_required
def hard_delete_folder(request, folder_id):
    """
    Menghapus folder secara permanen beserta seluruh isinya dari database.
    (Relasi CASCADE di model akan menangani penghapusan file terkait)
    """
    folder_obj = get_object_or_404(Folder, id=folder_id, owner=request.user)
    folder_name = folder_obj.name
    
    # Penghapusan objek folder
    folder_obj.delete()
    
    messages.success(request, f"Folder '{folder_name}' telah dihapus secara permanen.")
    return redirect('storage:trash_bin')
