import tempfile
import fitz  # PyMuPDF
from datetime import datetime

def add_pdf_watermark(input_path, user_name, user_email):
    """
    Menambahkan watermark ke setiap halaman PDF secara dinamis menggunakan file di disk.
    Mencegah RAM server penuh (OOM) dengan memproses file langsung dari disk.
    """
    # 1. Buka PDF dari path (Hemat RAM!)
    doc = fitz.open(input_path)
    
    # 2. Siapkan Teks Watermark
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    watermark_text = f"DOWNLOADED BY: {user_name} ({user_email})\nDATE: {timestamp}\nPRIVATE CLOUD AWAN - CONFIDENTIAL"
    
    for page in doc:
        page_width = page.rect.width
        page_height = page.rect.height
        
        # Tambahkan teks watermark (Kiri Bawah)
        page.insert_text(
            (50, page_height - 50),
            watermark_text,
            fontsize=10,
            color=(0.7, 0.7, 0.7),
            fill_opacity=0.5,
            rotate=0
        )
        
        # Watermark Diagonal (Tengah)
        page.insert_text(
            (page_width / 4, page_height / 2),
            "CONFIDENTIAL",
            fontsize=60,
            color=(0.8, 0.8, 0.8),
            fill_opacity=0.2,
            rotate=0
        )

    # 3. Simpan hasil ke file sementara (disk) daripada BytesIO (RAM)
    temp_output = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    doc.save(temp_output.name)
    doc.close()
    
    return temp_output.name
