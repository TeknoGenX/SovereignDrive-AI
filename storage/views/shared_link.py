from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseForbidden, StreamingHttpResponse, Http404
from storage.models import SharedLink, File, Folder
from storage.services.encryption import decrypt_stream
from django.utils import timezone

def shared_link_view(request, share_id):
    """
    View publik untuk mengakses file/folder yang dibagikan melalui link.
    Mendukung proteksi password dan pengecekan expiry date.
    """
    shared_link = get_object_or_404(SharedLink, share_id=share_id, is_active=True)

    # 1. Cek Expiry
    if shared_link.is_expired:
        return render(request, 'storage/shared/expired.html', status=410)

    # 2. Cek Password jika ada
    if shared_link.password:
        # Cek apakah password sudah ada di session
        session_key = f'share_auth_{shared_link.share_id}'
        if not request.session.get(session_key):
            if request.method == 'POST':
                password = request.POST.get('password')
                if shared_link.check_password(password):
                    request.session[session_key] = True
                    return redirect('storage:shared_link_view', share_id=share_id)
                else:
                    return render(request, 'storage/shared/password_required.html', {
                        'shared_link': shared_link,
                        'error': 'Password salah!'
                    })
            return render(request, 'storage/shared/password_required.html', {'shared_link': shared_link})

    # 3. Update Statistik
    shared_link.view_count += 1
    shared_link.save(update_fields=['view_count'])

    # 4. Tampilkan Konten
    if shared_link.file:
        file_obj = shared_link.file
        if request.GET.get('download') == '1':
            return _serve_decrypted_file(file_obj)
        
        return render(request, 'storage/shared/file_view.html', {
            'shared_link': shared_link,
            'file': file_obj
        })
    
    elif shared_link.folder:
        folder_obj = shared_link.folder
        
        # Handle download specific file inside this shared folder
        if request.GET.get('download') == '1' and request.GET.get('file_id'):
            file_id = request.GET.get('file_id')
            # Pastikan file tersebut memang ada di dalam folder yang dibagikan
            target_file = get_object_or_404(File, id=file_id, folder=folder_obj, is_trashed=False)
            return _serve_decrypted_file(target_file)

        # Tampilkan daftar file di folder tersebut (read-only viewer)
        files = File.objects.filter(folder=folder_obj, is_trashed=False)
        subfolders = Folder.objects.filter(parent=folder_obj, is_trashed=False)
        
        return render(request, 'storage/shared/folder_view.html', {
            'shared_link': shared_link,
            'folder': folder_obj,
            'files': files,
            'subfolders': subfolders
        })

    return HttpResponseForbidden("Konten tidak tersedia.")

def _serve_decrypted_file(file_obj):
    file_obj.file.seek(0)
    response = StreamingHttpResponse(
        decrypt_stream(file_obj.file),
        content_type='application/octet-stream'
    )
    response['Content-Disposition'] = f'attachment; filename="{file_obj.name}"'
    return response
