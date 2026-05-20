from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    
    # Menggunakan fitur bawaan Django untuk Login & Logout
    path('login/', auth_views.LoginView.as_view(
        template_name='accounts/login.html',
        redirect_authenticated_user=True
    ), name='login'),
    
    # --- UBAH BARIS INI: Gunakan fungsi custom_logout buatan kita ---
    path('logout/', views.custom_logout, name='logout'),
]