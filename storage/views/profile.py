# /home/andi-liani/code/awan/storage/views/profile.py

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import IntegrityError
from storage.models import UserProfile
from storage.selectors.profile_selector import get_user_storage_stats

@login_required
def profile(request):
    user = request.user
    profile_obj, _ = UserProfile.objects.get_or_create(user=user)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'update_info':
            username = request.POST.get('username', '').strip()
            email = request.POST.get('email', '').strip()
            first_name = request.POST.get('first_name', '').strip()
            middle_name = request.POST.get('middle_name', '').strip()
            last_name = request.POST.get('last_name', '').strip()
            
            try:
                if username: user.username = username
                if email: user.email = email
                
                # Gabungkan First + Middle ke field first_name Django
                if middle_name:
                    user.first_name = f"{first_name} {middle_name}"
                else:
                    user.first_name = first_name
                    
                user.last_name = last_name
                user.save()
                messages.success(request, 'Identitas akun berhasil diperbarui!')
            except IntegrityError:
                messages.error(request, 'Username sudah digunakan oleh orang lain.')
            except Exception as e:
                messages.error(request, f'Gagal memperbarui profil: {str(e)}')
                
            return redirect('storage:profile')
            
        elif action == 'update_avatar':
            avatar_file = request.FILES.get('avatar')
            if avatar_file:
                profile_obj.avatar = avatar_file
                profile_obj.save()
                messages.success(request, 'Foto profil berhasil diubah!')
            return redirect('storage:profile')

    # Logika Cerdas: Pisahkan kembali first_name jika ada spasi (untuk ditampilkan di form)
    raw_first = user.first_name
    display_first = raw_first
    display_middle = ""
    
    if " " in raw_first:
        parts = raw_first.split(" ", 1)
        display_first = parts[0]
        display_middle = parts[1]

    stats = get_user_storage_stats(user)
    context = {
        'profile': profile_obj,
        'display_first': display_first,
        'display_middle': display_middle,
        'used_gb': stats['used_gb'],
        'limit_gb': stats['limit_gb'],
        'storage_percent': stats['storage_percent'],
        'used_bytes': stats['used_bytes'],
        'hide_nav': True,
        'hide_footer': True,
    }
    return render(request, 'storage/profile.html', context)
