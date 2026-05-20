from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash, logout
from django.contrib.auth.forms import PasswordChangeForm
from .forms import UserRegisterForm, UserUpdateForm# --- TAMBAHAN: Import UserProfile dari aplikasi storage ---
from storage.models import UserProfile
def register(request):
if request.user.is_authenticated:
return redirect('dashboard')
if request.method == 'POST':
form = UserRegisterForm(request.POST)
if form.is_valid():
form.save()
username = form.cleaned_data.get('username')
messages.success(request, f'Akun {username} berhasil dibuat! Silakan login.')
return redirect('login')
else:
form = UserRegisterForm()
return render(request, 'accounts/register.html', {'form': form})
@login_required
def profile(request):
# Menangani 2 form sekaligus di satu halaman: Update Info & Ganti Password
if request.method == 'POST':
# Jika tombol "Update Profil" ditekan
if 'update_profile' in request.POST:
u_form = UserUpdateForm(request.POST, instance=request.user)
p_form = PasswordChangeForm(request.user) # Kosongkan form password
if u_form.is_valid():
u_form.save()
# --- LOGIKA PENYIMPANAN FOTO PROFIL (AVATAR) ---
if request.FILES.get('avatar'):
# Dapatkan atau buat profile jika user ini baru saja mendaftar
user_profile, created = UserProfile.objects.get_or_create(user=request.user)
user_profile.avatar = request.FILES['avatar']
user_profile.save()
# -----------------------------------------------
messages.success(request, 'Profil Anda berhasil diperbarui!')
return redirect('profile')
# Jika tombol "Ganti Password" ditekan
elif 'change_password' in request.POST:
u_form = UserUpdateForm(instance=request.user) # Kosongkan form profil
p_form = PasswordChangeForm(request.user, request.POST)
if p_form.is_valid():
user = p_form.save()
update_session_auth_hash(request, user) # Agar tidak otomatis logout
messages.success(request, 'Kata sandi Anda berhasil diubah!')
return redirect('profile')
else:
u_form = UserUpdateForm(instance=request.user)
p_form = PasswordChangeForm(request.user)context = {
'u_form': u_form,
'p_form': p_form
}
return render(request, 'accounts/profile.html', context)
def custom_logout(request):
"""Fungsi ini akan memaksa sistem menghancurkan sesi pengguna"""
if request.method == 'POST':
logout(request) # Perintah mutlak untuk membunuh sesi login
messages.info(request, "Anda telah berhasil keluar dengan aman.")
return redirect('login')
# Jika ada yang mencoba mengakses URL /logout/ secara langsung lewat browser (GET),
# cegah dan kembalikan ke dashboard.
return redirect('dashboard')
