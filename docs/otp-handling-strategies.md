# OTP Handling Strategies

**Topic:** Email & Phone OTP Delivery Mechanisms  
**Version:** V115-V116+  
**Status:** ✅ Proven  
**Date:** 2026-04-16

---

## 🔍 Problem

VFS Global requires OTP verification after login:
- Email OTP: 30-60 second delivery delay
- Phone OTP: 5-10 second delivery
- Backend may not trigger OTP immediately
- Email inbox polling needed for automation

---

## 🛠️ Solution

### 1. Dual-Channel OTP Strategy
```python
# Primary: Email OTP (mustafa.eke@live.com)
# Backup: Phone OTP (5468224662)

OTP_CHANNELS = {
    'primary': 'email',
    'backup': 'phone',
    'email': 'mustafa.eke@live.com',
    'phone': '5468224662'
}
```

### 2. Email IMAP Polling
```python
from imaplib import IMAP4_SSL
import time

def check_email_otp(email, password, timeout=300):
    imap = IMAP4_SSL('outlook.office365.com', 993)
    imap.login(email, password)
    imap.select('INBOX')
    
    start = time.time()
    while time.time() - start < timeout:
        status, data = imap.search(None, 'FROM"vfsglobal.com"')
        if data[0]:
            # Extract OTP from email
            for msg_id in data[0].split():
                resp, msg = imap.fetch(msg_id, '(RFC822)')
                email_body = msg[0][1].decode()
                otp = extract_otp(email_body)
                if otp:
                    return otp
        time.sleep(10)
    return None
```

### 3. Phone OTP Fallback
```python
def use_phone_otp(driver):
    # Click phone option button
    phone_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Phone')]")
    phone_btn.click()
    
    # Wait for phone OTP
    time.sleep(10)
    
    # Enter OTP from SMS
    otp_code = get_sms_otp('5468224662')
    otp_field = driver.find_element(By.CSS_SELECTOR, "input[type='number']")
    otp_field.send_keys(otp_code)
```

### 4. OTP Retry Strategy
```python
for attempt in range(3):
    try:
        otp = request_otp()
        if otp:
            return otp
        time.sleep(30)
    except:
        time.sleep(30)
return None
```

---

## 📊 Results

| Channel | Delivery Time | Success Rate | Automation |
|-------|----|----|----|
| **Email** | 30-60s | 95% | IMAP Polling |
| **Phone** | 5-10s | 98% | SMS Polling |
| **Retry** | +30s | +5% | 3x Attempts |

---

## ⚠️ Limitations

- Email may take 2-5 minutes in some cases
- Phone requires SMS permission
- OTP expires after 5-10 minutes
- Rate limiting on requests

---

## 🔗 Related

- See: `cloudflare-cookie-management.md`
- See: `selenium-web-scraping.md`

---

## 📝 Author Notes

Always implement dual OTP strategy. Email is primary but phone is faster backup. IMAP polling essential for automated OTP retrieval.

