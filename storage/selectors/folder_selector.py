from storage.models import Folder


def get_folder(folder_id):
    return Folder.objects.filter(id=folder_id, is_trashed=False).first()