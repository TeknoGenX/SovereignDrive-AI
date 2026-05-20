from storage.models import FileAccess, FolderAccess


def get_file_access_role(file_obj, user):
    if file_obj.owner == user:
        return 'editor'

    access = FileAccess.objects.filter(file=file_obj, user=user).first()
    if access:
        return access.role

    if file_obj.folder:
        folder_access = FolderAccess.objects.filter(
            folder=file_obj.folder,
            user=user
        ).first()

        if folder_access:
            return folder_access.role

    return None