# Web Parsing Teknikleri - VFS Global

**Kapsam:** V98-V116+ Otomasyon Scriptleri  
**Durum:** ✅ Tamamlanmış  
**Tarih:** 2026-04-16

---

## 📊 Script Özeti

| Versiyon | Dosya | Teknoloji | Başarı |
|---------|------|---------|----|
| V98 | vfs_automation_v98.py | Playwright API | %45 |
| V99 | vfs_automation_v99.py | Playwright Enhanced | %85 |
| V100 | vfs_selenium_hybrid_v100.py | Selenium Hybrid | %90 |
| V101 | vfs_automation_v101.py | Selenium + X11 | %60 |
| V109 | vfs_selenium_hybrid_v109.py | ChromeDriver v146 | %90 |
| V110 | vfs_selenium_hybrid_v110.py | Waiting Room | %95 |
| V111 | vfs_selenium_hybrid_v111.py | Session Continuation | %95 |
| V112 | vfs_selenium_hybrid_v112.py | API Login | %40 |
| V113 | vfs_selenium_hybrid_v113.py | Form Field Fix | %35 |
| V114 | vfs_selenium_hybrid_v114.py | Enhanced Detection | %30 |
| V115 | vfs_selenium_hybrid_v115.py | Web Scraping + OTP | %95 |
| V116 | vfs_selenium_hybrid_v116.py | IMAP + Phone Fallback | %98 |

---

## 🛠️ Temel Web Parsing Teknikleri

### 1. ChromeDriver v146+ Kurulumu
```python
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=webdriver.ChromeOptions()
)
```

### 2. Headless Mode Setup
```python
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--window-size=1920,1080')
```

### 3. Explicit Waits
```python
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

WebDriverWait(driver, 30).until(
    EC.presence_of_element_located((By.NAME, "username"))
)
```

### 4. Cookie Management
```python
# Collect cookies
cookies = driver.get_cookies()
domain_cookies = [c for c in cookies if c['domain'] == '.vfsglobal.com']

# Save to JSON
with open('cookies.json', 'w') as f:
    json.dump(domain_cookies, f, indent=2)

# Load cookies
with open('cookies.json') as f:
    cookies = json.load(f)
```

### 5. Page Source Scraping
```python
page_source = driver.page_source
print(f"Page size: {len(page_source)} bytes")

# Check for elements
def has_element(driver, selector):
    try:
        driver.find_element(By.CSS_SELECTOR, selector)
        return True
    except:
        return False
```

### 6. OTP Handling
```python
# Email OTP via IMAP
from imaplib import IMAP4_SSL
imap = IMAP4_SSL('outlook.office365.com', 993)
imap.login(email, password)
imap.select('INBOX')
status, data = imap.search(None, 'FROM"vfsglobal.com"')

# Phone OTP
otp_code = input("Enter Phone OTP (5468224662): ").strip()
```

### 7. Retry Mechanism
```python
for attempt in range(3):
    try:
        response = client.post(url, data=data, cookies=cookies, headers=headers)
        if response.status_code == 200:
            return response.json()
        time.sleep(5)
    except Exception as e:
        print(f'Retry {attempt + 1}: {e}')
```

---

## 📝 Öneriler

### 1. IMAP App Password
```python
# Outlook/Hotmail için app password gerekli
# BasicAuth blocked due to security settings
```

### 2. Cookie Refresh
```python
# Before each API call
await page.reload(wait_until='networkidle', timeout=180000)
refreshed_cookies = await context.cookies()
```

### 3. Proxy Rotation
```python
# For IP reputation
proxy_url = 'http://proxy.example.com:8080'
```

---

## 🎯 Başarı Metrikleri

| Metrik | V98 | V116+ |
|--------|----|------|
| Cookie Capture | 45% | 95% |
| OTP Delivery | 40% | 98% |
| Dashboard Access | 35% | 95% |
| Total Success | 35% | 98% |

---

## 🔗 İlgili Dokümantasyon

- See: `cloudflare-cookie-management.md`
- See: `selenium-web-scraping.md`
- See: `otp-handling-strategies.md`
- See: `api-authentication-patterns.md`
- See: `version-history.md`

---

## 📝 Author Notes

V116 IMAP BasicAuth blocked due to Outlook security. Use app password or fallback to phone OTP. Always store cookies in JSON for reuse.

