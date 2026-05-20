import io
import fitz  # PyMuPDF
from datetime import datetime

def add_pdf_watermark(file_stream, user_name, user_email):
    """
    Menambahkan watermark ke setiap halaman PDF secara dinamis.
    Digunakan untuk DLP (Data Loss Prevention).
    """
    # 1. Baca PDF dari stream
    pdf_bytes = b"".join(file_stream)
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    
    # 2. Siapkan Teks Watermark
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    watermark_text = f"DOWNLOADED BY: {user_name} ({user_email})\nDATE: {timestamp}\nPRIVATE CLOUD AWAN - CONFIDENTIAL"
    
    for page in doc:
        # Tentukan posisi (Diagonal atau bawah)
        # Di sini kita gunakan posisi diagonal transparan
        page_width = page.rect.width
        page_height = page.rect.height
        
        # Tambahkan teks watermark
        # Kita gunakan fontsize yang cukup besar dan warna abu-abu transparan
        page.insert_text(
            (50, page_height - 50), # Posisi kiri bawah
            watermark_text,
            fontsize=10,
            color=(0.7, 0.7, 0.7), # Abu-abu terang
            fill_opacity=0.5,
            rotate=0
        )
        
        # Opsional: Tambahkan watermark diagonal di tengah
        page.insert_text(
            (page_width / 4, page_height / 2),
            "CONFIDENTIAL",
            fontsize=60,
            color=(0.8, 0.8, 0.8),
            fill_opacity=0.2,
            rotate=45
        )

    # 3. Simpan hasil ke BytesIO
    output_stream = io.BytesIO()
    doc.save(output_stream)
    doc.close()
    
    output_stream.seek(0)
    return output_stream
