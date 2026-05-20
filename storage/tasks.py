import io
import os
import fitz  # PyMuPDF
import pytesseract  # Tesseract OCR
from PIL import Image
from celery import shared_task

@shared_task(bind=True, max_retries=3)
def process_file_and_index(self, file_id):
    """Worker AI Hybrid Cerdas dengan dukungan Streaming Enkripsi"""
    print(f"\n[CELERY WORKER] Memulai pemindaian AI untuk file ID: {file_id}...")
    try:
        from storage.models import File
        from storage.services.encryption import decrypt_stream
        
        try:
            from storage.documents import FileDocument
        except ImportError:
            FileDocument = None
            
        file_obj = File.objects.get(id=file_id)
        if file_obj.is_trashed:
            return f"[CELERY WORKER] Dibatalkan: File {file_obj.name} ada di tong sampah."

        extracted_text = ""
        
        # Batasi OCR hanya untuk file di bawah 50MB agar tidak membuat RAM worker jebol
        if file_obj.size > 50 * 1024 * 1024:
            return f"[CELERY WORKER] File terlalu besar untuk OCR/AI (>50MB)."

        # TAHAP 0: BUKA GEMBOK (STREAMING KE TEMP FILE / RAM)
        print(f"[CELERY WORKER] Mendekripsi file secara streaming...")
        file_obj.file.seek(0)
        
        decrypted_io = io.BytesIO()
        for chunk in decrypt_stream(file_obj.file):
            decrypted_io.write(chunk)
            
        decrypted_bytes = decrypted_io.getvalue()

        # TAHAP 1: EKSTRAKSI TEKS
        if file_obj.name.lower().endswith('.pdf'):
            doc = fitz.open(stream=decrypted_bytes, filetype="pdf")
            for page in doc:
                extracted_text += page.get_text()
        elif file_obj.name.lower().endswith(('.png', '.jpg', '.jpeg')):
            img = Image.open(io.BytesIO(decrypted_bytes))
            extracted_text = pytesseract.image_to_string(img)
        elif file_obj.name.lower().endswith('.txt'):
            extracted_text = decrypted_bytes.decode('utf-8', errors='ignore')
            
        # TAHAP 1.5: NLP PREPROCESSING
        if extracted_text.strip():
            from storage.services.nlp_service import TextPreprocessor
            try:
                processor = TextPreprocessor()
                # Kita gunakan full_process untuk membersihkan corpus secara otomatis
                preprocessed_tokens = processor.full_process(extracted_text)
                
                # Masukkan kembali ke extracted_text sebagai string bersih untuk indexing
                extracted_text = " ".join(preprocessed_tokens)
                
                # SIMPAN KE DATABASE (Agar bisa dilihat di UI Detail)
                file_obj.extracted_text = extracted_text
                file_obj.save(update_fields=['extracted_text'])
                
                print(f"[CELERY WORKER] Preprocessing Sukses: {len(preprocessed_tokens)} tokens disimpan ke DB.")
            except Exception as nlp_err:
                print(f"[CELERY WORKER] Gagal Preprocessing NLP: {nlp_err}. Lanjutkan dengan raw text.")

        # TAHAP 2: INDEKSING (Isolasi Total ke Elasticsearch)
        if extracted_text.strip() and FileDocument:
            try:
                file_doc = FileDocument(
                    meta={'id': str(file_obj.id)},
                    name=file_obj.name,
                    owner_id=file_obj.owner.id,
                    is_trashed=file_obj.is_trashed,
                    extracted_text=extracted_text
                )
                file_doc.save() 
                print(f"[CELERY WORKER] SUKSES! Teks diindeks.")
            except Exception as es_err:
                print(f"!!! [CELERY WORKER] GAGAL INDEKS: Elasticsearch sedang Read-Only atau Penuh. ({es_err})")
                return f"Upload Berhasil, tapi Pencarian AI untuk {file_obj.name} tertunda (Disk ES Penuh)."
            
        return f"File {file_obj.name} di-scan."
        
    except File.DoesNotExist:
        return f"[CELERY WORKER] GAGAL: File ID {file_id} tidak ditemukan."
    except Exception as exc:
        raise self.retry(exc=exc, countdown=10)

@shared_task
def generate_thumbnail_task(file_id):
    """Membuat thumbnail di background secara asinkron (Mendukung Gambar & PDF)."""
    try:
        from storage.models import File
        from storage.services.encryption import decrypt_stream
        from django.core.files.base import ContentFile
        
        file_obj = File.objects.get(id=file_id)
        
        # 1. Dekripsi data ke memori
        file_obj.file.seek(0)
        decrypted_io = io.BytesIO()
        for chunk in decrypt_stream(file_obj.file):
            decrypted_io.write(chunk)
        decrypted_bytes = decrypted_io.getvalue()

        thumb_bytes = None
        ext = file_obj.name.lower()

        # 2. Logika Berdasarkan Tipe File
        if ext.endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
            # Gunakan fungsi generate_thumbnail bawaan model (jika ada)
            file_obj.generate_thumbnail(decrypted_bytes)
            file_obj.save(update_fields=['thumbnail'])
            return "Thumbnail gambar sukses"

        elif ext.endswith('.pdf'):
            # EKSTRAKSI HALAMAN PERTAMA PDF SEBAGAI GAMBAR
            doc = fitz.open(stream=decrypted_bytes, filetype="pdf")
            if doc.page_count > 0:
                page = doc.load_page(0)
                pix = page.get_pixmap(matrix=fitz.Matrix(0.5, 0.5)) # Downscale agar ringan
                img = Image.open(io.BytesIO(pix.tobytes("png")))
                
                thumb_io = io.BytesIO()
                img.save(thumb_io, format='JPEG', quality=80)
                thumb_bytes = thumb_io.getvalue()
                
                if thumb_bytes:
                    thumb_name = f"thumb_pdf_{file_obj.id}.jpg"
                    file_obj.thumbnail.save(thumb_name, ContentFile(thumb_bytes), save=False)
                    file_obj.save(update_fields=['thumbnail'])
                    return "Thumbnail PDF sukses"

        return "Format file tidak didukung untuk thumbnail"
    except Exception as e:
        print(f"Thumbnail task failed: {e}")
        return f"Gagal: {e}"
