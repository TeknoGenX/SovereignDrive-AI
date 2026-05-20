from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/collab/(?P<file_id>[^/]+)/$', consumers.FileCollabConsumer.as_asgi()),
]
