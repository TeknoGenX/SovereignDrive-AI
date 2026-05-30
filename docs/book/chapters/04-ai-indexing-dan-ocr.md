# Bab 4: Brain-Circuit: AI Indexing & OCR

## Cerita Di Balik Layar
Bayangkan Anda memiliki ribuan foto nota, dokumen PDF hasil scan, dan materi penting di dalam cloud Anda. Di cloud konvensional, Anda harus membuka file satu per satu secara manual karena komputer tidak tahu apa isi di dalam gambar tersebut. Data ini sering disebut sebagai **Dark Data**—data yang ada namun tidak bisa dimanfaatkan karena tidak dapat dicari.

Dalam bab ini, kita akan membangun "Mata Digital" untuk SovereignDrive. Kita akan membuat sistem yang secara otomatis membaca setiap piksel gambar, mengekstraksi teksnya, dan menyimpannya ke dalam memori cerdas server agar bisa dicari dalam hitungan milidetik. Inilah keunggulan utama yang membedakan SovereignDrive dari penyimpanan cloud biasa.

---

## 4.1. Membangun Pipeline Visi Komputer (OCR)

OCR (*Optical Character Recognition*) adalah teknologi yang menjembatani dunia fisik (piksel gambar) dengan dunia digital (teks terstruktur). Di jantung sistem ini, kita menggunakan **Tesseract OCR**, mesin berbasis *Neural Network* (LSTM) yang dikembangkan oleh Google.

### 4.1.1. Alur Kerja Ekstraksi Pintar
SovereignDrive tidak melakukan OCR secara buta. Kita membangun pipeline yang efisien:

```mermaid
graph TD
    A[File Terunggah] --> B{Cek Tipe File}
    B -- PDF Digital -- > C[Ekstraksi Teks via PyMuPDF]
    B -- Gambar / Scan --> D[Image Pre-processing]
    D --> E[Tesseract OCR Engine]
    C & E --> F[Teks Mentah]
    F --> G[NLP Pipeline: Cleansing]
    G --> H[Simpan ke DB & Elasticsearch]
```

### 4.1.2. Pre-processing: Memberi "Kacamata" pada AI
Tesseract seringkali gagal jika gambar terlalu buram, miring, atau memiliki latar belakang yang bising. Kita menggunakan **Pillow (PIL)** untuk melakukan normalisasi citra sebelum diproses:

1.  **Grayscale & Binarization**: Mengubah gambar menjadi hitam-putih murni. Ini menghilangkan gangguan warna dan memperjelas kontur huruf.
2.  **DPI Scaling**: Tesseract bekerja optimal pada resolusi 300 DPI. Kita secara otomatis mengubah ukuran gambar yang terlalu kecil agar karakter lebih mudah dikenali.
3.  **Noise Removal**: Menggunakan filter median untuk membuang bintik-bintik halus (salt and pepper noise) yang sering muncul pada dokumen hasil scan lama.

---

## 4.2. Natural Language Processing (NLP)

Mendapatkan teks dari gambar hanyalah separuh jalan. Teks hasil OCR seringkali mengandung kesalahan ketik atau kata-kata yang tidak berguna untuk pencarian.

### 4.2.1. Normalisasi & Cleansing
Kita membangun modul `TextPreprocessor` yang melakukan tugas-tugas berikut:
- **Case Folding**: Mengubah semua teks menjadi huruf kecil agar pencarian bersifat *case-insensitive*.
- **Regex Cleaning**: Membuang karakter non-alfanumerik yang sering muncul sebagai sampah hasil OCR (seperti `|`, `_`, atau `~`).

### 4.2.2. Lemmatization: Mencari Berdasarkan Makna
Mengapa mencari "makanan" juga harus memunculkan file berisi kata "makan"? 
Inilah gunanya **Lemmatization**. Berbeda dengan *Stemming* yang hanya memotong imbuhan secara kaku (misal: "mewarnai" menjadi "warna"), Lemmatization menggunakan kamus bahasa untuk mengembalikan kata ke bentuk dasarnya (Lemma) secara cerdas. 

Di SovereignDrive, kita mengintegrasikan NLTK dengan dukungan bahasa Indonesia untuk memastikan hasil pencarian tetap akurat meskipun kata yang dicari menggunakan imbuhan yang berbeda.

---

## 4.3. Bedah Kode: Arsitektur AI Hybrid Worker

Tugas AI adalah tugas yang sangat haus *resource* (CPU dan RAM). Jika dilakukan langsung di server web, aplikasi akan membeku. Kita menggunakan **Celery** untuk mengelola tugas-tugas ini secara asinkron.

### 4.3.1. Implementasi RAM-Friendly Indexing
Perhatikan strategi kita dalam menangani file besar di `storage/tasks/__init__.py`. Kita tidak memuat seluruh file ke memori, melainkan melakukan *streaming decryption* langsung ke file sementara di disk:

```python
@shared_task(bind=True, max_retries=3)
def process_file_and_index(self, file_id):
    # TAHAP 0: DEKRIPSI KE TEMPORARY FILE (RAM-Friendly)
    # NamedTemporaryFile memungkinkan library lain (fitz/PIL) membaca langsung dari disk
    with tempfile.NamedTemporaryFile(delete=True) as tmp_file:
        file_obj.file.seek(0)
        for chunk in decrypt_stream(file_obj.file):
            tmp_file.write(chunk)
        tmp_file.flush() # Pastikan semua data tertulis ke disk
        
        # TAHAP 1: EKSTRAKSI BERDASARKAN TIPE
        if ext.endswith('.pdf'):
            # Buka PDF dari path file sementara (Hemat RAM!)
            with fitz.open(tmp_file.name) as doc:
                text = "".join([p.get_text() for p in doc])
        else:
            # Buka Gambar dari path file sementara
            with Image.open(tmp_file.name) as img:
                text = pytesseract.image_to_string(img)
```

### **Analisis Engineering Tingkat Lanjut:**
1.  **Disk Buffering**: Dengan menulis ke disk sementara (`tmp_file.name`), kita bisa memproses file 100MB di server yang hanya memiliki sisa RAM 50MB.
2.  **Context Manager (`with`)**: Penggunaan `with` menjamin `tmp_file` akan dihapus dari disk segera setelah blok kode selesai, meskipun terjadi error di tengah proses.
3.  **Hybrid Engine**: Menggunakan `fitz` (PyMuPDF) karena ia mampu mengekstrak teks dari ribuan halaman PDF digital dalam hitungan detik tanpa membebani CPU seperti OCR.

---

## 4.4. Skalabilitas: Celery Task Prioritization

Tidak semua tugas AI memiliki prioritas yang sama. Di SovereignDrive, kita memisahkan antrean (queues):
- **Queue: `high_priority`**: Untuk pembuatan *thumbnail* agar user bisa langsung melihat pratinjau foto.
- **Queue: `ai_indexing`**: Untuk proses OCR dan NLP yang berat. 

Dengan pemisahan ini, ribuan dokumen yang sedang diindeks di latar belakang tidak akan mengganggu kecepatan sistem dalam memunculkan ikon gambar di dashboard pengguna.

---

## 4.5. Common Pitfalls (Lubang Jebakan)

1.  **Missing Tesseract Data**: Tesseract akan *crash* jika paket bahasa (`tessdata`) tidak ditemukan. Pastikan path `TESSDATA_PREFIX` sudah terkonfigurasi di environment server.
2.  **Encoding Nightmares**: Teks hasil OCR seringkali mengandung karakter non-UTF8. Selalu gunakan `.decode('utf-8', 'ignore')` atau `.encode('utf-8')` saat memproses string hasil ekstraksi.
3.  **Zombie Temporary Files**: Jika worker mati di tengah jalan, `NamedTemporaryFile` mungkin tidak terhapus. Selalu gunakan blok `try...finally` atau *context manager* (`with` statement) untuk menjamin kebersihan disk server.

---

## ✅ Engineering Checkpoint: AI Indexing & OCR
Mesin kecerdasan membutuhkan penanganan khusus agar tidak membebani resource server:
- [ ] **Hybrid Extraction Engine:** Apakah sistem sudah menggunakan `fitz` untuk PDF digital dan Tesseract hanya untuk gambar/scan?
- [ ] **Image Pre-processing:** Sudahkah Anda mengimplementasikan *binarization* dan *resizing* untuk meningkatkan akurasi OCR?
- [ ] **NLP Sanitization Pipeline:** Apakah teks sudah dibersihkan dari karakter sampah dan dilakukan *lemmatization* untuk akurasi pencarian?
- [ ] **Memory Protection:** Apakah proses ekstraksi menggunakan *disk buffering* (Temporary Files) untuk mencegah lonjakan RAM (OOM)?
- [ ] **Queue Separation:** Apakah tugas AI yang berat sudah dipisahkan ke dalam antrean Celery yang berbeda dari tugas ringan (seperti thumbnail)?
- [ ] **Multi-language Support:** Apakah Tesseract sudah dikonfigurasi untuk mendukung bahasa utama dokumen (Indonesian & English)?
