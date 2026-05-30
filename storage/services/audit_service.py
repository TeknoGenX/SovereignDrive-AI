# storage/services/audit_service.py

from django.contrib.contenttypes.models import ContentType
from storage.tasks import create_audit_log_task

def log_action(user, action, target_object=None, description="", request=None):
    """
    Service terpusat untuk mencatat tindakan audit secara asinkron.
    """
    ip_address = None
    user_agent = None
    
    if request:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        ip_address = x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')
        user_agent = request.META.get('HTTP_USER_AGENT')

    user_id = user.id if user and not user.is_anonymous else None
    
    ct_id = None
    obj_id = None
    if target_object:
        ct = ContentType.objects.get_for_model(target_object)
        ct_id = ct.id
        obj_id = str(target_object.pk)

    # Kirim ke Celery
    create_audit_log_task.delay(
        user_id,
        action,
        target_content_type_id=ct_id,
        target_object_id=obj_id,
        description=description,
        ip_address=ip_address,
        user_agent=user_agent
    )
