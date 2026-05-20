# /home/andi-liani/code/awan/storage/views/webhooks.py

import json
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.base import ContentFile
from django.contrib.auth.models import User
from django.conf import settings

from storage.models import File

import json
import requests
import hashlib
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

from storage.models import UserProfile
from storage.services.upload_service import upload_file as service_upload_file

@csrf_exempt
def telegram_webhook(request):
    """
    Webhook Telegram yang AMAN: Mendukung Enkripsi AES, Cek Kuota, 
    dan Verifikasi Identitas User via Chat ID.
    """
    # 0. VERIFIKASI TOKEN (Safety Gate)
    webhook_token = request.GET.get('token')
    secret_token = hashlib.sha256(settings.SECRET_KEY.encode()).hexdigest()[:16]
    
    if webhook_token != secret_token:
        return HttpResponseForbidden("Webhook Token Tidak Valid.")

    if request.method != 'POST':
        return JsonResponse({"status": "invalid method"}, status=405)

    try:
        update = json.loads(request.body.decode('utf-8'))
        
        # Validasi struktur pesan Telegram
        if 'message' in update and 'document' in update['message']:
            message = update['message']
            chat_id = message['chat']['id']
            doc = message['document']
            
            # 1. IDENTIFIKASI USER (Via mapping Chat ID di Profile)
            # Trik Hackathon: Kita cari profile yang punya chat_id cocok
            # Jika tidak ada, kita tolak demi privasi.
            try:
                profile = UserProfile.objects.get(user__username=str(chat_id)) # Simulasi mapping
                user = profile.user
            except UserProfile.DoesNotExist:
                # Fallback: Tolak jika user tidak dikenal
                return JsonResponse({"status": "user unknown"}, status=403)

            # 2. DOWNLOAD FILE DARI TELEGRAM
            bot_token = getattr(settings, 'TELEGRAM_BOT_TOKEN', '')
            api_url = f'https://api.telegram.org/bot{bot_token}'
            
            file_res = requests.get(f'{api_url}/getFile?file_id={doc["file_id"]}').json()
            file_path = file_res['result']['file_path']
            download_url = f'https://api.telegram.org/file/bot{bot_token}/{file_path}'
            
            file_content = requests.get(download_url).content
            
            # 3. WRAP CONTENT (Agar sesuai dengan upload_service)
            uploaded_file = SimpleUploadedFile(doc['file_name'], file_content)

            # 4. ENCRYPT & SAVE (Gunakan Service Pusat)
            # Ini otomatis: Enkripsi AES + Update Kuota + Trigger AI Indexing
            new_file = service_upload_file(user, uploaded_file)

            # 5. BALAS KE TELEGRAM
            requests.post(f'{api_url}/sendMessage', data={
                'chat_id': chat_id,
                'text': f'🔒 File "{new_file.name}" AMAN & TERENKRIPSI di AWAN Cloud!'
            })

            return JsonResponse({"status": "success", "file_id": str(new_file.id)})

        return JsonResponse({"status": "ignored"})

    except Exception as e:
        print(f"🔥 Webhook Critical Error: {e}")
        return JsonResponse({"status": "error", "message": str(e)}, status=500)