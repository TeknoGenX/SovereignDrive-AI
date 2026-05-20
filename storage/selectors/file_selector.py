from django.db.models import Q
from storage.models import File

def get_user_files(user, folder=None):
    """
    Mengambil daftar file pengguna dengan optimasi select_related 
    untuk mencegah N+1 Query problem.
    """
    # Menggunakan select_related untuk menarik data owner dan folder dalam 1 query SQL
    qs = File.objects.select_related('owner', 'folder').filter(is_trashed=False)

    if folder:
        return qs.filter(folder=folder)

    # Menampilkan file di root (tanpa folder) milik user
    return qs.filter(owner=user, folder=None)

def get_file_by_id(file_id):
    return File.objects.select_related('owner', 'folder').filter(id=file_id, is_trashed=False).first()

def search_files(user, query):
    """
    Pencarian file dengan optimasi performa, mencakup pencarian nama file
    dan konten yang telah diekstrak (Content-based Search).
    """
    return File.objects.select_related('owner', 'folder').filter(
        Q(name__icontains=query) | Q(extracted_text__icontains=query),
        Q(owner=user) | Q(accesses__user=user),
        is_trashed=False
    ).distinct()