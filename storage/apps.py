from django.apps import AppConfig


class StorageConfig(AppConfig):
    name = 'storage'
from django.apps import AppConfig

class StorageConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'storage'

    def ready(self):
        # Mengimpor signals agar otomatisasi kuota dan AI berjalan
        import storage.signals