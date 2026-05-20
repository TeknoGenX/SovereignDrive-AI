import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import storage.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# Inisialisasi ASGI secara eksplisit agar Django terpanggil dengan benar
django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(
            storage.routing.websocket_urlpatterns
        )
    ),
})
