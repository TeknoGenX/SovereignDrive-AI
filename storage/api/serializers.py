# /home/andi-liani/code/awan/storage/api/serializers.py

from rest_framework import serializers
from storage.models import (
    Folder, File, SharedLink, FileVersion, FileComment, 
    ApprovalRequest, AuditLog
)
from django.contrib.auth.models import User

class UserSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']

class FolderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Folder
        fields = ['id', 'name', 'parent', 'created_at']
        read_only_fields = ['id', 'created_at']

class FileSerializer(serializers.ModelSerializer):
    size_formatted = serializers.SerializerMethodField()
    approval_status = serializers.CharField(source='approval.status', read_only=True)

    class Meta:
        model = File
        fields = [
            'id', 'name', 'file', 'folder', 'size', 'size_formatted', 
            'is_public', 'extracted_text', 'created_at', 'approval_status'
        ]
        read_only_fields = ['id', 'size', 'extracted_text', 'created_at']

    def get_size_formatted(self, obj):
        if obj.size >= 1024 * 1024:
            return f"{obj.size / (1024 * 1024):.2f} MB"
        return f"{obj.size / 1024:.2f} KB"

class SharedLinkSerializer(serializers.ModelSerializer):
    set_password = serializers.CharField(write_only=True, required=False)
    target_name = serializers.SerializerMethodField()
    share_url = serializers.SerializerMethodField()

    class Meta:
        model = SharedLink
        fields = [
            'share_id', 'file', 'folder', 'target_name', 'role', 
            'expiry_date', 'view_count', 'is_active', 'share_url', 'set_password'
        ]
        read_only_fields = ['share_id', 'view_count', 'share_url']

    def get_target_name(self, obj):
        return obj.file.name if obj.file else obj.folder.name

    def get_share_url(self, obj):
        return f"/s/{obj.share_id}/"

    def create(self, validated_data):
        password = validated_data.pop('set_password', None)
        instance = super().create(validated_data)
        if password:
            instance.set_password(password)
            instance.save()
        return instance

class FileVersionSerializer(serializers.ModelSerializer):
    created_by = UserSimpleSerializer(read_only=True)

    class Meta:
        model = FileVersion
        fields = ['id', 'version_number', 'file', 'size', 'created_by', 'created_at', 'comment']

class FileCommentSerializer(serializers.ModelSerializer):
    author = UserSimpleSerializer(read_only=True)
    replies_count = serializers.IntegerField(source='replies.count', read_only=True)

    class Meta:
        model = FileComment
        fields = ['id', 'file', 'author', 'content', 'parent', 'replies_count', 'created_at', 'mentions']
        read_only_fields = ['id', 'author', 'created_at']

class ApprovalRequestSerializer(serializers.ModelSerializer):
    requester = UserSimpleSerializer(read_only=True)
    file_name = serializers.CharField(source='file.name', read_only=True)

    class Meta:
        model = ApprovalRequest
        fields = ['id', 'file', 'file_name', 'requester', 'approver', 'status', 'note', 'requested_at', 'reviewed_at']
        read_only_fields = ['id', 'requester', 'requested_at', 'reviewed_at']

class AuditLogSerializer(serializers.ModelSerializer):
    user = UserSimpleSerializer(read_only=True)
    target_type = serializers.CharField(read_only=True) # Menggunakan property target_type

    class Meta:
        model = AuditLog
        fields = [
            'id', 'user', 'action', 'target_id', 'target_type', 
            'description', 'ip_address', 'user_agent', 'created_at'
        ]
