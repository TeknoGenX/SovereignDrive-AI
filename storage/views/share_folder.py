# /home/andi-liani/code/awan/storage/views/share_folder.py

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.models import User

from storage.models import Folder, FolderAccess

@login_required
def share_folder(request, folder_id):
    """
    Membagikan folder ke pengguna lain dengan role tertentu.
    """
    folder = get_object_or_404(Folder, id=folder_id, owner=request.user)

    if request.method != 'POST':
        return redirect('storage:dashboard_folder', folder_id=folder_id)

    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'

    target_username = request.POST.get('username')
    role = request.POST.get('role', 'viewer')

    # =========================
    # 1. VALIDASI ROLE & USER
    # =========================
    if role not in ['viewer', 'editor']:
        msg = "Role tidak valid."
        if is_ajax:
            return JsonResponse({'error': msg}, status=400)
        messages.error(request, msg)
        return redirect('storage:dashboard_folder', folder_id=folder_id)

    try:
        target_user = User.objects.get(username=target_username)
    except User.DoesNotExist:
        msg = "User tidak ditemukan."
        if is_ajax:
            return JsonResponse({'error': msg}, status=404)
        messages.error(request, msg)
        return redirect('storage:dashboard_folder', folder_id=folder_id)

    if target_user == request.user:
        msg = "Tidak bisa membagikan ke diri sendiri."
        if is_ajax:
            return JsonResponse({'error': msg}, status=400)
        messages.error(request, msg)
        return redirect('storage:dashboard_folder', folder_id=folder_id)

    # =========================
    # 2. SHARE / UPDATE ROLE
    # =========================
    access, created = FolderAccess.objects.update_or_create(
        folder=folder,
        user=target_user,
        defaults={'role': role}
    )

    msg = f"Akses {'ditambahkan' if created else 'diperbarui'} untuk {target_user.username} sebagai {role}."

    if is_ajax:
        return JsonResponse({
            'message': msg,
            'username': target_user.username,
            'role': role
        })

    messages.success(request, msg)
    return redirect('storage:dashboard_folder', folder_id=folder_id)