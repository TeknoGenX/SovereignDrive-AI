from django.urls import path
from storage import views

app_name = 'storage'

urlpatterns = [
    # --- HALAMAN UTAMA ---
    path('', views.home, name='landing'), 
    path('privacy/', views.privacy_policy, name='privacy'),
    path('terms/', views.terms_of_service, name='terms'),
    path('help/', views.help_center, name='help'),
    path('help/user-guide/', views.user_guide, name='user_guide'),
    path('help/security/', views.security_docs, name='security_docs'),
    
    # --- DASHBOARD & PROFILE ---
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/folder/<uuid:folder_id>/', views.dashboard, name='dashboard_folder'),
    path('profile/', views.profile, name='profile'),

    # --- FOLDER ACTIONS ---
    path('folder/create/', views.create_folder, name='create_folder'),
    path('folder/<uuid:folder_id>/delete/', views.delete_folder, name='delete_folder'),
    path('folder/<uuid:folder_id>/share/', views.share_folder, name='share_folder'),
    path('folder/<uuid:folder_id>/download-zip/', views.download_folder_zip, name='download_folder_zip'),

    # --- FILE ACTIONS ---
    path('upload/', views.upload_file, name='upload_file'),
    path('file/<uuid:file_id>/', views.file_detail, name='file_detail'),
    path('file/<uuid:file_id>/view/', views.view_file, name='view_file'),
    path('file/<uuid:file_id>/download/', views.download_file, name='download_file'),
    path('file/<uuid:file_id>/download/status/', views.check_download_status, name='check_download_status'),
    path('file/<uuid:file_id>/edit/', views.edit_file, name='edit_file'),
    path('file/<uuid:file_id>/delete/', views.delete_file, name='delete_file'),
    path('file/<uuid:file_id>/share/', views.share_file, name='share_file'),

    # --- TONG SAMPAH ---
    path('trash/', views.trash_bin, name='trash_bin'),
    path('file/<uuid:file_id>/restore/', views.restore_file, name='restore_file'),
    path('file/<uuid:file_id>/hard-delete/', views.hard_delete_file, name='hard_delete_file'),
    path('folder/<uuid:folder_id>/restore/', views.restore_folder, name='restore_folder'),
    path('folder/<uuid:folder_id>/hard-delete/', views.hard_delete_folder, name='hard_delete_folder'),

    # --- FITUR PUBLIK ---
    path('file/<uuid:file_id>/toggle-public/', views.toggle_public, name='toggle_public'),
    path('p/<uuid:public_id>/', views.public_download, name='public_download'),
    path('s/<uuid:share_id>/', views.shared_link_view, name='shared_link_view'),

    # --- WEBHOOKS & API ---
    path('webhook/telegram/', views.telegram_webhook, name='telegram_webhook'),
]