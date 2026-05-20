# /home/andi-liani/code/awan/storage/views/dashboard.py

from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.db.models import Q, Sum
from django.http import HttpResponseForbidden

from storage.models import (
    File, Folder,
    FileAccess, FolderAccess,
    FileAccessLog, UserProfile
)

@login_required
def dashboard(request, folder_id=None):
    """
    Fungsi ini menangani tampilan halaman utama (Dashboard).
    Termasuk perhitungan kuota penyimpanan, pencarian file, dan daftar file/folder.
    """
    user = request.user

    # =========================
    # 1. PROFILE & STORAGE (Selector Terpusat)
    # =========================
    from storage.selectors.profile_selector import get_user_storage_stats
    stats = get_user_storage_stats(user)
    
    profile = stats['profile']
    used_gb = stats['used_gb']
    limit_gb = stats['limit_gb']
    storage_percent = stats['storage_percent']

    # =========================
    # 2. GREETING (SAPAAN)
    # =========================
    hour = datetime.now().hour
    if 5 <= hour < 12:
        greeting = "Selamat Pagi! 🌅"
    elif 12 <= hour < 18:
        greeting = "Selamat Siang! ☀️"
    else:
        greeting = "Selamat Malam! 🌙"

    # =========================
    # 3. SEARCH & CURRENT FOLDER
    # =========================
    search_query = request.GET.get('q', '').strip()
    current_folder = None

    if folder_id:
        current_folder = get_object_or_404(Folder, id=folder_id, is_trashed=False)

        # Cek apakah user memiliki akses ke folder ini
        has_access = (
            current_folder.owner == user or
            FolderAccess.objects.filter(folder=current_folder, user=user).exists()
        )

        if not has_access:
            return HttpResponseForbidden("Akses Ditolak.")

    # =========================
    # 4. QUERY FILE & FOLDER
    # =========================
    if search_query:
        # Jika user melakukan pencarian
        folder_filter = Q(name__icontains=search_query)
        folders = Folder.objects.filter(
            folder_filter,
            Q(owner=user) | Q(accesses__user=user),
            is_trashed=False
        ).distinct()

        file_filter = Q(name__icontains=search_query)

        # Integrasi Elasticsearch (Jika ada)
        try:
            from storage.documents import FileDocument
            from elasticsearch_dsl import Q as ES_Q
            
            # Query utama: prioritaskan nama file, tapi cari juga di isi file (OCR)
            # Berikan bobot (boost) lebih tinggi pada nama file
            es_results = FileDocument.search().query(
                "bool",
                should=[
                    ES_Q("multi_match", query=search_query, fields=['name^3', 'name.suggest'], fuzziness="AUTO"),
                    ES_Q("multi_match", query=search_query, fields=['extracted_text', 'extracted_text.suggest'], fuzziness="AUTO"),
                ],
                minimum_should_match=1
            ).filter(
                'term', owner_id=user.id
            ).filter(
                'term', is_trashed=False
            )[:100]

            found_ids = [hit.meta.id for hit in es_results]
            if found_ids:
                file_filter |= Q(id__in=found_ids)

        except Exception as e:
            print(f"Elasticsearch Error: {e}") # Akan print ke console jika ES mati

        files = File.objects.filter(
            file_filter,
            Q(owner=user) | Q(accesses__user=user),
            is_trashed=False
        ).distinct()

    else:
        # Jika tidak ada pencarian, tampilkan isi folder saat ini
        if current_folder:
            folders = Folder.objects.filter(parent=current_folder, is_trashed=False)
            files = File.objects.filter(folder=current_folder, is_trashed=False)
        else:
            folders = Folder.objects.filter(owner=user, parent=None, is_trashed=False)
            files = File.objects.filter(owner=user, folder=None, is_trashed=False)

    # =========================
    # 5. SHARED FOLDERS & FILES
    # =========================
    shared_folders = Folder.objects.filter(
        accesses__user=user,
        is_trashed=False
    ).distinct()

    shared_files = File.objects.filter(
        accesses__user=user,
        is_trashed=False
    ).distinct()

    # =========================
    # 6. ROOT FOLDERS & SUGGESTIONS
    # =========================
    root_folders = Folder.objects.filter(
        owner=user,
        parent=None,
        is_trashed=False
    ).order_by('name')

    # Mengambil file yang sering diakses (Suggested Files)
    recent_logs = FileAccessLog.objects.filter(user=user).select_related('file')[:15]
    suggested_files = list(
        File.objects.filter(owner=user, is_trashed=False).order_by('-created_at')[:3]
    )

    seen_ids = set(f.id for f in suggested_files)

    for log in recent_logs:
        if log.file.id not in seen_ids and not log.file.is_trashed:
            suggested_files.append(log.file)
            seen_ids.add(log.file.id)

        if len(suggested_files) >= 3:
            break

    # =========================
    # 7. RENDER KE HTML
    # =========================
    context = {
        'current_folder': current_folder,
        'folders': folders,
        'files': files,
        'shared_folders': shared_folders,
        'shared_files': shared_files,
        
        'profile': profile,
        'used_gb': used_gb,
        'limit_gb': limit_gb,
        'storage_percent': storage_percent,
        
        'search_query': search_query,
        'root_folders': root_folders,
        'greeting': greeting,
        'suggested_files': suggested_files[:3],
    }
    return render(request, 'storage/dashboard.html', context)