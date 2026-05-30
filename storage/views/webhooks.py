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
    Webhook Telegram yang AMAN & ASINKRON: 
    Validasi via telegram_chat_id dan offload kerja berat ke Celery.
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
        
        if 'message' in update and 'document' in update['message']:
            message = update['message']
            chat_id = str(message['chat']['id'])
            doc = message['document']
            
            # 1. IDENTIFIKASI USER (Via telegram_chat_id di Profile)
            if not UserProfile.objects.filter(telegram_chat_id=chat_id).exists():
                return JsonResponse({"status": "user unknown"}, status=403)

            # 2. OFF-LOAD KERJA KE CELERY (Disk-to-Disk & API calls)
            from storage.tasks import process_telegram_upload_task
            process_telegram_upload_task.delay(
                chat_id, 
                doc['file_id'], 
                doc.get('file_name', 'telegram_file'),
                doc.get('file_size', 0)
            )

            # 3. BALAS INSTAN KE TELEGRAM (User Experience)
            bot_token = getattr(settings, 'TELEGRAM_BOT_TOKEN', '')
            api_url = f'https://api.telegram.org/bot{bot_token}'
            requests.post(f'{api_url}/sendMessage', data={
                'chat_id': chat_id,
                'text': f'⏳ Sedang memproses file "{doc.get("file_name")}"... Mohon tunggu.'
            })

            return JsonResponse({"status": "processing_started"})

        return JsonResponse({"status": "ignored"})

    except Exception as e:
        print(f"🔥 Webhook Critical Error: {e}")
        return JsonResponse({"status": "error", "message": str(e)}, status=500)