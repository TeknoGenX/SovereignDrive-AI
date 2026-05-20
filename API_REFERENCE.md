# 📖 API Reference: AwanDrive X (v1.0)

Dokumentasi teknis untuk integrasi pihak ketiga, aplikasi Mobile (Flutter), dan Desktop.  
**Base URL:** `http://localhost:8000/api/storage/v1/`

---

## 🛠️ Global Configuration
Seluruh request harus menyertakan header berikut:
| Header | Value | Deskripsi |
| :--- | :--- | :--- |
| `Accept` | `application/json` | Format data yang diharapkan |
| `Authorization` | `Bearer <token>` | Token akses JWT (untuk endpoint terproteksi) |

### HTTP Status Codes
*   `200 OK`: Request berhasil.
*   `201 Created`: Resource baru berhasil dibuat.
*   `401 Unauthorized`: Token tidak valid atau kedaluwarsa.
*   `403 Forbidden`: Anda tidak memiliki izin untuk akses resource ini.
*   `404 Not Found`: Objek (File/Folder) tidak ditemukan.

---

## 🔐 Authentication (JWT)
Menggunakan standar OAuth2/JWT. Token akses berlaku selama 60 menit.

### 1. Login
*   **POST** `/auth/login/`
*   **Payload:**
    ```json
    {
        "username": "admin",
        "password": "password123"
    }
    ```
*   **Success Response:**
    ```json
    {
        "access": "eyJhbG...",
        "refresh": "eyJhbG..."
    }
    ```

---

## 📁 Folders & Directory
### 1. List Folders
*   **GET** `/folders/`
*   **Response:** `Array of Folder Objects`

### 2. Create Folder
*   **POST** `/folders/`
*   **Payload:** `{ "name": "Project Alpha", "parent": null }`

---

## 📄 Files & AI Search
### 1. List Files
*   **GET** `/files/`

### 2. Smart AI Search (Elasticsearch)
*   **GET** `/files/search/?q=laporan keuangan`
*   **Fitur:** Mendukung *Fuzzy Search* (toleransi typo) dan *OCR Content Search*.
*   **Ordering:** Hasil diurutkan berdasarkan skor relevansi AI tertinggi.

### 3. Secure Download (Streaming)
*   **GET** `/files/<uuid>/download/`
*   **Header:** Membutuhkan `Authorization`
*   **Note:** File akan didekripsi secara *real-time* di sisi server menggunakan AES-256 GCM sebelum dikirim sebagai stream.

---

## 🔗 sharing & Collaboration
### 1. Generate Secure Link
*   **POST** `/shares/`
*   **Payload:**
    ```json
    {
        "file": "550e8400-e29b-41d4-a716-446655440000",
        "role": "viewer",
        "set_password": "link_secret_123",
        "expiry_date": "2026-12-31T23:59:59Z"
    }
    ```

---

## 🏢 Enterprise Governance
### 1. Polymorphic Audit Logs (Admin)
*   **GET** `/audit-logs/`
*   **Data Fields:**
    *   `target_id`: UUID objek yang diakses.
    *   `target_type`: Tipe objek (`file`, `folder`, `sharedlink`).
    *   `ip_address`: Lokasi akses user.
    *   `user_agent`: Perangkat yang digunakan.

---

## 🚀 Large File Upload (Chunked)
Gunakan alur ini untuk file > 100MB agar tidak terjadi *timeout*:
1.  **Init:** `POST /files/start_chunked_upload/` -> Ambil `upload_id`.
2.  **Upload:** `POST /files/upload_chunk/<upload_id>/` dengan parameter `chunk_index`.
3.  **Merge:** `POST /files/complete_chunked_upload/<upload_id>/` untuk finalisasi.

---
*Dokumentasi ini dibuat secara otomatis untuk AwanDrive X Arsitektur. Gunakan Postman untuk melakukan testing endpoint.*
