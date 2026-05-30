# Bab 9: Mobilisasi Data: Membangun Aplikasi Android

## Cerita Di Balik Layar
Seiring berjalannya waktu, data tidak lagi berdiam di satu tempat. Pengguna SovereignDrive AI ingin mengakses dokumen rahasia mereka saat berada di perjalanan, memotret nota fisik langsung dari kamera ponsel, dan menyimpannya secara instan ke cloud pribadi tanpa melalui perantara pihak ketiga. 

Dalam bab ini, kita akan mentransformasi SovereignDrive AI dari sekadar aplikasi web menjadi **Ekosistem Mobile**. Kita akan membangun jembatan (API) agar ponsel Android bisa "berbicara" dengan server kita dengan bahasa yang sama, aman, dan efisien.

---

## 9.1. Arsitektur API: Jembatan JSON yang Skalabel

Aplikasi Android tidak mengerti bahasa HTML. Ia mengerti **JSON (JavaScript Object Notation)**. Kita menggunakan **Django Rest Framework (DRF)** untuk mengubah objek database menjadi format JSON yang ringan.

### 9.1.1. API Versioning
Dunia mobile sangat dinamis. Anda mungkin merilis fitur baru yang mengubah struktur data. 
**Prinsip Senior**: Selalu gunakan versi pada URL API Anda (misal: `/api/v1/`). Ini menjamin aplikasi user lama tidak akan rusak saat Anda merilis update di sisi server.

### 9.1.2. Autentikasi JWT (Stateless Security)
Ponsel Android tidak menyimpan *cookie* seperti browser. SovereignDrive menggunakan **JWT (JSON Web Token)**.
- **Access Token**: Token jangka pendek (misal: 1 jam) untuk akses data.
- **Refresh Token**: Token jangka panjang (misal: 7 hari) untuk mendapatkan access token baru tanpa harus login ulang.
- **Prinsip**: Jika ponsel hilang, user bisa melakukan *revoke* refresh token dari dashboard web.

---

## 9.2. Bedah Kode: Serializer & Security Hardening

Berikut adalah implementasi di `storage/api/serializers.py` untuk mengoptimalkan data yang dikirim:

```python
from rest_framework import serializers
from storage.models import File

class FileSerializer(serializers.ModelSerializer):
    # [1] Custom Field: Konversi Byte ke Megabyte di level API
    size_mb = serializers.SerializerMethodField()

    class Meta:
        model = File
        fields = ['id', 'name', 'size_mb', 'created_at', 'thumbnail']
        read_only_fields = ['id', 'created_at']

    def get_size_mb(self, obj):
        return round(obj.size / (1024 * 1024), 2)
```

**Analisis Teknikal:**
- **`SerializerMethodField`**: Memungkinkan kita melakukan transformasi data (seperti perhitungan unit) di level API, sehingga aplikasi mobile tidak perlu melakukan kalkulasi berat.
- **Field Minimization**: Kita tidak mengirimkan *path* fisik file di server untuk mencegah peretasan melalui informasi struktur direktori.

---

## 9.3. Membangun Aplikasi Android (React Native)

Kita menggunakan **React Native** agar bisa membangun aplikasi mobile menggunakan JavaScript/TypeScript namun tetap mendapatkan performa asli (Native).

### 9.3.1. Keamanan Penyimpanan Token
Jangan pernah menyimpan JWT di `AsyncStorage` biasa karena datanya tersimpan dalam teks polos (plaintext) yang mudah dicuri oleh aplikasi jahat lain di ponsel yang di-root.
**Solusi**: Gunakan `react-native-keychain` yang menyimpan token di dalam **Android Keystore** (hardware-backed security).

### 9.3.2. Implementasi SSL Pinning
Untuk mencegah serangan *Man-in-the-Middle* (di mana peretas berpura-pura menjadi server Anda), aplikasi Android SovereignDrive hanya akan percaya pada sertifikat SSL yang sudah ditentukan sidik jarinya (*Certificate Pinning*).

---

## 9.4. Fitur Mobile: Kamera ke Cloud & Offline Sync

### 9.4.1. Instant Camera Upload
Alur kerja:
1.  User mengambil foto via `react-native-vision-camera`.
2.  File disimpan sementara di cache internal ponsel.
3.  Aplikasi memicu upload menggunakan `Multipart/form-data`.
4.  Server menerima, mengenkripsi, dan memberikan ID UUID seketika.

### 9.4.2. Offline Metadata Caching
Agar aplikasi terasa cepat, kita menyimpan daftar file di database lokal ponsel (**SQLite**). Saat tidak ada sinyal, user tetap bisa melihat daftar dokumen yang mereka miliki.

---

## 9.5. Common Pitfalls (Lubang Jebakan)

1.  **Over-fetching Data**: Mengirim seluruh isi database ke ponsel. Ini menghabiskan kuota user dan membuat aplikasi lambat. Gunakan **Pagination** pada setiap endpoint list.
2.  **API Rate Limiting**: Jika aplikasi mobile Anda bug dan melakukan ribuan request per detik, server Anda bisa mati. Gunakan `DRF Throttling` untuk membatasi jumlah request per IP/User.
3.  **Rooted Device Risk**: Aplikasi yang menangani data rahasia sebaiknya mendeteksi apakah ponsel sudah di-*root*. Jika ya, sistem harus membatasi fitur atau memberikan peringatan risiko keamanan.

---

## ✅ Engineering Checkpoint: Mobile & API Architecture
Pastikan jembatan antara mobile dan cloud Anda cepat, aman, dan efisien:
- [ ] **API Versioning:** Apakah seluruh URL API sudah diawali dengan prefix versi (v1/v2)?
- [ ] **Access & Refresh Tokens:** Apakah sistem JWT sudah menangani rotasi token dengan aman?
- [ ] **Secure Storage:** Apakah token disimpan di hardware-backed Keystore, bukan plaintext?
- [ ] **Data Minimization:** Apakah Serializer sudah menyembunyikan informasi internal server?
- [ ] **Throttling:** Apakah limitasi jumlah request (Rate Limit) sudah aktif di sisi server?
- [ ] **SSL Pinning:** Apakah aplikasi mobile sudah memvalidasi sertifikat server secara spesifik?
- [ ] **Root Detection:** Apakah aplikasi memiliki mekanisme deteksi keamanan perangkat?
