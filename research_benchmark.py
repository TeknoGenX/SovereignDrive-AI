import os
import time
import io
import sys

# Mock settings for encryption
class MockSettings:
    SECRET_KEY = 'benchmark-secret-key-12345'
    ENCRYPTION_KEY = 'benchmark-secret-key-12345'

sys.modules['django.conf'] = type('obj', (object,), {'settings': MockSettings})

from storage.services.encryption import encrypt_file_data, encrypt_stream

def benchmark_encryption(sizes_mb):
    print(f"{'Ukuran File':<15} | {'Enkripsi Blok (detik)':<25} | {'Enkripsi Streaming (detik)':<30}")
    print("-" * 75)
    
    for size in sizes_mb:
        data = os.urandom(size * 1024 * 1024)
        
        # Benchmark Block Encryption
        start = time.time()
        _ = encrypt_file_data(data)
        block_time = time.time() - start
        
        # Benchmark Stream Encryption
        input_stream = io.BytesIO(data)
        start = time.time()
        for _ in encrypt_stream(input_stream):
            pass
        stream_time = time.time() - start
        
        print(f"{size:>2} MB {'':<10} | {block_time:>20.4f} {'':<4} | {stream_time:>25.4f}")

if __name__ == "__main__":
    sizes = [1, 10, 50, 100] # MB
    print("Memulai Benchmark Keamanan Proyek Awan...\n")
    benchmark_encryption(sizes)
