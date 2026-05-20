# /home/andi-liani/code/awan/storage/views/get_file_access_role.py

from storage.selectors.access_selector import get_file_access_role as get_role

def get_file_access_role(file_obj, user):
    """
    Wrapper untuk memanggil logika pengecekan akses dari selector.
    """
    return get_role(file_obj, user)