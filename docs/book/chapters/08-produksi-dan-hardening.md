# Bab 8: Menghadapi Dunia Nyata (Production Readiness)

## Cerita Di Balik Layar
Aplikasi Anda berjalan sempurna di laptop lokal. Tidak ada *error*, semua mulus. Namun, ketika Anda memindahkannya ke server produksi (VPS atau Cloud), aplikasi Anda tiba-tiba crash saat diakses 100 orang bersamaan, disk server penuh dalam seminggu, dan *hacker* iseng berhasil melihat *source code* Anda hanya karena konfigurasi kecil yang terlupakan.

Dunia lokal dan produksi adalah dua dimensi yang berbeda. Bab ini adalah pedoman militer untuk mengeraskan (*hardening*) SovereignDrive AI agar tahan banting dari serangan siber, kehabisan memori, dan penyimpangan data di lingkungan yang keras.

---

## 8.1. Keamanan Berlapis (Defense in Depth)

Jangan pernah mengandalkan satu lapis keamanan. Di produksi, kita harus mengunci setiap pintu masuk.

### 8.1.1. Environment Hardening
Gunakan `python-decouple` untuk memisahkan rahasia dari kode.
- **Kunci Rahasia**: Pastikan `SECRET_KEY` di produksi berbeda dari lokal dan memiliki entropi tinggi.
- **Allowed Hosts**: Jangan gunakan `['*']`. Batasi hanya pada domain Anda (misal: `['cloud.pribadi.com']`) untuk mencegah serangan *Host Header Injection*.

### 8.1.2. Keamanan Cookie & Sesi
Tambahkan pengaturan berikut di `settings.py` untuk melindungi sesi user:
```python
SESSION_COOKIE_SECURE = True  # Cookie hanya dikirim via HTTPS
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000 # Paksa browser gunakan HTTPS selama 1 tahun
SECURE_CONTENT_TYPE_NOSNIFF = True # Mencegah MIME sniffing
```

---

## 8.2. Optimasi Infrastruktur & Web Server

Django tidak berjalan sendiri di produksi. Ia membutuhkan pelayan yang kuat.

### 8.2.1. Gunicorn & Worker Model
Kita menggunakan **Gunicorn** sebagai WSGI HTTP Server. Untuk performa maksimal, gunakan rumus worker: `(2 x Jumlah Core CPU) + 1`.
Jika server Anda punya 2 Core, jalankan Gunicorn dengan 5 worker:
`gunicorn core.wsgi:application --workers 5 --bind 0.0.0.0:8000`

### 8.2.2. Reverse Proxy dengan Nginx
Jangan biarkan Gunicorn terekspos langsung ke internet. Gunakan **Nginx** sebagai tameng depan (Reverse Proxy).
- **Fungsi Nginx**: Terminasi SSL (HTTPS), pembatasan ukuran upload (`client_max_body_size`), dan pembatasan frekuensi akses (*Rate Limiting*) untuk mencegah DDoS.

---

## 8.3. Efisiensi Skala Besar: Pencegahan Kebocoran Disk

Fitur "Download as ZIP" memproses banyak file sementara (`tempfile`) di sistem. Jika terjadi error di tengah jalan, file sisa ini akan menumpuk di folder `/tmp` Linux hingga server mati.

### 8.3.1. Bedah Kode: `CleanupFileResponse`
SovereignDrive menggunakan teknik kustom untuk menjamin pembersihan file:

```python
from django.http import FileResponse
import os

class CleanupFileResponse(FileResponse):
    """
    Wrapper FileResponse yang otomatis menghapus file di disk 
    setelah streaming selesai dikirim ke browser.
    """
    def __init__(self, *args, **kwargs):
        self._file_to_cleanup = kwargs.pop('file_to_cleanup', None)
        super().__init__(*args, **kwargs)

    def close(self):
        super().close()
        if self._file_to_cleanup and os.path.exists(self._file_to_cleanup):
            os.remove(self._file_to_cleanup)
```
Dengan kelas ini, kita memberikan garansi bahwa disk server tetap bersih meskipun koneksi internet user terputus saat mengunduh.

---

## 8.4. Audit & Integritas Data Jangka Panjang

### 8.4.1. Audit Logging Asinkron
Sistem level korporat harus mencatat setiap klik dan unduh. Kita menggunakan Celery untuk mencatat log ini agar tidak memperlambat responsivitas UI bagi pengguna.

### 8.4.2. Management Command: `audit_quota`
Data kuota penyimpanan di database bisa menyimpang dari realita file di disk (misal: karena server mati mendadak). SovereignDrive memiliki perintah CLI untuk kalibrasi ulang:
`python manage.py audit_quota --fix`

---

## 8.5. Monitoring & Observability

Anda tidak bisa memperbaiki apa yang tidak Anda lihat.
- **Sentry**: Integrasikan Sentry untuk menangkap setiap *error* Python secara *real-time* sebelum user melaporkannya.
- **Prometheus & Grafana**: Gunakan untuk memantau penggunaan RAM, CPU, dan kesehatan database PostgreSQL.

---

## 8.6. Common Pitfalls (Lubang Jebakan)

1.  **Leaving DEBUG=True**: Ini adalah kesalahan nomor satu. Peretas bisa melihat konfigurasi database Anda dari halaman error Django.
2.  **Insecure Media Folder**: Folder `media/` seringkali bisa diakses langsung lewat URL tanpa pengecekan login. SovereignDrive memproteksi ini dengan mengarahkan unduhan melalui *Internal Redirect* (X-Accel-Redirect) di Nginx.
3.  **No Database Backups**: Enkripsi terkuat sekalipun tidak berguna jika hardisk server rusak. Gunakan `pg_dump` secara otomatis setiap malam dan simpan hasilnya di lokasi fisik yang berbeda.

---

## ✅ Engineering Checkpoint: Production Hardening
Sebelum melepas aplikasi ke pengguna nyata, pastikan benteng pertahanan Anda sudah terkunci rapat:
- [ ] **Security Headers:** Apakah HSTS dan Secure Cookies sudah aktif di `settings.py`?
- [ ] **Reverse Proxy:** Apakah Nginx sudah dikonfigurasi sebagai tameng depan dan menangani terminasi SSL?
- [ ] **Disk Hygiene:** Apakah seluruh unduhan file dinamis (ZIP) sudah menggunakan `CleanupFileResponse`?
- [ ] **Database Agility:** Apakah koneksi database menggunakan *Connection Pooling* (seperti `django-db-geventpool` atau PGBouncer)?
- [ ] **Audit Trail:** Apakah setiap tindakan administratif dicatat secara asinkron via Celery?
- [ ] **Disaster Recovery:** Apakah Anda sudah memiliki skrip backup database otomatis yang sudah diuji proses *restore*-nya?
- [ ] **Observability:** Apakah Sentry sudah aktif untuk memantau error di sisi server secara *real-time*?
