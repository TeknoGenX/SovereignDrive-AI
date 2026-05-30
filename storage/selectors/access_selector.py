from storage.models import FileAccess, FolderAccess, Folder

def get_file_access_role(file_obj, user):
    """
    Mengecek hak akses pengguna terhadap sebuah file secara efisien.
    Mengoptimalkan query dengan cara:
    1. Mengambil semua FolderAccess user dalam satu query (Memory Lookup).
    2. Menghindari N+1 query pada pengecekkan hierarki folder.
    3. Menggunakan .values() untuk meminimalisir pembuatan objek model yang berat.
    """
    # 1. OWNER LANGSUNG → FULL ACCESS (Editor)
    if file_obj.owner_id == user.id:
        return 'editor'

    # 2. IZIN LANGSUNG PADA FILE (Direct Access)
    file_access = FileAccess.objects.filter(file=file_obj, user=user).values_list('role', flat=True).first()
    if file_access:
        return file_access

    # 3. IZIN BERDASARKAN HIERARKI FOLDER (Inherited Access)
    if not file_obj.folder_id:
        return None

    # Optimasi: Ambil semua folder_id yang di-share ke user ini sekaligus.
    # Disimpan dalam dictionary untuk lookup O(1) di dalam loop.
    user_folder_accesses = dict(
        FolderAccess.objects.filter(user=user).values_list('folder_id', 'role')
    )

    # Telusuri ke atas (Parent Traversal)
    curr_folder_id = file_obj.folder_id
    visited_ids = set()
    max_depth = 50 # Limit keamanan untuk mencegah infinite loop atau struktur terlalu dalam

    while curr_folder_id and len(visited_ids) < max_depth:
        # Detect Cycle
        if curr_folder_id in visited_ids:
            print(f"⚠️ Terdeteksi Circular Reference pada folder {curr_folder_id}")
            break
        visited_ids.add(curr_folder_id)

        # A. Cek apakah folder ini ada di daftar yang di-share ke user
        if curr_folder_id in user_folder_accesses:
            return user_folder_accesses[curr_folder_id]

        # B. Ambil data folder untuk cek ownership dan parent_id berikutnya.
        # Menggunakan .values() lebih cepat daripada mengambil objek model lengkap.
        folder_data = Folder.objects.filter(id=curr_folder_id).values('parent_id', 'owner_id').first()
        
        if not folder_data:
            break

        # C. Jika user adalah owner dari salah satu parent folder, otomatis jadi Editor
        if folder_data['owner_id'] == user.id:
            return 'editor'

        # Naik ke folder induk
        curr_folder_id = folder_data['parent_id']

    return None
