from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
# 1. Form Registrasi yang Diperluas (Menambahkan Email)
class UserRegisterForm(UserCreationForm):
email = forms.EmailField(required=True, help_text='Wajib diisi untuk pemulihan akun.')
class Meta:
model = User
fields = ['username', 'email']
# 2. Form Update Profil (Nama & Email)
class UserUpdateForm(forms.ModelForm):
email = forms.EmailField(required=True)
class Meta:
model = User
fields = ['username', 'first_name', 'last_name', 'email']
/home/andi-liani/code/private-cloud/accounts/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
urlpatterns = [
path('register/', views.register, name='register'),
path('profile/', views.profile, name='profile'),
# Menggunakan fitur bawaan Django untuk Login & Logout
path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html',
redirect_authenticated_user=True), name='login'),
# --- UBAH BARIS INI: Gunakan fungsi custom_logout buatan kita ---
path('logout/', views.custom_logout, name='logout'),
]
