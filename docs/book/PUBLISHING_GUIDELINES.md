# Panduan Penerbitan Buku (Publishing Guidelines)

Dokumen ini berisi daftar periksa dan pedoman untuk mempersiapkan naskah buku agar mudah diterima dan diproses oleh penerbit. Berdasarkan masukan pengguna pada 30 Mei 2026.

## 📋 Daftar Periksa (Checklist)

### 1. Format File & Penggabungan
- [ ] Gabungkan seluruh naskah bab (Bab 1 - Bab 10) ke dalam **satu file `.docx`**. Jangan dipisah per bab.
- [ ] Gunakan **Google Docs** untuk pengetikan/pengeditan utama, hindari penggunaan Microsoft Word secara langsung untuk kolaborasi awal.

### 2. Struktur & Navigasi
- [ ] Pastikan **Daftar Isi** memiliki nomor halaman yang akurat (otomatis tergenerate jika menggunakan satu file).

### 3. Konten Tambahan (Filosofi & Dasar)
- [ ] **Bab Pendahuluan (Filosofi):** Tambahkan cerita tentang Ubuntu, Open Source, dan alasan mengapa kita harus menggunakan Open Source.
- [ ] **Konteks Server:** Jelaskan kapan Ubuntu Server digunakan, mengapa memilih Ubuntu Server, dan dukungan hardware apa saja yang tersedia.

### 4. Target Pembaca & Gaya Visual
- [ ] **Pendekatan Pemula:** Jika targetnya pemula, utamakan penggunaan **GUI/Desktop** daripada CLI.
- [ ] **Kekayaan Gambar:** Untuk pemula, sertakan banyak gambar/tangkapan layar (screenshot), terutama saat:
    - Instalasi OS.
    - Instalasi aplikasi.
- [ ] **Pegangan Admin Server:** Jika ditujukan sebagai buku pegangan admin, sertakan screenshot langkah-demi-langkah instalasi server secara detail.

### 5. Tata Letak (Layout) & Tipografi
- [ ] **Tampilan CLI:** Jangan gunakan perataan "rata kiri-kanan" (justify) untuk teks/blok kode CLI agar tidak berantakan. Gunakan rata kiri (align left).

### 6. Penutup & Ekspansi
- [ ] **Bab Akhir (Masa Depan):** Ceritakan kemampuan Ubuntu Server yang belum dibahas di buku ini (Cloud, Kubernetes, Docker, AI, Machine Learning, Deep Learning, dll) sebagai jembatan ke buku selanjutnya.

---

## 🚀 Status Implementasi

| No | Deskripsi | Status | Catatan |
|---|---|---|---|
| 1 | File .docx Tunggal | Belum | Tersedia skrip penggabungan `.md` |
| 2 | Daftar Isi Berhalaman | Belum | Tergantung pada Google Docs/Word |
| 3 | Penggunaan Google Docs | Belum | Disarankan untuk tahap final |
| 4 | Bab Filosofi Open Source | Sudah | Lihat `00-filosofi-open-source.md` |
| 5 | Penjelasan Ubuntu Server | Sudah | Terintegrasi di Bab 0 dan Bab 1 |
| 6 | Fokus GUI (Pemula) | Belum | Perlu penyesuaian narasi visual |
| 7 | Screenshot Instalasi | Belum | Perlu pengambilan gambar manual |
| 8 | Screenshot Admin Server | Belum | Perlu pengambilan gambar manual |
| 9 | Tipografi CLI (Align Left) | Sudah | Standar Markdown sudah rata kiri |
| 10 | Bab Masa Depan (Outlook) | Sudah | Lihat Bagian 10.7 di Bab 10 |

---

## 🛠️ Alat Bantu (Helper Scripts)

### Menggabungkan Semua Bab
Gunakan perintah ini di terminal untuk menggabungkan seluruh file Markdown menjadi satu file `NASKAH_LENGKAP.md` yang siap diimpor ke Google Docs atau dikonversi ke `.docx`:

```bash
cat docs/book/chapters/00-filosofi-open-source.md \
    docs/book/chapters/01-pondasi-dan-persiapan.md \
    docs/book/chapters/02-database-dan-hirarki.md \
    docs/book/chapters/03-kriptografi-dan-streaming.md \
    docs/book/chapters/04-ai-indexing-dan-ocr.md \
    docs/book/chapters/05-elasticsearch-search-engine.md \
    docs/book/chapters/06-celery-background-worker.md \
    docs/book/chapters/07-telegram-bot-dan-visual-alur.md \
    docs/book/chapters/08-produksi-dan-hardening.md \
    docs/book/chapters/09-mobile-android-api.md \
    docs/book/chapters/10-testing-dan-security-audit.md > docs/book/NASKAH_LENGKAP.md
```
