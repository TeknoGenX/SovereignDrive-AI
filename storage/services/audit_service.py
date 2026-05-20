# storage/services/audit_service.py

from storage.models import AuditLog
from django.contrib.contenttypes.models import ContentType

def log_action(user, action, target_object=None, description="", request=None):
    """
    Service terpusat untuk mencatat tindakan audit menggunakan GenericForeignKey.
    Mendukung target_object secara fleksibel (File, Folder, dll).
    """
    ip_address = None
    user_agent = None
    
    if request:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(',')[0]
        else:
            ip_address = request.META.get('REMOTE_ADDR')
        
        user_agent = request.META.get('HTTP_USER_AGENT')

    log_data = {
        'user': user,
        'action': action,
        'description': description,
        'ip_address': ip_address,
        'user_agent': user_agent
    }

    if target_object:
        log_data['content_object'] = target_object

    return AuditLog.objects.create(**log_data)
