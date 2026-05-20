# 📖 API Reference: SovereignDrive AI (v1.0)

Technical documentation for third-party integrations, Mobile (Flutter), and Desktop applications.  
**Base URL:** `http://localhost:8000/api/storage/v1/`

---

## 🛠️ Global Configuration
All requests must include the following headers:
| Header | Value | Description |
| :--- | :--- | :--- |
| `Accept` | `application/json` | Expected data format |
| `Authorization` | `Bearer <token>` | JWT Access Token (for protected endpoints) |

### HTTP Status Codes
*   `200 OK`: Request successful.
*   `201 Created`: New resource successfully created.
*   `401 Unauthorized`: Token invalid or expired.
*   `403 Forbidden`: You do not have permission to access this resource.
*   `404 Not Found`: Object (File/Folder) not found.

---

## 🔐 Authentication (JWT & SSO)
Using OAuth2/JWT standard. Access tokens are valid for 60 minutes.

### 1. Login (Standard)
*   **POST** `/auth/login/`
*   **Payload:** `{ "username": "admin", "password": "password123" }`

### 2. SSO Redirect
*   **GET** `/social-auth/login/azuread-oauth2/` (Microsoft Azure AD)
*   **GET** `/social-auth/login/google-oauth2/` (Google Workspace)

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
*   **GET** `/files/search/?q=financial report`
*   **Features:** Supports *Fuzzy Search* and *OCR Content Search*.
*   **Ordering:** Results sorted by highest AI relevance score.

### 3. Secure Download (Streaming + DLP)
*   **GET** `/files/<uuid>/download/`
*   **Note:** Files are decrypted real-time using AES-256 GCM. PDF files will have dynamic forensic watermarks injected.

---

## 🔗 Sharing & Collaboration
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
### 1. Polymorphic Audit Logs (Admin Only)
*   **GET** `/audit-logs/`
*   **Data Fields:** `target_id`, `target_type`, `ip_address`, `user_agent`.

---

## 🚀 Large File Upload (Chunked)
Use this flow for files > 100MB to avoid timeouts:
1.  **Init:** `POST /files/start_chunked_upload/` -> Get `upload_id`.
2.  **Upload:** `POST /files/upload_chunk/<upload_id>/` with `chunk_index`.
3.  **Merge:** `POST /files/complete_chunked_upload/<upload_id>/` for finalization.

---
*This documentation is auto-generated for SovereignDrive AI Architecture. Use Postman for endpoint testing.*
