# /home/andi-liani/code/awan/storage/models/mixins.py

from django.core.files.base import ContentFile
# Menggunakan service yang sudah kita buat sebelumnya
from storage.services.thumbnail import generate_image_thumbnail

class ThumbnailMixin:
    """
    Mixin khusus untuk menambahkan kemampuan pembuatan thumbnail pada model File.
    """
    IMAGE_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.gif', '.webp')

    def generate_thumbnail(self, raw_data=None):
        # 1. Pastikan file ada dan merupakan gambar
        if not self.file or not self.name.lower().endswith(self.IMAGE_EXTENSIONS):
            return

        try:
            # 2. Siapkan data bytes (mentah)
            if raw_data:
                file_bytes = raw_data
            else:
                self.file.seek(0)
                file_bytes = self.file.read()

                # Coba dekripsi jika file di hardisk terenkripsi
                try:
                    from storage.services.encryption import decrypt_file_data
                    file_bytes = decrypt_file_data(file_bytes)
                except Exception:
                    pass

            # 3. Panggil fungsi service untuk membuat thumbnail
            thumb_bytes = generate_image_thumbnail(file_bytes)

            # 4. Jika berhasil dibuat, simpan ke field thumbnail
            if thumb_bytes:
                ext = self.name.split('.')[-1].lower()
                fmt_ext = 'jpg' if ext in ['jpg', 'jpeg'] else ext
                thumb_name = f"thumb_{self.id}.{fmt_ext}"
                
                self.thumbnail.save(
                    thumb_name,
                    ContentFile(thumb_bytes),
                    save=False
                )

        except Exception as e:
            print(f"Thumbnail Error ({self.name}): {e}")