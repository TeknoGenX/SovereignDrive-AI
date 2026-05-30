# Panduan Penempatan Ilustrasi Visual Buku SovereignDrive AI

Dokumen ini menjelaskan posisi tepat (Bab dan Poin/Sub-bab) di mana gambar atau screenshot harus disisipkan.

---

## Bab 0: Dunia Open Source dan Keajaiban Ubuntu

1.  **Gambar 0.1: Logo Open Source & Ubuntu**
    *   **Posisi:** Setelah paragraf pertama di **Sub-bab 0.1 (Gerakan Open Source)**.
    *   *Keterangan:* Simbol kolaborasi global dan filosofi "Kemanusiaan untuk Sesama".
2.  **Gambar 0.2: Interface Ubuntu Desktop vs CLI**
    *   **Posisi:** Di tengah **Sub-bab 0.2.1 (Ubuntu Desktop vs Ubuntu Server)**.
    *   *Keterangan:* Tampilan GUI yang ramah pengguna (kiri) dibandingkan terminal Ubuntu Server yang efisien (kanan).
3.  **Gambar 0.3: Ilustrasi Perangkat Keras**
    *   **Posisi:** Di akhir **Sub-bab 0.3 (Dukungan Perangkat Keras)**.
    *   *Keterangan:* Ubuntu dapat berjalan di berbagai perangkat, dari laptop lama hingga Raspberry Pi.

## Bab 1: Pondasi & Filosofi

1.  **Gambar 1.1: Diagram Arsitektur SovereignDrive**
    *   **Posisi:** Sebelum **Sub-bab 1.2.1 (Komponen Utama & Interaksinya)**.
    *   *Keterangan:* Alur data dari Browser ke Django, Redis, hingga ke AI Engine.
2.  **Gambar 1.2: Proses Instalasi Docker di Ubuntu**
    *   **Posisi:** Di bawah instruksi instalasi di **Sub-bab 1.3.1 (Modern Tooling)**.
    *   *Keterangan:* Tampilan terminal saat mengunduh dan memasang paket Docker.
3.  **Gambar 1.3: Dashboard Docker Desktop / Portainer**
    *   **Posisi:** Setelah file YAML di **Sub-bab 1.3.2 (Docker: Kontainerisasi)**.
    *   *Keterangan:* Status kontainer PostgreSQL, Redis, dan Elasticsearch yang sudah berjalan.

## Bab 2: Arsitektur Database & Hirarki Folder

1.  **Gambar 2.1: Skema Database (ERD)**
    *   **Posisi:** Sebelum penjelasan kelebihan di **Sub-bab 2.1.1 (Adjacency List)**.
    *   *Keterangan:* Hubungan antara tabel User, Folder, dan File (One-to-Many).
2.  **Gambar 2.2: Ilustrasi Struktur Folder Rekursif**
    *   **Posisi:** Setelah poin solusi di **Sub-bab 2.1.2 (Tantangan: Full Path)**.
    *   *Keterangan:* Visualisasi pohon (Tree) bagaimana folder bersarang di dalam database.

## Bab 3: Kriptografi: Mengunci Gerbang Data

1.  **Gambar 3.1: Diagram Alur Enkripsi AES-256 GCM**
    *   **Posisi:** Setelah poin keunggulan GCM di **Sub-bab 3.1.2**.
    *   *Keterangan:* Proses pengamanan file menggunakan Kunci Master, Nonce, dan Tag Autentikasi.
2.  **Gambar 3.2: Perbandingan File Asli vs File Terenkripsi**
    *   **Posisi:** Di tengah **Sub-bab 3.3.2 (Bedah Struktur Byte di Disk)**.
    *   *Keterangan:* Tampilan teks asli yang bisa dibaca vs format biner .enc yang terenkripsi.

## Bab 4: Brain-Circuit: AI Indexing & OCR

1.  **Gambar 4.1: Proses OCR Tesseract**
    *   **Posisi:** Sebelum daftar teknik pre-processing di **Sub-bab 4.1.2**.
    *   *Keterangan:* Contoh gambar dokumen (nota/PDF scan) dan teks hasil ekstraksi AI.
2.  **Gambar 4.2: Terminal Log saat AI Bekerja**
    *   **Posisi:** Setelah potongan kode di **Sub-bab 4.3.1**.
    *   *Keterangan:* Log Celery Worker yang menunjukkan proses OCR sedang berjalan di latar belakang.

## Bab 5: Elasticsearch: Pencarian Secepat Kilat

1.  **Gambar 5.1: Visualisasi Inverted Index**
    *   **Posisi:** Setelah tabel contoh di **Sub-bab 5.1.1**.
    *   *Keterangan:* Cara Elasticsearch memetakan kata kunci ke ID dokumen secara instan.
2.  **Gambar 5.2: Tampilan Dashboard Kibana / Hasil Pencarian**
    *   **Posisi:** Setelah blok query di **Sub-bab 5.3.1**.
    *   *Keterangan:* Hasil pencarian cerdas yang memprioritaskan nama file (boosting).

## Bab 6: Celery: Pekerja di Balik Layar

1.  **Gambar 6.1: Diagram Alur Kerja Asinkron**
    *   **Posisi:** Sebelum **Sub-bab 6.2 (Engineering Best Practices)**.
    *   *Keterangan:* Urutan interaksi antara Django, Redis Broker, dan Celery Worker.
2.  **Gambar 6.2: Dashboard Flower (Monitoring)**
    *   **Posisi:** Di akhir **Sub-bab 6.4 (Observability)**.
    *   *Keterangan:* Grafik statistik tugas yang sukses, gagal, dan sedang diproses.

## Bab 7: Integrasi Bot Telegram & API

1.  **Gambar 7.1: Screenshot Chat Bot Telegram**
    *   **Posisi:** Di tengah **Sub-bab 7.1.1 (Visualisasi Alur Data)**.
    *   *Keterangan:* Pengguna mengirim file ke bot dan menerima pesan konfirmasi "Proses Berhasil".
2.  **Gambar 7.2: Interface Link Berbagi (Shared Link)**
    *   **Posisi:** Setelah poin ke-3 di **Sub-bab 7.2.2**.
    *   *Keterangan:* Halaman unduhan publik yang dilindungi kata sandi (Password Protected).

## Bab 8: Menghadapi Dunia Nyata (Production)

1.  **Gambar 8.1: Topologi Nginx + Gunicorn**
    *   **Posisi:** Di tengah **Sub-bab 8.2.2 (Reverse Proxy)**.
    *   *Keterangan:* Nginx berdiri di gardu depan melindungi server aplikasi Django.
2.  **Gambar 8.2: Dashboard Monitoring Sentry**
    *   **Posisi:** Setelah poin Sentry di **Sub-bab 8.5**.
    *   *Keterangan:* Tampilan laporan error dan statistik kesehatan aplikasi di produksi.

## Bab 9: Mobilisasi Data (Android)

1.  **Gambar 9.1: Screenshot Aplikasi Android SovereignDrive**
    *   **Posisi:** Sebelum **Sub-bab 9.4 (Fitur Mobile)**.
    *   *Keterangan:* Tampilan modern daftar file dan folder pada perangkat smartphone.
2.  **Gambar 9.2: Proses Kamera ke Cloud**
    *   **Posisi:** Di akhir **Sub-bab 9.4.1**.
    *   *Keterangan:* Visualisasi saat foto kamera HP langsung diunggah ke cloud pribadi.

## Bab 10: Testing & Security Audit

1.  **Gambar 10.1: Laporan Pytest (Green Line)**
    *   **Posisi:** Setelah penjelasan Fixtures di **Sub-bab 10.1.1**.
    *   *Keterangan:* Konsol terminal menunjukkan status "PASSED" untuk seluruh pengujian keamanan.
2.  **Gambar 10.2: Roadmap Teknologi Masa Depan**
    *   **Posisi:** Di akhir **Sub-bab 10.7.4**, sebelum kalimat Penutup.
    *   *Keterangan:* Ikon Kubernetes, Cloud Native, dan AI untuk perjalanan belajar selanjutnya.
