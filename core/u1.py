from django.contrib import admin
from django.urls import path, include
from storage import views as storage_views # Import langsung views storage

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Root URL: Menampilkan Landing Page
    path('', storage_views.landing, name='landing'), 
    
    # Auth: Login, Register, Logout
    path('accounts/', include('accounts.urls')), 
    
    # Bisnis Logika: Dashboard, Upload, Telegram, dll.
    # Kita biarkan kosong '' agar rute di storage.urls yang mengatur
    path('', include('storage.urls')),
]

from django.contrib import admin
from django.urls import path, include
# KUNCI UTAMA: Wajib import ini
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.config.urls),
    # Rute ke app storage Anda
    path('', include('storage.urls')), 
    
    # Rute ke API jika ada
    # path('api/v1/', include(api_router.urls)),
]

# KUNCI KEDUA: Jalur akses file MEDIA hanya di mode DEBUG=True
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) # Tambahan keamanan untuk static
    
    