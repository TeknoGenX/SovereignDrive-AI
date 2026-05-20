# /home/andi-liani/code/awan/storage/views/share_file.py

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.models import User

from storage.models import File, FileAccess

@login_required
def share_file(request, file_id):
    """
    Membagikan file ke pengguna lain dengan role tertentu (viewer/editor).
    """
    file_obj = get_object_or_404(
        File,
        id=file_id,
        owner=request.user,
        is_trashed=False
    )

    if request.method != 'POST':
        return redirect('storage:file_detail', file_id=file_id)

    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'

    target_username = request.POST.get('username')
    role = request.POST.get('role', 'viewer')

    # =========================
    # 1. VALIDASI ROLE
    # =========================
    if role not in ['viewer', 'editor']:
        msg = "Role tidak valid."
        if is_ajax:
            return JsonResponse({'error': msg}, status=400)
        messages.error(request, msg)
        return redirect('storage:file_detail', file_id=file_id)

    # =========================
    # 2. VALIDASI USER TARGET
    # =========================
    try:
        target_user = User.objects.get(username=target_username)
    except User.DoesNotExist:
        msg = "User tidak ditemukan."
        if is_ajax:
            return JsonResponse({'error': msg}, status=404)
        messages.error(request, msg)
        return redirect('storage:file_detail', file_id=file_id)

    if target_user == request.user:
        msg = "Tidak bisa membagikan file ke diri sendiri."
        if is_ajax:
            return JsonResponse({'error': msg}, status=400)
        messages.error(request, msg)
        return redirect('storage:file_detail', file_id=file_id)

    # =========================
    # 3. SHARE / UPDATE AKSES
    # =========================
    access, created = FileAccess.objects.update_or_create(
        file=file_obj,
        user=target_user,
        defaults={'role': role}
    )

    msg = f"Akses {'ditambahkan' if created else 'diperbarui'} untuk {target_user.username} sebagai {role}."

    # =========================
    # 4. RESPONSE
    # =========================
    if is_ajax:
        return JsonResponse({
            'message': msg,
            'username': target_user.username,
            'role': role
        })

    messages.success(request, msg)
    return redirect('storage:file_detail', file_id=file_id)