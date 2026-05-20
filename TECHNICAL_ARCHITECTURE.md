# 🏛️ Arsitektur Sistem: SovereignDrive AI

Dokumen ini menjelaskan desain teknis, pola arsitektur, dan aliran data dalam sistem **SovereignDrive AI**.

## 1. Pola Desain (Clean Architecture)
SovereignDrive AI meninggalkan pola "Fat Models/Views" tradisional Django dan mengadopsi pemisahan logika yang lebih bersih:

*   **Selectors (`storage/selectors/`):** Bertanggung jawab atas semua query pembacaan data (Read).
    *   *Contoh:* `get_file_access_role` menggunakan strategi *Memory Lookup* untuk memproses izin folder berjenjang secara efisien.
*   **Services (`storage/services/`):** Bertanggung jawab atas mutasi data (Write/Update/Delete) dan logika bisnis berat.
    *   *Contoh:* `encryption.py` untuk streaming AES-256 GCM dan `audit_service.py` untuk pencatatan jejak audit.
*   **Models:** Hanya sebagai representasi skema database dan properti sederhana.

## 2. Struktur Database Polimorfik (Audit Log)
Sistem menggunakan **Django ContentTypes Framework** untuk mencatat jejak audit.
*   **GenericForeignKey:** Memungkinkan model `AuditLog` merujuk ke model apa pun (File, Folder, SharedLink) tanpa perlu membuat banyak tabel perantara.
*   **Benefit:** Mempermudah pembuatan laporan aktivitas sistem yang terkonsolidasi dalam satu tampilan tabel tunggal.

## 3. Aliran Data & Enkripsi (Storage Pipeline)
1.  **Upload:** File diterima dalam bentuk *Chunks* -> Didekripsi -> Dienkripsi ulang dengan AES-256 GCM -> Disimpan ke Disk.
2.  **DLP (Data Loss Prevention) Engine:**
    *   Selama proses unduhan PDF, sistem menggunakan `dlp_service.py` (PyMuPDF) untuk menyuntikkan watermark dinamis.
    *   Watermark bersifat forensik, menyertakan metadata pengguna (Nama, Email) dan timestamp untuk pelacakan kebocoran data.
3.  **Background Processing (Celery):**
    *   File tidak dibaca seluruhnya ke RAM, melainkan menggunakan `tempfile` (Disk Buffer).
    *   **OCR Engine:** Tesseract mengekstrak teks dari gambar/PDF.
    *   **NLP Processor:** NLTK membersihkan teks (Stopwords removal & Stemming).
4.  **Indexing:** Teks yang sudah bersih dikirim ke **Elasticsearch** dengan *Indonesian Analyzer*.

## 4. Integrasi Identitas Korporat (SSO/IAM)
Sistem mendukung integrasi dengan penyedia identitas eksternal menggunakan protokol modern:
*   **OpenID Connect (OIDC) & OAuth2:** Terintegrasi via `social-auth-app-django`.
*   **Pipeline Authentication:** Pengguna dari Azure AD atau Google Workspace dipetakan secara otomatis ke model User lokal, memungkinkan sinkronisasi profil tanpa pendaftaran manual.
*   **Role Mapping:** Mendukung pemetaan grup AD ke tingkat izin akses di dalam SovereignDrive AI.

## 5. Strategi Pencarian AI
Pencarian dilakukan melalui Elasticsearch dengan parameter:
*   **Multi-match Query:** Mencari di field `name` dan `extracted_text`.
*   **Field Boosting:** Nama file memiliki bobot 3x lebih besar (`name^3`) daripada isi konten.
*   **Fuzzy Search:** Toleransi kesalahan pengetikan hingga 2 karakter.
*   **Scoring Preservation:** Django ORM menggunakan `Case/When` untuk memastikan urutan hasil di UI sama persis dengan skor relevansi Elasticsearch.

## 6. Infrastruktur (Containerization)
Sistem dijalankan menggunakan **Docker Compose** dengan komponen:
*   **PostgreSQL 16:** Penyimpanan metadata relasional.
*   **Redis:** Broker pesan Celery dan cache kursor real-time.
*   **Elasticsearch 7.17:** Mesin pencari AI konten.
*   **Daphne (ASGI):** Mendukung komunikasi dua arah via WebSockets.

---
*Dokumentasi ini dibuat untuk memastikan transparansi arsitektur bagi pengembang dan auditor keamanan.*
