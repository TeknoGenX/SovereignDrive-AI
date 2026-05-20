import base64
import hashlib
import struct
import os
from django.conf import settings
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

STREAM_MAGIC_HEADER = b'AWAN_AESGCM\x00'

def get_fernet_instance():
    raw_key = getattr(settings, 'ENCRYPTION_KEY', getattr(settings, 'SECRET_KEY'))
    key_bytes = hashlib.sha256(raw_key.encode('utf-8')).digest()
    fernet_key = base64.urlsafe_b64encode(key_bytes)
    return Fernet(fernet_key)

def get_aesgcm_key():
    raw_key = getattr(settings, 'ENCRYPTION_KEY', getattr(settings, 'SECRET_KEY'))
    return hashlib.sha256(raw_key.encode('utf-8')).digest()

def encrypt_file_data(raw_data: bytes) -> bytes:
    try:
        fernet = get_fernet_instance()
        return fernet.encrypt(raw_data)
    except Exception as e:
        print(f"Error saat mengenkripsi file: {e}")
        raise Exception("Proses enkripsi gagal.")

def decrypt_file_data(encrypted_data: bytes) -> bytes:
    if encrypted_data.startswith(STREAM_MAGIC_HEADER):
        raise ValueError("Gunakan decrypt_stream untuk file AES-GCM.")
    try:
        fernet = get_fernet_instance()
        return fernet.decrypt(encrypted_data)
    except InvalidToken:
        raise ValueError("Data tidak dapat didekripsi. Token tidak valid atau file tidak terenkripsi.")
    except Exception as e:
        print(f"Error saat mendekripsi file: {e}")
        raise Exception("Proses dekripsi gagal.")

def encrypt_stream(input_stream, chunk_size=64*1024):
    key = get_aesgcm_key()
    aesgcm = AESGCM(key)
    yield STREAM_MAGIC_HEADER
    while True:
        chunk = input_stream.read(chunk_size)
        if not chunk:
            break
        nonce = os.urandom(12)
        encrypted_chunk = aesgcm.encrypt(nonce, chunk, None)
        yield struct.pack('<I', len(encrypted_chunk)) + nonce + encrypted_chunk

def decrypt_stream(input_stream):
    header = input_stream.read(12)
    if header != STREAM_MAGIC_HEADER:
        input_stream.seek(0)
        raw_data = input_stream.read()
        try:
            yield decrypt_file_data(raw_data)
        except Exception:
            yield raw_data
        return

    key = get_aesgcm_key()
    aesgcm = AESGCM(key)
    while True:
        len_bytes = input_stream.read(4)
        if not len_bytes or len(len_bytes) < 4:
            break
        chunk_len = struct.unpack('<I', len_bytes)[0]
        
        nonce = input_stream.read(12)
        if len(nonce) < 12: break
        
        encrypted_chunk = input_stream.read(chunk_len)
        if len(encrypted_chunk) < chunk_len: break
        
        try:
            decrypted_chunk = aesgcm.decrypt(nonce, encrypted_chunk, None)
            yield decrypted_chunk
        except Exception as e:
            print(f"Error dekripsi chunk: {e}")
            break