# 📂 Panduan Migrasi Penyimpanan Eksternal (SovereignDrive AI)

Dokumen ini menjelaskan langkah-langkah teknis untuk memindahkan lokasi penyimpanan file utama (folder `media`) dari penyimpanan internal server ke unit eksternal seperti SSD/Flashdisk 2TB.

---

## 1. Persiapan Perangkat (Mounting)
Langkah pertama adalah memastikan media penyimpanan terdeteksi dan terpasang (*mounted*) secara permanen di sistem Linux Anda.

1.  **Identifikasi Lokasi Disk:**
    Jalankan: `lsblk` -> Cari perangkat Anda (misal: `/dev/sdb1`).

2.  **Buat Titik Kait (Mount Point):**
    ```bash
    sudo mkdir -p /mnt/sovereigndrive
    ```

3.  **Mount Permanen via `/etc/fstab`:**
    Tambahkan baris berikut ke file `/etc/fstab` menggunakan UUID disk Anda:
    ```text
    UUID=nomor-uuid-anda /mnt/sovereigndrive ext4 defaults 0 2
    ```
    Lalu jalankan `sudo mount -a`.

---

## 2. Migrasi Data
Pindahkan file yang sudah ada dari folder `media` internal ke disk eksternal.

1.  **Hentikan Layanan:** Matikan Django dan Celery.
2.  **Salin Data:**
    ```bash
    sudo rsync -avzh /home/andi-liani/code/python_django/awan1/media/ /mnt/sovereigndrive/
    ```
3.  **Atur Hak Akses:**
    ```bash
    sudo chown -R $USER:$USER /mnt/sovereigndrive
    sudo chmod -R 755 /mnt/sovereigndrive
    ```

---

## 3. Konfigurasi Lingkungan (`.env`)
Ubah jalur penyimpanan di file konfigurasi utama Anda.

Buka file `.env` (atau `core/settings.py` jika tidak menggunakan .env untuk path) dan sesuaikan:
```python
MEDIA_ROOT = "/mnt/sovereigndrive"
```

---

## 4. Penyesuaian Docker
Jika menjalankan aplikasi di dalam kontainer, perbarui bagian `volumes` di `docker-compose.yml`:
```yaml
services:
  web:
    volumes:
      - /mnt/sovereigndrive:/app/media
```

---

## ⚠️ Catatan Penting:
*   **Backup Metadata:** Meskipun file fisik ada di disk eksternal, metadata tetap tersimpan di database **PostgreSQL**. Lakukan backup database secara rutin.
*   **Keamanan:** Disk eksternal tetap terlindungi oleh enkripsi **AES-256** SovereignDrive AI di level aplikasi. Namun, disarankan juga untuk mengenkripsi disk di level OS menggunakan LUKS untuk keamanan fisik total.
