# /home/andi-liani/code/awan/storage/views/delete_file.py

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse

from storage.models import File, FileAccess

@login_required
def delete_file(request, file_id):
    """
    Pindahkan file ke sampah tanpa membuang user keluar dari folder saat ini.
    """
    file_obj = get_object_or_404(File, id=file_id)
    user = request.user
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'

    if file_obj.owner == user:
        # 1. Tandai sebagai terhapus
        file_obj.is_trashed = True
        
        # 2. Simpan. (Ini akan otomatis memicu Signals untuk update kuota storage!)
        file_obj.save() 
        msg = f'File "{file_obj.name}" dipindahkan ke sampah.'
        msg_type = 'warning'
    else:
        # Jika bukan owner, hapus saja aksesnya
        FileAccess.objects.filter(file=file_obj, user=user).delete()
        msg = "Akses file dihapus."
        msg_type = 'success'

    # 3. Response
    if is_ajax:
        return JsonResponse({'message': msg})

    if msg_type == 'warning':
        messages.warning(request, msg)
    else:
        messages.success(request, msg)

    # 4. KUNCI UX: Kembali ke halaman asal (tetap di folder yang sama)
    return redirect(request.META.get('HTTP_REFERER', 'storage:dashboard'))