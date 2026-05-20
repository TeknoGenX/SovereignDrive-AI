# /home/andi-liani/code/awan/storage/views/upload_file.py

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib import messages
from storage.models import Folder, FolderAccess, UserProfile
from storage.services.upload_service import upload_file as service_upload_file

@login_required
def upload_file(request):
    """
    Fungsi untuk mengunggah file. Mendukung GET (render form) 
    dan POST (proses upload via AJAX/Normal).
    """
    # 1. RENDER FORM (GET)
    if request.method == 'GET':
        folder_id = request.GET.get('folder')
        target_folder = None
        if folder_id:
            target_folder = get_object_or_404(Folder, id=folder_id, is_trashed=False)
        
        return render(request, 'storage/upload_file.html', {
            'target_folder': target_folder
        })

    # 2. PROSES UPLOAD (POST)
    uploaded_file = request.FILES.get('file') # Menggunakan 'file' sesuai standar Dropzone/XHR
    folder_id = request.POST.get('folder_id')
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.POST.get('is_ajax')

    if not uploaded_file:
        if is_ajax: return JsonResponse({'error': 'Pilih file terlebih dahulu.'}, status=400)
        messages.error(request, "Pilih file terlebih dahulu.")
        return redirect('storage:dashboard')

    # Validasi Akses Folder
    target_folder = None
    if folder_id:
        target_folder = get_object_or_404(Folder, id=folder_id, is_trashed=False)
        if target_folder.owner != request.user:
            access = FolderAccess.objects.filter(folder=target_folder, user=request.user).first()
            if not access or access.role != 'editor':
                if is_ajax: return JsonResponse({'error': 'Akses Ditolak.'}, status=403)
                return HttpResponseForbidden("Akses Ditolak.")

    # Validasi Kuota
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if profile.storage_used + uploaded_file.size > profile.storage_limit:
        msg = "Kuota penyimpanan penuh! Gagal mengunggah."
        if is_ajax: return JsonResponse({'error': msg}, status=400)
        messages.error(request, msg)
        return redirect('storage:dashboard')

    try:
        # Panggil service upload yang sudah dioptimasi (Streaming + Encryption)
        new_file = service_upload_file(request.user, uploaded_file, target_folder)

        if is_ajax:
            return JsonResponse({
                'message': 'Unggah berhasil!',
                'name': new_file.name,
                'id': str(new_file.id)
            })

        messages.success(request, f"File '{new_file.name}' berhasil diunggah.")
        return redirect('storage:dashboard_folder', folder_id=folder_id) if folder_id else redirect('storage:dashboard')

    except Exception as e:
        if is_ajax: return JsonResponse({'error': str(e)}, status=500)
        messages.error(request, f"Gagal mengunggah: {str(e)}")
        return redirect('storage:dashboard')