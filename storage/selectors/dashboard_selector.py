from storage.models import Folder, File


def get_dashboard_data(user, folder=None):
    if folder:
        folders = Folder.objects.select_related('parent').filter(
            parent=folder, is_trashed=False
        )

        files = File.objects.select_related('folder').filter(
            folder=folder, is_trashed=False
        )
    else:
        folders = Folder.objects.filter(
            owner=user, parent=None, is_trashed=False
        )

        files = File.objects.filter(
            owner=user, folder=None, is_trashed=False
        )

    return folders, files