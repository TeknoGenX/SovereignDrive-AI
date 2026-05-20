# /home/andi-liani/code/awan/storage/services/thumbnail.py

import io
from PIL import Image

def generate_image_thumbnail(raw_data: bytes, max_size=(256, 256)) -> bytes:
    """
    Menerima raw_data (bytes) dari file.
    Jika file tersebut adalah gambar, fungsi ini akan membuat thumbnail
    dan mengembalikan data bytes-nya. Jika bukan, akan mengembalikan None.
    """
    try:
        # 1. Buka gambar dari data bytes di memori
        img = Image.open(io.BytesIO(raw_data))

        # 2. Konversi format warna jika perlu
        # (Misal: PNG dengan background transparan (RGBA) diubah ke RGB agar ukurannya lebih kecil saat disimpan sbg JPEG)
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")

        # 3. Buat thumbnail
        # Fungsi .thumbnail() bawaan Pillow akan memperkecil gambar 
        # namun tetap mempertahankan rasio aslinya (tidak gepeng)
        img.thumbnail(max_size)

        # 4. Simpan hasil thumbnail ke dalam buffer memori
        thumb_io = io.BytesIO()
        img.save(thumb_io, format='JPEG', quality=85)
        
        # Kembalikan data bytes dari thumbnail yang sudah jadi
        return thumb_io.getvalue()

    except IOError:
        # IOError biasanya terjadi jika 'raw_data' bukanlah file gambar (misal: PDF, TXT, MP4)
        # Kita abaikan saja secara diam-diam dan kembalikan None
        return None
    except Exception as e:
        print(f"Gagal membuat thumbnail: {e}")
        return None