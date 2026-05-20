from storage.models import UserProfile, File
from django.db.models import Sum

def get_user_storage_stats(user):
    """
    Menghitung statistik penyimpanan pengguna untuk UI.
    """
    profile, _ = UserProfile.objects.get_or_create(user=user)
    
    used_bytes = profile.storage_used
    limit_bytes = profile.storage_limit

    # Konversi ke GB
    used_gb = round(used_bytes / (1024 ** 3), 2)
    limit_gb = round(limit_bytes / (1024 ** 3), 2)

    # Minimal tampilan
    if used_bytes > 0 and used_gb == 0.0:
        used_gb = 0.01

    percent = (used_bytes / limit_bytes) * 100 if limit_bytes > 0 else 0
    if 0 < percent < 1:
        percent = 1

    return {
        'profile': profile,
        'used_bytes': used_bytes,
        'limit_bytes': limit_bytes,
        'used_gb': used_gb,
        'limit_gb': limit_gb,
        'storage_percent': percent
    }
