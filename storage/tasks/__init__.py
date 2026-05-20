import io
import os
import tempfile
from celery import shared_task

# Kita impor library berat di dalam task atau dengan penanganan error
# agar worker tidak crash saat startup jika library belum terinstall.
try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None

try:
    import pytesseract
except ImportError:
    pytesseract = None

from PIL import Image

@shared_task(bind=True, max_retries=3)
def process_file_and_index(self, file_id):
    """
    Worker AI Hybrid yang dioptimalkan RAM-nya.
    Menggunakan TemporaryFile untuk memproses file besar tanpa membebani memori.
    """
    try:
        from storage.models import File
        from storage.services.encryption import decrypt_stream
        
        try:
            from storage.documents import FileDocument
        except ImportError:
            FileDocument = None
            
        file_obj = File.objects.get(id=file_id)
        if file_obj.is_trashed:
            return f"Dibatalkan: File {file_obj.name} di Trash."

        # Batasi OCR hanya untuk file di bawah 50MB
        if file_obj.size > 50 * 1024 * 1024:
            return f"File {file_obj.name} terlalu besar untuk AI (>50MB)."

        extracted_text = ""
        ext = file_obj.name.lower()

        # TAHAP 0: DEKRIPSI KE TEMPORARY FILE (RAM-Friendly)
        # NamedTemporaryFile memungkinkan library lain (fitz/PIL) membaca langsung dari disk
        with tempfile.NamedTemporaryFile(delete=True) as tmp_file:
            file_obj.file.seek(0)
            for chunk in decrypt_stream(file_obj.file):
                tmp_file.write(chunk)
            tmp_file.flush() # Pastikan semua data tertulis ke disk
            
            # TAHAP 1: EKSTRAKSI BERDASARKAN TIPE
            if ext.endswith('.pdf'):
                if not fitz:
                    return "Gagal: Library PyMuPDF (fitz) tidak tersedia."
                
                # Buka PDF dari path file sementara (Hemat RAM!)
                with fitz.open(tmp_file.name) as doc:
                    for page in doc:
                        extracted_text += page.get_text()

            elif ext.endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp')):
                if not pytesseract:
                    return "Gagal: Tesseract OCR tidak tersedia."
                
                # Buka Gambar dari path file sementara
                with Image.open(tmp_file.name) as img:
                    extracted_text = pytesseract.image_to_string(img)

            elif ext.endswith('.txt'):
                tmp_file.seek(0)
                extracted_text = tmp_file.read().decode('utf-8', errors='ignore')

        # TAHAP 2: NLP & INDEXING
        if extracted_text.strip():
            # Simpan hasil sementara ke DB
            file_obj.extracted_text = extracted_text
            file_obj.save(update_fields=['extracted_text'])

            # Lakukan NLP Preprocessing jika tersedia
            try:
                from storage.services.nlp_service import TextPreprocessor
                processor = TextPreprocessor()
                clean_tokens = processor.full_process(extracted_text)
                extracted_text = " ".join(clean_tokens)
                
                # Update DB dengan teks yang sudah bersih
                file_obj.extracted_text = extracted_text
                file_obj.save(update_fields=['extracted_text'])
            except Exception as nlp_err:
                print(f"NLP Preprocessing skipped: {nlp_err}")

            # Index ke Elasticsearch
            if FileDocument:
                try:
                    file_doc = FileDocument(
                        meta={'id': str(file_obj.id)},
                        name=file_obj.name,
                        owner_id=file_obj.owner.id,
                        is_trashed=file_obj.is_trashed,
                        extracted_text=extracted_text
                    )
                    file_doc.save()
                except Exception as es_err:
                    print(f"Elasticsearch Indexing Error: {es_err}")

        return f"Sukses memproses {file_obj.name}"

    except File.DoesNotExist:
        return "File tidak ditemukan."
    except Exception as exc:
        raise self.retry(exc=exc, countdown=10)

@shared_task
def generate_thumbnail_task(file_id):
    """Membuat thumbnail dengan efisiensi RAM tinggi."""
    try:
        from storage.models import File
        from storage.services.encryption import decrypt_stream
        from django.core.files.base import ContentFile
        
        file_obj = File.objects.get(id=file_id)
        ext = file_obj.name.lower()

        with tempfile.NamedTemporaryFile(delete=True) as tmp_file:
            file_obj.file.seek(0)
            for chunk in decrypt_stream(file_obj.file):
                tmp_file.write(chunk)
            tmp_file.flush()

            if ext.endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                with Image.open(tmp_file.name) as img:
                    # Gunakan buffer untuk hasil thumbnail saja (kecil)
                    thumb_io = io.BytesIO()
                    img.thumbnail((300, 300))
                    img.save(thumb_io, format='JPEG', quality=85)
                    
                    thumb_name = f"thumb_{file_obj.id}.jpg"
                    file_obj.thumbnail.save(thumb_name, ContentFile(thumb_io.getvalue()), save=False)
                    file_obj.save(update_fields=['thumbnail'])
                    return "Thumbnail gambar sukses"

            elif ext.endswith('.pdf') and fitz:
                with fitz.open(tmp_file.name) as doc:
                    if doc.page_count > 0:
                        page = doc.load_page(0)
                        pix = page.get_pixmap(alpha=False)
                        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                        
                        thumb_io = io.BytesIO()
                        img.thumbnail((400, 400))
                        img.save(thumb_io, format='JPEG', quality=80)
                        
                        thumb_name = f"thumb_pdf_{file_obj.id}.jpg"
                        file_obj.thumbnail.save(thumb_name, ContentFile(thumb_io.getvalue()), save=False)
                        file_obj.save(update_fields=['thumbnail'])
                        return "Thumbnail PDF sukses"

        return "Format tidak didukung"
    except Exception as e:
        return f"Gagal: {e}"
