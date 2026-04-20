# VFS Global Visa Portal Automation

## 🚀 Project Overview

A robust Python-based automation system for logging into the VFS Global visa portal, bypassing Cloudflare protection, and handling multi-channel OTP authentication (Email/SMS).

## 🛠️ Key Features

- **Cloudflare Bypass:** Handles `403201` challenges automatically.
- **OTP Handling:** Dual-channel support (Email via IMAP, Phone via SMS).
- **Configuration:** YAML-based configuration with environment variable overrides.
- **Modular Architecture:** Designed for easy integration of new OTP providers and browsers.

## 📦 Installation & Setup

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
