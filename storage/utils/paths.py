import uuid

def user_directory_path(instance, filename):
    """
    Obfuscation: Sembunyikan nama asli file di disk fisik server Ubuntu menggunakan UUID.
    Format: user_<id>/<uuid>.<ext>
    """
    ext = filename.split('.')[-1]
    safe_filename = f"{uuid.uuid4()}.{ext}"
    return f'user_{instance.owner.id}/{safe_filename}'
