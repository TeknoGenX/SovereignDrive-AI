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

@shared_task(bind=True, max_retries=2)
def process_pdf_watermark_task(self, file_id, user_id, user_name, user_email):
    """
    Task asinkron untuk watermarking PDF besar.
    Hasil disimpan di direktori temporary media.
    """
    try:
        from storage.models import File
        from storage.services.encryption import decrypt_stream
        from storage.services.dlp_service import add_pdf_watermark
        from django.conf import settings
        import shutil
        
        file_obj = File.objects.get(id=file_id)
        
        # 1. Dekripsi ke file sementara
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_input:
            file_obj.file.seek(0)
            for chunk in decrypt_stream(file_obj.file):
                tmp_input.write(chunk)
            input_path = tmp_input.name

        try:
            # 2. Tambahkan watermark
            watermarked_path = add_pdf_watermark(input_path, user_name, user_email)
            
            # 3. Pindahkan ke lokasi yang bisa diakses (Internal Media)
            output_dir = os.path.join(settings.MEDIA_ROOT, 'temp_exports', str(user_id))
            os.makedirs(output_dir, exist_ok=True)
            
            final_path = os.path.join(output_dir, f"{file_id}.pdf")
            shutil.move(watermarked_path, final_path)
            
            # Cleanup input
            if os.path.exists(input_path): os.remove(input_path)
            
            return {"status": "success", "file_path": final_path}
            
        except Exception as e:
            if os.path.exists(input_path): os.remove(input_path)
            raise e

    except Exception as exc:
        raise self.retry(exc=exc, countdown=5)

@shared_task
def cleanup_temporary_downloads_task():
    """
    Membersihkan file temporary di temp_exports yang sudah lebih dari 2 jam.
    Berjalan secara periodik (misal setiap jam).
    """
    from django.conf import settings
    import time
    
    export_dir = os.path.join(settings.MEDIA_ROOT, 'temp_exports')
    if not os.path.exists(export_dir):
        return "Directory not found"
        
    now = time.time()
    count = 0
    # Berjalan melalui semua subfolder user
    for root, dirs, files in os.walk(export_dir):
        for name in files:
            path = os.path.join(root, name)
            # Jika file lebih tua dari 2 jam (7200 detik)
            if os.stat(path).st_mtime < now - 7200:
                os.remove(path)
                count += 1
                
    return f"Berhasil membersihkan {count} file temporary."

@shared_task
def sync_all_users_quota_task():
    """
    Sinkronisasi ulang kuota penyimpanan untuk semua user.
    Mencegah penyimpangan data (data drift) antara signal dan realita DB.
    """
    from django.contrib.auth.models import User
    from django.db.models import Sum
    from storage.models import File, UserProfile
    
    users = User.objects.all()
    updated_count = 0
    
    for user in users:
        actual_usage = File.objects.filter(owner=user, is_trashed=False).aggregate(total=Sum('size'))['total'] or 0
        profile, _ = UserProfile.objects.get_or_create(user=user)
        
        if profile.storage_used != actual_usage:
            profile.storage_used = actual_usage
            profile.save()
            updated_count += 1
            
    return f"Audit Selesai. {updated_count} user dikoreksi kuotanya."

@shared_task
def process_telegram_upload_task(chat_id, file_id, file_name, file_size):
    """
    Mengunduh file dari Telegram, mengenkripsi, dan menyimpannya ke storage.
    Dijalankan secara asinkron agar webhook Telegram tidak timeout.
    """
    import requests
    from django.conf import settings
    from django.core.files.uploadedfile import SimpleUploadedFile
    from storage.models import UserProfile
    from storage.services.upload_service import upload_file as service_upload_file

    try:
        # 1. Validasi User
        profile = UserProfile.objects.get(telegram_chat_id=str(chat_id))
        user = profile.user

        # 2. Get Download URL
        bot_token = getattr(settings, 'TELEGRAM_BOT_TOKEN', '')
        api_url = f'https://api.telegram.org/bot{bot_token}'
        
        file_res = requests.get(f'{api_url}/getFile?file_id={file_id}').json()
        if not file_res.get('ok'):
            return f"Gagal mendapatkan info file dari Telegram: {file_res}"
            
        file_path = file_res['result']['file_path']
        download_url = f'https://api.telegram.org/file/bot{bot_token}/{file_path}'
        
        # 3. Download (Streaming to Disk to avoid OOM)
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False) as tmp_tele:
            response = requests.get(download_url, stream=True)
            if response.status_code != 200:
                return "Gagal mengunduh file dari server Telegram."
            
            for chunk in response.iter_content(chunk_size=128*1024):
                tmp_tele.write(chunk)
            tmp_tele.flush()
            tmp_tele_path = tmp_tele.name

        try:
            from django.core.files import File as DjangoFile
            with open(tmp_tele_path, 'rb') as f:
                django_file = DjangoFile(f, name=file_name)
                # upload_service needs .size
                django_file.size = os.path.getsize(tmp_tele_path)
                
                new_file = service_upload_file(user, django_file)

        finally:
            if os.path.exists(tmp_tele_path):
                os.remove(tmp_tele_path)

        # 5. Notifikasi Balik ke Telegram
        requests.post(f'{api_url}/sendMessage', data={
            'chat_id': chat_id,
            'text': f'✅ File "{new_file.name}" berhasil diamankan!\nID: {new_file.id}'
        })

        return f"Sukses mengolah file Telegram {new_file.id}"

    except UserProfile.DoesNotExist:
        return f"User dengan Chat ID {chat_id} tidak terdaftar."
    except Exception as e:
        return f"Error proses Telegram: {e}"

@shared_task
def create_audit_log_task(user_id, action, target_content_type_id=None, target_object_id=None, description="", ip_address=None, user_agent=None):
    """
    Menulis Audit Log ke database secara asinkron.
    Mencegah penulisan log yang lambat menghambat respons aplikasi.
    """
    from django.contrib.auth.models import User
    from django.contrib.contenttypes.models import ContentType
    from storage.models import AuditLog
    
    try:
        user = User.objects.get(id=user_id) if user_id else None
        
        log_data = {
            'user': user,
            'action': action,
            'description': description,
            'ip_address': ip_address,
            'user_agent': user_agent
        }
        
        if target_content_type_id and target_object_id:
            log_data['content_type_id'] = target_content_type_id
            log_data['object_id'] = target_object_id
            
        AuditLog.objects.create(**log_data)
        return f"Audit log created: {action}"
    except Exception as e:
        return f"Gagal membuat audit log: {e}"

@shared_task
def update_elasticsearch_index_task(file_id, action='update'):
    """
    Sinkronisasi manual ke Elasticsearch via Celery.
    Digunakan setelah operasi bulk seperti 'move to trash' folder.
    """
    from storage.models import File
    try:
        from storage.documents import FileDocument
    except ImportError:
        return "ES Document not found"

    try:
        if action == 'delete':
            # Hapus dari index
            try:
                doc = FileDocument(meta={'id': file_id})
                doc.delete()
                return f"Deleted from index: {file_id}"
            except Exception:
                pass
            return "File not in index"

        file_obj = File.objects.get(id=file_id)
        doc = FileDocument(
            meta={'id': str(file_obj.id)},
            name=file_obj.name,
            owner_id=file_obj.owner.id,
            is_trashed=file_obj.is_trashed,
            extracted_text=file_obj.extracted_text
        )
        doc.save()
        return f"Indexed: {file_obj.name}"
    except File.DoesNotExist:
        return "File not found"
    except Exception as e:
        return f"ES Task Error: {e}"
