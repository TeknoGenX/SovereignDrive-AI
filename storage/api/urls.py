# /home/andi-liani/code/awan/storage/api/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    FolderViewSet, FileViewSet, SharedLinkViewSet, 
    CommentViewSet, ApprovalViewSet, AuditLogViewSet
)

# Registrasi Router API
api_router = DefaultRouter()
api_router.register(r'folders', FolderViewSet, basename='api-folder')
api_router.register(r'files', FileViewSet, basename='api-file')
api_router.register(r'shares', SharedLinkViewSet, basename='api-share')
api_router.register(r'comments', CommentViewSet, basename='api-comment')
api_router.register(r'approvals', ApprovalViewSet, basename='api-approval')
api_router.register(r'audit-logs', AuditLogViewSet, basename='api-audit-log')

urlpatterns = [
    # --- ENDPOINT API v1 ---
    # Karena di core/urls.py kamu memanggilnya dengan 'api/storage/',
    # maka di sini cukup tambahkan 'v1/' saja.
    # Nanti URL lengkapnya jadi: localhost:8000/api/storage/v1/folders/
    path('v1/', include(api_router.urls)),
    
    # Endpoint untuk Autentikasi JWT (Login API)
    path('v1/auth/login/', TokenObtainPairView.as_view(), name='api_token_obtain'),
    path('v1/auth/refresh/', TokenRefreshView.as_view(), name='api_token_refresh'),
]