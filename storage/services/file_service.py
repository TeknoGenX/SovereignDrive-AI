from storage.services.encryption import decrypt_file_data


def get_decrypted_file(file_obj):
    file_obj.file.seek(0)
    encrypted_data = file_obj.file.read()

    try:
        return decrypt_file_data(encrypted_data)
    except Exception:
        return encrypted_data


def soft_delete_file(file_obj):
    file_obj.is_trashed = True
    file_obj.save()


def restore_file(file_obj):
    file_obj.is_trashed = False
    file_obj.save()


def hard_delete_file(file_obj, profile):
    size = file_obj.size or 0

    profile.storage_used = max(0, profile.storage_used - size)
    profile.save()

    file_obj.delete()