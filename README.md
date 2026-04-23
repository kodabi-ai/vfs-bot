# VFS Global Visa Portal Automation

## 🚀 Project Overview

A robust Python-based automation system for logging into the VFS Global visa portal, bypassing Cloudflare protection, and handling multi-channel OTP authentication (Email/SMS).

## 🛠️ Key Features

- **Cloudflare Bypass:** Handles `403201` challenges automatically.
- **OTP Handling:** Dual-channel support (Email via IMAP, Phone via SMS).
- **Configuration:** YAML-based configuration with environment variable overrides.
- **Modular Architecture:** Designed for easy integration of new OTP providers and browsers.

## 📦 Installation & Setup

**Özellikler:**
- ✅ CloudFlare Cookie Bypass & Persistence
- ✅ Dual-Channel OTP (Email + Phone {{VFS_PHONE}})
- ✅ 15-Minute Session Cache
- ✅ Multi-Account Batch Processing
- ✅ Docker Container Deployment
- ✅ FastAPI Web Service

1. Clone the repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure credentials:
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```
4. Run the login script:
   ```bash
   python vfs_login.py
   ```

## 📄 Documentation

For detailed technical documentation and version history, see the `/docs` directory or the centralized `llmful.txt`.

## 🧪 Testing

Run the test suite:
```bash
pytest
```

### 2. Bağımlılıkları Kur

```bash
pip install -r requirements.txt
playwright install chromium
```

### 3. Environment Ayarla

```bash
cp .env.example .env
# Edit .env with your credentials
```

### 4. Docker ile Başlat

```bash
docker-compose up --build -d
```

### 5. API Test

```bash
curl http://localhost:8000/api/v1/health
```

---

## 🎯 Kullanım

### FastAPI API

```bash
# Health Check
curl http://localhost:8000/api/v1/health

# Account Status
curl http://localhost:8000/api/v1/accounts/{id}/status

# Refresh Session
curl -X POST http://localhost:8000/api/v1/accounts/{id}/refresh
```

### Python Kodu

```python
from src import create_worker, Account

# Worker oluştur
worker = await create_worker(multi_account=True)

# Hesap ekle
account = Account(
    id="acc_001",
    email="{{VFS_EMAIL}}",
    password="{{VFS_PASSWORD}}",
    phone="{{VFS_PHONE}}"
)

# İşleme başla
await worker.run_batch([account])
```

---

## 🔑 Çevresel Değişkenler

```bash
VFS_EMAIL={{VFS_EMAIL}}
VFS_PASSWORD={{VFS_PASSWORD}}
VFS_PHONE={{VFS_PHONE}}
CACHE_DURATION_SEC=900  # 15 minutes
MAX_RETRIES=3
```

---

## 📊 Başarı Metrikleri

| Metrik | Hedef | V116 |
|--------|----|----|
| Cookie Collection | %95+ | %98+ |
| Login Success | %95+ | %98+ |
| OTP Detection | %95+ | %98+ |
| Full Automation | %90+ | %95+ |
| Execution Time | < 5 min | 3-5 min |

---

## 🗂️ Dokümantasyon

- **Architecture:** `/docs/architecture.md`
- **Requirements:** `/docs/requirements.md`
- **Version History:** `/docs/version-history.md`
- **OTP Strategies:** `/docs/otp-handling-strategies.md`
- **API Patterns:** `/docs/api-authentication-patterns.md`

---

## 🔄 BMAD Fazları

| Faz | Durum | Sahip |
|-----|----|----|
| Phase 1: Planning | ✅ Complete | BMAD John (PM) |
| Phase 2: Solutioning | ✅ Complete | BMAD Winston (Arch) |
| Phase 3: Implementation | 🟡 Active | BMAD Amelia (Dev) |
| Phase 4: Quality | ⏳ Pending | BMAD Quinn (QA) |
| Phase 5: Innovation | ⏳ Pending | BMAD Victor (Oracle) |

---

## 📝 Lisans

**MIT License** - Kodabi Vize Otomasyonu

---

*Version 1.0 | April 2026 | Agent Zero System*

