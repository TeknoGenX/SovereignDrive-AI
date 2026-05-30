import os
import tempfile
import zipfile
from django.http import HttpResponseForbidden, FileResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required

from storage.models import File, Folder, FolderAccess
from storage.services.encryption import decrypt_stream
from storage.views.download_file import CleanupFileResponse

@login_required
def download_folder_zip(request, folder_id):
    """
    Mengunduh folder sebagai ZIP dengan efisiensi RAM tinggi (Anti-OOM).
    Mendukung dekripsi streaming dan penggunaan disk buffer.
    """
    folder = get_object_or_404(Folder, id=folder_id, is_trashed=False)

    # 1. Cek Akses (Owner atau Shared)
    has_access = (
        folder.owner == request.user or
        FolderAccess.objects.filter(folder=folder, user=request.user).exists()
    )

    if not has_access:
        return HttpResponseForbidden("Akses Ditolak.")

    # 2. Buat File ZIP Sementara di Disk
    temp_zip = tempfile.NamedTemporaryFile(delete=False, suffix=".zip")
    temp_zip_path = temp_zip.name
    temp_zip.close()

    try:
        with zipfile.ZipFile(temp_zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            def add_folder_to_zip(current_folder, archive_path=""):
                # A. Tambah File dalam Folder ini
                files = File.objects.filter(folder=current_folder, is_trashed=False)
                for f in files:
                    # Gunakan tempfile untuk dekripsi per file agar hemat RAM
                    with tempfile.NamedTemporaryFile(delete=False) as tmp_decrypted:
                        f.file.seek(0)
                        try:
                            for chunk in decrypt_stream(f.file):
                                tmp_decrypted.write(chunk)
                            tmp_decrypted.flush()
                            tmp_decrypted_path = tmp_decrypted.name
                            tmp_decrypted.close()

                            # Tambahkan ke ZIP dari disk
                            zip_file.write(tmp_decrypted_path, arcname=f"{archive_path}{f.name}")
                        finally:
                            if os.path.exists(tmp_decrypted.name):
                                os.remove(tmp_decrypted.name)

                # B. Tambah Subfolder (Recursion)
                subfolders = Folder.objects.filter(parent=current_folder, is_trashed=False)
                for sub in subfolders:
                    add_folder_to_zip(sub, f"{archive_path}{sub.name}/")

            # Mulai proses rekursif
            add_folder_to_zip(folder, f"{folder.name}/")

        # 3. Kirim File ke User menggunakan CleanupFileResponse agar ZIP dihapus setelah terkirim
        response = CleanupFileResponse(
            open(temp_zip_path, 'rb'), 
            content_type='application/zip',
            cleanup_paths=[temp_zip_path]
        )
        response['Content-Disposition'] = f'attachment; filename="{folder.name}.zip"'

        return response

    except Exception as e:
        if os.path.exists(temp_zip_path):
            os.remove(temp_zip_path)
        return HttpResponseForbidden(f"Gagal membuat ZIP: {str(e)}")
