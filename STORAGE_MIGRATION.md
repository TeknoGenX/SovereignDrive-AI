# 📂 Panduan Migrasi Penyimpanan ke Flashdisk 2TB (AwanDrive X)

Dokumen ini menjelaskan langkah-langkah teknis untuk memindahkan lokasi penyimpanan file utama (folder `media`) dari penyimpanan internal server ke unit eksternal seperti Flashdisk atau SSD 2TB.

---

## 1. Persiapan Perangkat (Mounting)
Langkah pertama adalah memastikan Flashdisk terdeteksi dan terpasang (*mounted*) secara permanen di sistem Linux Anda.

1.  **Identifikasi Lokasi Flashdisk:**
    Masukkan flashdisk, lalu jalankan:
    ```bash
    lsblk
    ```
    Cari perangkat Anda (misal: `/dev/sdb1`).

2.  **Buat Titik Kait (Mount Point):**
    ```bash
    sudo mkdir -p /mnt/awandrive
    ```

3.  **Format (Opsional):**
    Jika flashdisk masih baru, format ke sistem file Linux (ext4) agar mendukung perizinan file (*file permissions*) dengan baik:
    ```bash
    sudo mkfs.ext4 /dev/sdb1
    ```

4.  **Mount Permanen via `/etc/fstab`:**
    Dapatkan UUID flashdisk:
    ```bash
    sudo blkid /dev/sdb1
    ```
    Tambahkan baris berikut ke file `/etc/fstab` agar otomatis terpasang saat restart:
    ```text
    UUID=nomor-uuid-anda /mnt/awandrive ext4 defaults 0 2
    ```
    Lalu jalankan `sudo mount -a`.

---

## 2. Migrasi Data Lama
Pindahkan file yang sudah ada dari folder `media` internal ke flashdisk.

1.  **Hentikan Layanan:**
    Matikan Django dan Celery untuk memastikan tidak ada file yang sedang ditulis.

2.  **Salin Data dengan Presisi:**
    Gunakan `rsync` untuk menjaga struktur folder dan hak akses:
    ```bash
    sudo rsync -avzh /home/andi-liani/code/awan/media/ /mnt/awandrive/
    ```

3.  **Atur Hak Akses:**
    Pastikan user Anda memiliki akses penuh ke folder tersebut:
    ```bash
    sudo chown -R andi-liani:andi-liani /mnt/awandrive
    sudo chmod -R 755 /mnt/awandrive
    ```

---

## 3. Konfigurasi Django (`core/settings.py`)
Ubah jalur penyimpanan di dalam aplikasi Django Anda agar mengarah ke flashdisk.

Buka `core/settings.py` dan cari bagian `MEDIA_ROOT`, lalu ubah menjadi:

```python
# core/settings.py

# Lokasi lama: MEDIA_ROOT = BASE_DIR / "media"
# Lokasi baru (Flashdisk):
MEDIA_ROOT = "/mnt/awandrive"

# MEDIA_URL tetap sama
MEDIA_URL = "/media/"
```

---

## 4. Penyesuaian Infrastruktur (Docker)
Jika Anda menggunakan Docker untuk melayani file media (misal via Nginx atau jika app di-docker-kan), Anda perlu memperbarui `volumes` di `docker-compose.yml`:

```yaml
services:
  web:
    # ...
    volumes:
      - /mnt/awandrive:/home/andi-liani/code/awan/media
```

---

## 5. Verifikasi & Pengujian
1.  **Jalankan Kembali Layanan:**
    Mulai kembali Django dan Celery menggunakan `./run_services.sh`.
2.  **Cek Dashboard:**
    Pastikan thumbnail file lama tetap muncul.
3.  **Uji Unggah:**
    Unggah file baru seukuran >10MB dan pastikan file tersebut masuk ke `/mnt/awandrive/user_X/`.
4.  **Cek Sisa Ruang:**
    Jalankan `df -h /mnt/awandrive` untuk memastikan sistem mendeteksi kapasitas 2TB tersebut.

---

## ⚠️ Catatan Penting:
*   **Stabilitas USB:** Pastikan Flashdisk tidak sering dicabut-pasang. Penggunaan port USB 3.0 sangat disarankan untuk kecepatan transfer data.
*   **Backup Metadata:** Meskipun file ada di Flashdisk, metadata (nama file, relasi folder) tetap ada di database **PostgreSQL**. Pastikan database tetap rutin dibackup.
*   **Simlink (Alternatif):** Jika Anda tidak ingin mengubah `settings.py`, Anda bisa menggunakan *symbolic link*:
    ```bash
    ln -s /mnt/awandrive /home/andi-liani/code/awan/media
    ```
