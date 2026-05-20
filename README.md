# ☁️ SovereignDrive AI - Enterprise AI Cloud Storage

**SovereignDrive AI** is a high-performance, self-hosted cloud storage platform designed for individuals and enterprises who demand total data sovereignty. Built with **Django 5**, **PostgreSQL 16**, and **Elasticsearch 7**, it combines military-grade encryption with advanced AI content indexing.

---

## 🚀 Key Highlights

*   **🛡️ Sovereign Security:** AES-256 GCM encryption at rest with polymorphic audit logging.
*   **🏢 Enterprise SSO:** Seamless integration with **Azure AD**, **Google Workspace**, and **Okta** (OpenID Connect).
*   **🕵️ DLP Watermarking:** Dynamic forensic watermarking (Name, Email, Timestamp) on PDF downloads to prevent data leaks.
*   **🤖 AI Content Intelligence:** Deep-search through images and PDFs using Tesseract OCR and Elasticsearch.
*   **⚡ Enterprise Architecture:** RAM-optimized Celery workers and Clean Architecture (Selectors/Services pattern).
*   **🤝 Real-time Collaboration:** Live cursors and instant comments via WebSockets (Django Channels).

---

## 🛠️ Tech Stack

*   **Backend:** Python/Django (ASGI/Daphne)
*   **Database:** PostgreSQL 16
*   **Search Engine:** Elasticsearch 7.17
*   **Worker/Queue:** Celery + Redis
*   **Infrastructure:** Docker Compose

---

## 📖 Project Documentation

Detailed technical and strategic guides:

1.  **[Strategic Analysis](STRATEGIC_ANALYSIS.md):** Business objectives, user analysis, and risk mitigation.
2.  **[Technical Architecture](TECHNICAL_ARCHITECTURE.md):** Deep dive into design patterns, encryption pipelines, and indexing strategies.
3.  **[API Reference](API_REFERENCE.md):** Comprehensive REST API documentation for integration.
4.  **[Project Proposal](PROJECT_PROPOSAL.md):** Academic context and competitive benchmarking.
5.  **[Storage Migration Guide](STORAGE_MIGRATION.md):** Technical steps for external 2TB storage integration.

---

## ⚙️ Quick Start (Development)

1.  **Clone & Prepare:**
    ```bash
    git clone https://github.com/TeknoGenX/awan.git
    cd awan
    cp .env.example .env  # Configure your secrets
    ```

2.  **Spin Up Infrastructure:**
    ```bash
    docker-compose up -d
    ```

3.  **Run Application:**
    ```bash
    ./run_services.sh
    ```

4.  **Verify Health:**
    ```bash
    ./check_infra.sh
    ```

---

## 👨‍💻 Author
**Andi Liani** - *Visionary Software Engineer*

---

## 💼 Business & Sales Inquiries

Interested in deploying **SovereignDrive AI** for your organization? We offer:
*   **Custom Enterprise Deployment:** On-premise or Private Cloud setup.
*   **SSO/AD Custom Integration:** Tailored identity management.
*   **SLA & Dedicated Support:** Priority maintenance for corporate clients.

**Contact for Sales & Partnerships:**
📧 **Email:** sales@teknogenx.com / andi@teknogenx.com
🌐 **Website:** [www.teknogenx.com](https://www.teknogenx.com)
📱 **LinkedIn:** [Andi Liani](https://linkedin.com/in/andiliani)

---
**SovereignDrive AI** - *Your Data, Your Control, Powered by AI.*
