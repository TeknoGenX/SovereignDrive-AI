# /home/andi-liani/code/awan/storage/documents.py

from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from storage.models import File

@registry.register_document
class FileDocument(Document):
    """
    Konfigurasi Elasticsearch untuk model File.
    Mendukung pencarian pintar (AI Search) berbasis OCR dan metadata.
    """
    # Identitas Pemilik
    owner_id = fields.IntegerField()
    
    # Metadata Tambahan
    size = fields.LongField()
    created_at = fields.DateField()
    is_public = fields.BooleanField()
    
    # Pencarian Pintar (Smart Search)
    # Teks hasil OCR / Ekstraksi
    extracted_text = fields.TextField(
        attr='extracted_text',
        analyzer='indonesian', # Gunakan analyzer Indonesia untuk hasil lebih akurat
        fields={
            'raw': fields.KeywordField(),
            'suggest': fields.CompletionField(), # Untuk fitur auto-complete
        }
    )

    # Nama File dengan Fuzzy Matching
    name = fields.TextField(
        fields={
            'raw': fields.KeywordField(),
            'suggest': fields.CompletionField(),
        }
    )

    def prepare_owner_id(self, instance):
        return instance.owner.id
    
    def prepare_size(self, instance):
        return instance.size

    def prepare_created_at(self, instance):
        return instance.created_at

    def prepare_is_public(self, instance):
        return instance.is_public

    class Index:
        name = 'awan_files_v2'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0,
            'max_result_window': 10000,
        }

    class Django:
        model = File
        ignore_signals = True # Tetap asinkron via Celery
        fields = [
            'is_trashed',
        ]
