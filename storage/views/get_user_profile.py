# /home/andi-liani/code/awan/storage/views/get_user_profile.py

from django.core.cache import cache
from storage.models import UserProfile

def get_user_profile(user):
    """
    Mengambil profil pengguna. Memanfaatkan cache selama 5 menit (300 detik) 
    agar tidak perlu sering-sering query ke database.
    """
    cache_key = f"user_profile_{user.id}"
    profile = cache.get(cache_key)

    if not profile:
        profile, _ = UserProfile.objects.get_or_create(user=user)
        cache.set(cache_key, profile, 300)

    return profile