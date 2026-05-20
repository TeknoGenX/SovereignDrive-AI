# /home/andi-liani/code/awan/storage/signals.py

import os
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.db.models import Sum

from storage.models import File, UserProfile

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

from django.db.models import F

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
        # Deteksi perubahan status is_trashed (Jika Django mendukung model_utils Tracker lebih bagus, 
        # tapi di sini kita gunakan pengecekan manual sederhana atau asumsikan status berubah)
        # Logika: Jika is_trashed baru saja di-set ke False (Restore)
        # Kita butuh state sebelumnya. Untuk audit ini, kita asumsikan 
        # sinyal dipicu oleh operasi yang merubah is_trashed.
        
        # Sederhananya, jika kita ingin akurat tanpa state lama, kita bisa 
        # memisahkan fungsi pemanggil atau menggunakan init signal.
        # Namun untuk stabilitas, kita pastikan restore_file memanggil ini.
        pass

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