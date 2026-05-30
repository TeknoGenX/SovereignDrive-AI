# Glosarium Istilah Teknik: SovereignDrive AI

Glosarium ini disusun untuk membantu Anda memahami istilah-istilah teknis kelas atas yang digunakan di sepanjang buku ini. Istilah-istilah ini mencakup domain Kriptografi, Kecerdasan Buatan, Infrastruktur, dan Software Engineering.

---

## 🔐 Kriptografi & Keamanan

### **AES-256 GCM (Galois/Counter Mode)**
Standar enkripsi simetris yang menyediakan kerahasiaan sekaligus integritas data. Tidak seperti mode CBC, GCM adalah *Authenticated Encryption* yang dapat mendeteksi jika data telah dimodifikasi oleh pihak ketiga melalui *Authentication Tag*.

### **Authenticated Encryption with Associated Data (AEAD)**
Bentuk enkripsi yang menjamin kerahasiaan (data tidak bisa dibaca) dan autentikasi (data berasal dari sumber yang benar dan belum diubah).

### **Bcrypt**
Fungsi hashing kata sandi berbasis algoritma *Blowfish*. Bcrypt dirancang untuk menjadi lambat secara komputasi (memiliki *work factor*) guna memperlambat serangan *Brute Force*.

### **Ciphertext**
Data yang telah dienkripsi sehingga tidak dapat dipahami tanpa kunci dekripsi yang tepat.

### **Initialization Vector (IV) / Nonce**
Angka acak yang digunakan bersama kunci untuk mengenkripsi data. Nonce (*Number used once*) memastikan bahwa mengenkripsi data yang sama dua kali akan menghasilkan ciphertext yang berbeda.

### **IDOR (Insecure Direct Object Reference)**
Celah keamanan di mana pengguna dapat mengakses data milik orang lain hanya dengan mengganti parameter ID di URL (misal: mengganti `file/100` menjadi `file/101`). SovereignDrive mencegah ini menggunakan UUID.

### **JWT (JSON Web Token)**
Standar terbuka untuk berbagi klaim keamanan antara server dan client (biasanya mobile) secara *stateless*. Terdiri dari Header, Payload, dan Signature.

### **Zero-Trust Architecture**
Model keamanan yang berasumsi bahwa ancaman bisa datang dari mana saja (dalam atau luar jaringan). Di SovereignDrive, ini berarti server tidak dipercaya untuk melihat data asli, sehingga enkripsi dilakukan sebelum data disimpan.

---

## 🧠 Kecerdasan Buatan (AI) & NLP

### **Inverted Index**
Struktur data inti pada search engine (seperti Elasticsearch). Alih-alih memetakan Dokumen ke Kata, Inverted Index memetakan Kata ke Dokumen, memungkinkan pencarian teks penuh yang instan.

### **Lemmatization**
Proses NLP untuk mengembalikan kata ke bentuk dasarnya berdasarkan kamus (misal: "memakan" menjadi "makan"). Berbeda dengan *Stemming* yang hanya memotong imbuhan secara kasar.

### **OCR (Optical Character Recognition)**
Teknologi untuk mengekstraksi teks dari gambar atau dokumen hasil scan (seperti PDF gambar) menjadi teks digital yang bisa diedit dan dicari.

### **Stopwords**
Kata-kata umum yang sering muncul dalam bahasa (seperti "yang", "di", "dan") namun tidak memiliki nilai penting dalam pencarian informasi, sehingga biasanya dibuang dalam proses *indexing*.

### **Tokenization**
Proses memecah aliran teks menjadi potongan-potongan kecil yang disebut token (biasanya berupa kata-kata individu).

---

## ⚙️ Infrastruktur & Software Engineering

### **Asynchronous Task**
Tugas yang dijalankan di latar belakang tanpa menghentikan proses utama. Di SovereignDrive, OCR dan Enkripsi dilakukan secara asinkron agar pengguna tidak perlu menunggu lama saat mengunggah file.

### **Bulk Operations**
Teknik melakukan banyak operasi database (seperti update atau delete ribuan baris) dalam satu perintah SQL tunggal untuk meningkatkan performa secara drastis.

### **CI/CD (Continuous Integration / Continuous Deployment)**
Praktik otomatisasi dalam pengembangan perangkat lunak, di mana kode dites secara otomatis setiap kali ada perubahan, dan dideploy ke server jika lolos pengujian.

### **Idempotency**
Sifat suatu operasi yang jika dijalankan berkali-kali akan memberikan hasil yang sama. Sangat penting dalam antrean tugas (Celery) agar pengiriman ulang tugas yang gagal tidak merusak data.

### **Message Broker**
Perangkat lunak (seperti Redis atau RabbitMQ) yang berfungsi sebagai perantara untuk menerima pesan tugas dari aplikasi dan menyimpannya hingga dikerjakan oleh *worker*.

### **N+1 Query Problem**
Masalah performa di mana aplikasi melakukan terlalu banyak query kecil ke database di dalam sebuah loop, padahal bisa dilakukan dalam satu query besar menggunakan *JOIN*.

### **OOM (Out-of-Memory)**
Kondisi di mana aplikasi mencoba menggunakan lebih banyak RAM daripada yang tersedia di server, biasanya menyebabkan sistem *crash*. SovereignDrive mencegah ini dengan teknik *streaming*.

### **UUID (Universally Unique Identifier)**
String 128-bit yang digunakan sebagai pengenal unik yang secara matematis mustahil untuk diduplikasi, bahkan antar sistem yang berbeda.

---

## 🛠️ Tools & Library

- **Celery:** Distributed Task Queue untuk Python.
- **Daphne/Gunicorn:** Server untuk menjalankan aplikasi Django di produksi.
- **Elasticsearch:** Mesin pencari dan analitik terdistribusi.
- **NLTK:** Natural Language Toolkit untuk pemrosesan teks.
- **Tesseract:** Mesin OCR open-source dari Google.
- **WhiteNoise:** Middleware Django untuk melayani file statis secara efisien.
