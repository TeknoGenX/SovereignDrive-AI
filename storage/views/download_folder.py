import io
import zipfile
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required

from storage.models import File, Folder, FolderAccess
from storage.services.encryption import decrypt_file_data # Gunakan path service yang benar

@login_required
def download_folder_zip(request, folder_id):
    folder = get_object_or_404(Folder, id=folder_id, is_trashed=False)

    # Cek Akses (Owner atau Shared)
    has_access = (
        folder.owner == request.user or
        FolderAccess.objects.filter(folder=folder, user=request.user).exists()
    )

    if not has_access:
        return HttpResponseForbidden("Akses Ditolak.")

    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        def add_folder_to_zip(current_folder, path=""):
            # Tambah File
            files = File.objects.filter(folder=current_folder, is_trashed=False)
            for f in files:
                try:
                    f.file.seek(0)
                    data = decrypt_file_data(f.file.read())
                    zip_file.writestr(f"{path}{f.name}", data)
                except Exception:
                    # Fallback jika tidak terenkripsi
                    f.file.seek(0)
                    zip_file.writestr(f"{path}{f.name}", f.file.read())

            # Tambah Subfolder (Recursion)
            subfolders = Folder.objects.filter(parent=current_folder, is_trashed=False)
            for sub in subfolders:
                add_folder_to_zip(sub, f"{path}{sub.name}/")

        add_folder_to_zip(folder, f"{folder.name}/")

    response = HttpResponse(zip_buffer.getvalue(), content_type='application/zip')
    response['Content-Disposition'] = f'attachment; filename="{folder.name}.zip"'
    return response