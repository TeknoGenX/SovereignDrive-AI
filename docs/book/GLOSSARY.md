# Glosarium Istilah Teknik: SovereignDrive AI (Edisi Lengkap)

Glosarium ini disusun untuk membantu Anda memahami istilah-istilah teknis kelas atas yang digunakan di sepanjang buku ini. Istilah-istilah ini mencakup domain Kriptografi, Kecerdasan Buatan, Infrastruktur, dan Software Engineering.

---

## 🔐 Kriptografi & Keamanan

### **AES-256 GCM (Galois/Counter Mode)**
Standar enkripsi simetris yang menyediakan kerahasiaan sekaligus integritas data. Tidak seperti mode CBC, GCM adalah *Authenticated Encryption* yang dapat mendeteksi jika data telah dimodifikasi melalui *Authentication Tag*.

### **Bcrypt**
Fungsi hashing kata sandi berbasis algoritma *Blowfish*. Bcrypt dirancang untuk menjadi lambat secara komputasi guna memperlambat serangan *Brute Force*.

### **Certificate Pinning**
Teknik keamanan pada aplikasi mobile untuk hanya mempercayai sertifikat SSL spesifik milik server Anda, mencegah serangan *Man-in-the-Middle* (MitM).

### **DLP (Data Loss Prevention)**
Strategi keamanan untuk memastikan data sensitif tidak keluar dari organisasi secara tidak sah. Dalam buku ini diimplementasikan melalui *watermarking* dinamis pada PDF.

### **IDOR (Insecure Direct Object Reference)**
Celah keamanan di mana pengguna dapat mengakses data milik orang lain dengan mengganti parameter ID. SovereignDrive mencegah ini menggunakan UUIDv4 yang acak.

### **JWT (JSON Web Token)**
Standar untuk berbagi klaim keamanan antara server dan mobile secara *stateless*. Terdiri dari Header, Payload, dan Signature.

### **Little-Endian**
Urutan penyimpanan byte di mana byte yang paling tidak signifikan disimpan di alamat memori terendah. Digunakan dalam struktur biner `.enc` agar file konsisten di berbagai arsitektur CPU (Intel/ARM).

### **Nonce (Number Used Once)**
Angka acak unik yang digunakan hanya sekali dalam enkripsi AES-GCM untuk memastikan ciphertext selalu berbeda meskipun data aslinya sama.

---

## 🧠 Kecerdasan Buatan (AI) & Pencarian

### **Inverted Index**
Struktur data inti pada Elasticsearch. Memetakan kata kunci ke daftar dokumen secara langsung, memungkinkan pencarian jutaan data dalam milidetik.

### **Lemmatization**
Proses NLP untuk mengembalikan kata ke bentuk dasarnya berdasarkan kamus (misal: "mewarnai" menjadi "warna").

### **OCR (Optical Character Recognition)**
Teknologi mengekstraksi teks dari gambar atau hasil scan menggunakan mesin seperti Tesseract.

### **PyMuPDF (Fitz)**
Library berperforma tinggi untuk memproses PDF. Jauh lebih cepat daripada OCR konvensional untuk PDF yang sudah memiliki teks digital.

### **Relevance Scoring**
Algoritma untuk menentukan urutan hasil pencarian berdasarkan kemiripan teks. SovereignDrive menjaga skor ini di database menggunakan logika *Case/When*.

---

## ⚙️ Infrastruktur & Software Engineering

### **Audit Log**
Catatan permanen dan tidak dapat diubah (immutable) tentang siapa yang melakukan apa, kapan, dan di mana. Sangat krusial untuk audit kepatuhan (compliance).

### **CleanupFileResponse**
Pola desain (pattern) kustom untuk menjamin file sementara di disk server terhapus secara otomatis segera setelah pengiriman data ke pengguna selesai.

### **Chunked Upload**
Metode mengunggah file besar dengan membaginya menjadi potongan-potongan kecil (chunks) agar lebih stabil terhadap gangguan koneksi internet.

### **F() Expressions**
Fitur Django untuk melakukan operasi matematika langsung di level database SQL, mencegah *Race Condition* saat memperbarui kuota penyimpanan.

### **Idempotency**
Sifat operasi yang memberikan hasil yang sama meskipun dijalankan berulang kali. Penting agar tugas Celery yang di-*retry* tidak menduplikasi data.

### **License Gatekeeper**
Mekanisme validasi kunci lisensi saat aplikasi dijalankan (startup), memastikan integritas distribusi perangkat lunak.

### **NamedTemporaryFile**
Teknik manajemen memori di mana data besar ditulis ke file sementara di disk (bukan RAM), mencegah error *Out-of-Memory* (OOM).

### **SSO (Single Sign-On)**
Sistem autentikasi yang memungkinkan pengguna login ke berbagai aplikasi menggunakan satu identitas terpusat (seperti Google atau Azure AD).

### **X-Accel-Redirect**
Fitur Nginx untuk mengambil alih tugas pengiriman file besar dari Django, meningkatkan performa server secara signifikan melalui pengalihan internal.

---

## 🛠️ Daftar Alat & Library Utama

- **Bandit:** Alat analisis statis untuk menemukan celah keamanan dalam kode Python.
- **Celery Beat:** Penjadwal tugas (scheduler) untuk menjalankan tugas rutin seperti pembersihan disk dan audit kuota.
- **Daphne:** Server ASGI yang memungkinkan Django menangani WebSocket dan protokol asinkron.
- **Flower:** Dashboard monitoring real-time untuk memantau kesehatan koki digital (Celery Workers).
- **Redis:** Sistem penyimpanan data di memori yang digunakan sebagai *Message Broker* dan *Cache*.
- **uv:** Paket manajer Python berbasis Rust yang super cepat (10x lebih cepat dari pip).
