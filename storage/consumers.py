import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from storage.models import File
from storage.selectors.access_selector import get_file_access_role

class FileCollabConsumer(AsyncWebsocketConsumer):
    """
    Consumer untuk kolaborasi real-time pada file tertentu.
    Menangani Live Cursor dan Broadcast Komentar dengan Auth Check.
    """
    async def connect(self):
        self.user = self.scope['user']
        self.file_id = self.scope['url_route']['kwargs']['file_id']
        self.room_group_name = f'file_{self.file_id}'

        # 1. CEK OTENTIKASI & AKSES
        if not self.user.is_authenticated:
            await self.close()
            return

        has_access = await self.check_file_access(self.file_id, self.user)
        if not has_access:
            await self.close()
            return

        # 2. Gabung ke grup file
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    @database_sync_to_async
    def check_file_access(self, file_id, user):
        try:
            file_obj = File.objects.get(id=file_id, is_trashed=False)
            return get_file_access_role(file_obj, user) is not None
        except File.DoesNotExist:
            return False

    async def disconnect(self, close_code):
        # Keluar dari grup
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message dari WebSocket (Client)
    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type')

        # 1. Menangani Live Cursor
        if message_type == 'cursor_move':
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'cursor_update',
                    'user': self.scope['user'].username if self.scope['user'].is_authenticated else 'Guest',
                    'x': data.get('x'),
                    'y': data.get('y')
                }
            )
        
        # 2. Notifikasi Komentar Baru (untuk update UI tanpa refresh)
        elif message_type == 'new_comment':
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'comment_broadcast',
                    'author': data.get('author'),
                    'content': data.get('content'),
                    'created_at': data.get('created_at')
                }
            )

    # Handler untuk cursor_update
    async def cursor_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'cursor_update',
            'user': event['user'],
            'x': event['x'],
            'y': event['y']
        }))

    # Handler untuk comment_broadcast
    async def comment_broadcast(self, event):
        await self.send(text_data=json.dumps({
            'type': 'new_comment',
            'author': event['author'],
            'content': event['content'],
            'created_at': event['created_at']
        }))
