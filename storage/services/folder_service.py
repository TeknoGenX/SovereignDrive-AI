from storage.models import Folder


def create_folder(user, name, parent=None):
    return Folder.objects.create(
        name=name,
        parent=parent,
        owner=user
    )


def soft_delete_folder(folder):
    folder.is_trashed = True
    folder.save()


def restore_folder(folder):
    folder.is_trashed = False
    folder.save()