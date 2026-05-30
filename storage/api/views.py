# /home/andi-liani/code/awan/storage/api/views.py

import os
import shutil
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.core.files.base import ContentFile
from django.http import StreamingHttpResponse
from django.db import transaction
from django.utils import timezone

# Menggunakan absolute import agar aman dari error ModuleNotFound
from storage.models import (
    Folder, File, FileChunk, SharedLink, FileVersion, 
    FileComment, ApprovalRequest, AuditLog
)
from storage.api.serializers import (
    FolderSerializer, FileSerializer, SharedLinkSerializer, 
    FileVersionSerializer, FileCommentSerializer, 
    ApprovalRequestSerializer, AuditLogSerializer
)

# Services
from storage.services.encryption import decrypt_stream
from storage.services.upload_service import upload_file as service_upload_file
from storage.services.audit_service import log_action

class FolderViewSet(viewsets.ModelViewSet):
    serializer_class = FolderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Folder.objects.filter(owner=self.request.user, is_trashed=False).order_by('-created_at')

    def perform_create(self, serializer):
        folder = serializer.save(owner=self.request.user)
        log_action(self.request.user, 'edit', target_object=folder, 
                   description=f"Dibuat folder baru: {folder.name}", request=self.request)

class FileViewSet(viewsets.ModelViewSet):
    serializer_class = FileSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        return File.objects.filter(owner=self.request.user, is_trashed=False).order_by('-created_at')

    def perform_create(self, serializer):
        uploaded_file = self.request.FILES.get('file')
        folder_id = self.request.data.get('folder')
        target_folder = None
        if folder_id:
            target_folder = Folder.objects.filter(id=folder_id, owner=self.request.user).first()
            
        if uploaded_file:
            new_file = service_upload_file(self.request.user, uploaded_file, target_folder)
            serializer.instance = new_file
            
            # ENTERPRISE: Buat Approval Request otomatis
            ApprovalRequest.objects.create(file=new_file, requester=self.request.user)
            
            log_action(self.request.user, 'upload', target_object=new_file, 
                       description=f"Upload file: {new_file.name}", request=self.request)
        else:
            file_obj = serializer.save(owner=self.request.user)
            log_action(self.request.user, 'upload', target_object=file_obj, 
                       description=f"Upload metadata file: {file_obj.name}", request=self.request)

    @action(detail=True, methods=['GET'])
    def download(self, request, pk=None):
        file_obj = self.get_object()
        
        # ENTERPRISE: Cek Approval sebelum download
        if hasattr(file_obj, 'approval') and file_obj.approval.status != 'approved':
             if file_obj.owner != request.user:
                 return Response({'error': 'File ini belum disetujui untuk diakses.'}, status=status.HTTP_403_FORBIDDEN)

        log_action(request.user, 'download', target_object=file_obj, 
                   description=f"Download file: {file_obj.name}", request=request)
        
        file_obj.file.seek(0)
        response = StreamingHttpResponse(
            decrypt_stream(file_obj.file),
            content_type='application/octet-stream'
        )
        response['Content-Disposition'] = f'attachment; filename="{file_obj.name}"'
        if file_obj.size:
            response['Content-Length'] = file_obj.size
            
        return response

    @action(detail=False, methods=['GET'])
    def search(self, request):
        query = request.GET.get('q', '').strip()
        if not query:
            return Response({'error': 'Search query is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        from storage.documents import FileDocument
        from elasticsearch_dsl import Q as ES_Q
        
        es_query = FileDocument.search().query(
            "bool",
            should=[
                ES_Q("multi_match", query=query, fields=['name^3'], fuzziness="AUTO"),
                ES_Q("multi_match", query=query, fields=['extracted_text'], fuzziness="AUTO"),
            ],
            minimum_should_match=1
        ).filter(
            'term', owner_id=request.user.id
        ).filter(
            'term', is_trashed=False
        )[:100]
        
        results = es_query.execute()
        found_ids = [hit.meta.id for hit in results]
        
        if not found_ids:
            return Response([])
        
        # Optimasi: Menjamin urutan file sesuai dengan skor relevansi Elasticsearch
        from django.db.models import Case, When
        preserved_order = Case(*[When(id=pk, then=pos) for pos, pk in enumerate(found_ids)])
        
        files = File.objects.filter(id__in=found_ids).order_by(preserved_order)
        
        log_action(request.user, 'view', description=f"Pencarian AI: '{query}'", request=request)

        serializer = self.get_serializer(files, many=True)
        return Response(serializer.data)

    # --- VERSIONING ACTIONS ---
    @action(detail=True, methods=['GET'])
    def versions(self, request, pk=None):
        file_obj = self.get_object()
        versions = file_obj.versions.all()
        serializer = FileVersionSerializer(versions, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['POST'])
    def upload_new_version(self, request, pk=None):
        file_obj = self.get_object()
        uploaded_file = request.FILES.get('file')
        comment = request.data.get('comment', '')

        if not uploaded_file:
            return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            next_version_num = file_obj.versions.count() + 1
            FileVersion.objects.create(
                file_record=file_obj,
                file=file_obj.file,
                version_number=next_version_num,
                size=file_obj.size,
                created_by=request.user,
                comment=f"Auto-saved before updating to newer version"
            )

            file_obj.file = uploaded_file
            file_obj.size = uploaded_file.size
            file_obj.save()

            from storage.tasks import generate_thumbnail_task, process_file_and_index
            generate_thumbnail_task.delay(str(file_obj.id))
            process_file_and_index.delay(str(file_obj.id))
            
            log_action(request.user, 'edit', target_object=file_obj, 
                       description=f"Upload versi baru v{next_version_num+1}: {file_obj.name}", request=request)

        return Response(self.get_serializer(file_obj).data)

    # --- CHUNKING ACTIONS ---
    @action(detail=False, methods=['POST'])
    def start_chunked_upload(self, request):
        filename = request.data.get('filename')
        total_chunks = request.data.get('total_chunks')
        total_size = request.data.get('total_size', 0)
        folder_id = request.data.get('folder')
        
        if not filename or not total_chunks:
            return Response({'error': 'filename and total_chunks are required'}, status=status.HTTP_400_BAD_REQUEST)

        target_folder = None
        if folder_id:
            target_folder = Folder.objects.filter(id=folder_id, owner=request.user).first()

        chunk_upload = FileChunk.objects.create(
            owner=request.user,
            filename=filename,
            total_chunks=int(total_chunks),
            total_size=int(total_size),
            folder=target_folder
        )
        return Response({'upload_id': chunk_upload.upload_id})

    @action(detail=False, methods=['POST'], url_path='upload_chunk/(?P<upload_id>[^/.]+)')
    def upload_chunk(self, request, upload_id=None):
        chunk_index = request.data.get('chunk_index')
        if chunk_index is None:
            return Response({'error': 'chunk_index is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        chunk_index = int(chunk_index)
        file_chunk = get_object_or_404(FileChunk, upload_id=upload_id, owner=request.user)
        
        uploaded_chunk = request.FILES.get('chunk')
        if not uploaded_chunk:
            return Response({'error': 'No chunk provided'}, status=status.HTTP_400_BAD_REQUEST)

        chunk_path = file_chunk.get_chunk_path(chunk_index)
        with open(chunk_path, 'wb+') as destination:
            for chunk in uploaded_chunk.chunks():
                destination.write(chunk)
        
        file_chunk.received_chunks += 1
        file_chunk.save()
        
        return Response({'status': 'Chunk uploaded', 'received_chunks': file_chunk.received_chunks})

    @action(detail=False, methods=['POST'], url_path='complete_chunked_upload/(?P<upload_id>[^/.]+)')
    def complete_chunked_upload(self, request, upload_id=None):
        file_chunk = get_object_or_404(FileChunk, upload_id=upload_id, owner=request.user)
        
        if file_chunk.received_chunks < file_chunk.total_chunks:
            return Response({'error': f'Not all chunks received ({file_chunk.received_chunks}/{file_chunk.total_chunks})'}, 
                            status=status.HTTP_400_BAD_REQUEST)

        final_temp_path = os.path.join('/tmp', f'assembled_{file_chunk.upload_id}')
        try:
            with open(final_temp_path, 'wb') as final_file:
                for i in range(file_chunk.total_chunks):
                    chunk_path = file_chunk.get_chunk_path(i)
                    if not os.path.exists(chunk_path):
                         return Response({'error': f'Missing chunk part {i}'}, status=status.HTTP_400_BAD_REQUEST)
                    with open(chunk_path, 'rb') as part:
                        final_file.write(part.read())
                    os.remove(chunk_path)

            from django.core.files import File as DjangoFile
            with open(final_temp_path, 'rb') as f:
                django_file = DjangoFile(f, name=file_chunk.filename)
                # upload_service needs .size
                django_file.size = os.path.getsize(final_temp_path)
                new_file = service_upload_file(request.user, django_file, file_chunk.folder)
            
            # ENTERPRISE: Buat Approval Request otomatis
            ApprovalRequest.objects.create(file=new_file, requester=request.user)
            log_action(request.user, 'upload', target_object=new_file, 
                       description=f"Upload file (chunked): {new_file.name}", request=request)

            chunk_dir = os.path.dirname(file_chunk.get_chunk_path(0))
            if os.path.exists(chunk_dir):
                shutil.rmtree(chunk_dir)
            file_chunk.delete()

            serializer = self.get_serializer(new_file)
            return Response(serializer.data)
        finally:
            if os.path.exists(final_temp_path):
                os.remove(final_temp_path)

class SharedLinkViewSet(viewsets.ModelViewSet):
    serializer_class = SharedLinkSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'share_id'

    def get_queryset(self):
        return SharedLink.objects.filter(creator=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        share = serializer.save(creator=self.request.user)
        log_action(self.request.user, 'share', target_object=share, 
                   description=f"Dibuat link share untuk {'File' if share.file else 'Folder'}", request=self.request)

class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = FileCommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        file_id = self.request.query_params.get('file_id')
        if file_id:
            return FileComment.objects.filter(file_id=file_id).order_by('created_at')
        return FileComment.objects.none()

    def perform_create(self, serializer):
        comment = serializer.save(author=self.request.user)
        log_action(self.request.user, 'view', target_object=comment.file, 
                   description=f"Menambahkan komentar: {comment.content[:20]}", request=self.request)

class ApprovalViewSet(viewsets.ModelViewSet):
    serializer_class = ApprovalRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Admin bisa melihat semua, user biasa hanya yang mereka minta
        if self.request.user.is_staff:
            return ApprovalRequest.objects.all().order_by('-requested_at')
        return ApprovalRequest.objects.filter(requester=self.request.user).order_by('-requested_at')

    @action(detail=True, methods=['POST'], permission_classes=[IsAdminUser])
    def approve(self, request, pk=None):
        approval = self.get_object()
        approval.status = 'approved'
        approval.approver = request.user
        approval.reviewed_at = timezone.now()
        approval.note = request.data.get('note', '')
        approval.save()
        
        log_action(request.user, 'approval', target_object=approval.file, 
                   description=f"Menyetujui file: {approval.file.name}", request=request)
        return Response({'status': 'Approved'})

    @action(detail=True, methods=['POST'], permission_classes=[IsAdminUser])
    def reject(self, request, pk=None):
        approval = self.get_object()
        approval.status = 'rejected'
        approval.approver = request.user
        approval.reviewed_at = timezone.now()
        approval.note = request.data.get('note', '')
        approval.save()
        
        log_action(request.user, 'approval', target_object=approval.file, 
                   description=f"Menolak file: {approval.file.name}", request=request)
        return Response({'status': 'Rejected'})

class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AuditLogSerializer
    permission_classes = [IsAdminUser] # Hanya Admin yang bisa melihat log audit

    def get_queryset(self):
        return AuditLog.objects.all().order_by('-created_at')
