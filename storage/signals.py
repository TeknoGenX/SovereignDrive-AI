# /home/andi-liani/code/awan/storage/signals.py

import os
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.db.models import Sum, F

from storage.models import File, UserProfile

# ==========================================
# 0. CAPTURE OLD STATE FOR QUOTA TRACKING
# ==========================================
@receiver(pre_save, sender=File)
def capture_old_is_trashed(sender, instance, **kwargs):
    """
    Simpan status is_trashed lama ke dalam instance sementara
    agar bisa dibandingkan di post_save.
    """
    if instance.pk:
        try:
            old_instance = File.objects.get(pk=instance.pk)
            instance._old_is_trashed = old_instance.is_trashed
        except File.DoesNotExist:
            instance._old_is_trashed = None
    else:
        instance._old_is_trashed = None

# ==========================================
# 1. OTOMATIS BUAT PROFIL SAAT USER MENDAFTAR
# ==========================================
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Jika ada User baru terdaftar, otomatis buatkan UserProfile (kuota penyimpanan).
    """
    if created:
        UserProfile.objects.get_or_create(user=instance)

# ==========================================
# 2. OTOMATIS UPDATE KUOTA SECARA INKREMENTAL
# ==========================================
@receiver(post_save, sender=File)
def update_quota_on_save(sender, instance, created, **kwargs):
    """
    Update kuota secara inkremental (F expression).
    Menangani file baru, restorasi file, dan pemindahan ke sampah.
    """
    if created:
        if not instance.is_trashed:
            UserProfile.objects.filter(user=instance.owner).update(
                storage_used=F('storage_used') + instance.size
            )
    else:
        # Deteksi perubahan status is_trashed
        old_is_trashed = getattr(instance, '_old_is_trashed', None)
        
        if old_is_trashed is not None and old_is_trashed != instance.is_trashed:
            if instance.is_trashed: # False -> True (Masuk Sampah)
                UserProfile.objects.filter(user=instance.owner).update(
                    storage_used=F('storage_used') - instance.size
                )
            else: # True -> False (Restore dari Sampah)
                UserProfile.objects.filter(user=instance.owner).update(
                    storage_used=F('storage_used') + instance.size
                )

@receiver(post_delete, sender=File)
def update_quota_on_delete(sender, instance, **kwargs):
    """
    Hanya kurangi kuota jika file yang dihapus PERMANEN 
    sebelumnya berstatus TIDAK di tong sampah (is_trashed=False).
    Jika file sudah di tong sampah, kuotanya sudah dikurangi saat masuk tong sampah.
    """
    if not instance.is_trashed:
        UserProfile.objects.filter(user=instance.owner).update(
            storage_used=F('storage_used') - instance.size
        )

# ==========================================
# 3. OTOMATIS PANGGIL AI & THUMBNAIL (CELERY)
# ==========================================
@receiver(post_save, sender=File)
def trigger_asynchronous_tasks(sender, instance, created, **kwargs):
    """
    Kirim tugas asinkron (Celery) untuk Indexing AI dan Pembuatan Thumbnail.
    Dibungkus Try-Except agar kegagalan Broker (Redis) tidak mematikan upload.
    """
    if created and not instance.is_trashed:
        try:
            from storage.tasks import process_file_and_index, generate_thumbnail_task
            
            # 1. Indexing & OCR AI
            process_file_and_index.delay(str(instance.id))
            
            # 2. Thumbnailing (hanya untuk file gambar)
            exts = ('.png', '.jpg', '.jpeg', '.gif', '.webp')
            if instance.name.lower().endswith(exts):
                generate_thumbnail_task.delay(str(instance.id))
                print(f"Triggered Asynchronous Tasks for {instance.name}")
                
        except Exception as e:
            # Jika Redis/Broker mati, cukup cetak ke log, jangan hentikan upload
            print(f"⚠️ GAGAL PEMICU CELERY: {e}")
            pass

# ==========================================
# 4. OTOMATIS HAPUS FILE FISIK DARI SERVER
# ==========================================
@receiver(post_delete, sender=File)
def delete_physical_file(sender, instance, **kwargs):
    """
    Jika file benar-benar dihapus permanen dari database (hard delete),
    hapus juga file aslinya dari hardisk agar tidak menjadi sampah.
    """
    # Hapus file utama
    if instance.file and os.path.isfile(instance.file.path):
        os.remove(instance.file.path)
        
    # Hapus file thumbnail (jika ada)
    if instance.thumbnail and os.path.isfile(instance.thumbnail.path):
        os.remove(instance.thumbnail.path)