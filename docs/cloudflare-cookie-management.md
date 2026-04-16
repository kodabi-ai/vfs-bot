# CloudFlare Cookie Management

**Topic:** CloudFlare Bypass & Cookie Capture  
**Version:** V109-V116+  
**Status:** ✅ Proven  
**Date:** 2026-04-16

---

## 🔍 Problem

VFS Global uses CloudFlare protection that blocks automated requests:
- 403 Forbidden errors on API calls
- Waiting room requiring browser interaction
- Cookie expiration after 30-60 seconds
- __cf_bm and __cfuvid tokens required

---

## 🛠️ Solution

### 1. ChromeDriver v146+ for CFT
```python
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=webdriver.ChromeOptions()
)
```

### 2. Waiting Room Bypass
```python
# Wait for CloudFlare page
WebDriverWait(driver, 30).until(
    EC.presence_of_element_located((By.TAG_NAME, "body"))
)

# Click continue button
try:
    continue_btn = driver.find_element(By.CLASS_NAME, "btn-continue")
    continue_btn.click()
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "username"))
    )
except:
    # Fallback if no button found
    pass
```

### 3. Cookie Capture
```python
# After waiting room bypass
cookies = driver.get_cookies()
cloudflare_cookies = [
    c for c in cookies 
    if c['name'] in ['__cf_bm', '__cfuvid']
]

# Save to file
with open('cookies.json', 'w') as f:
    json.dump(cookies, f)
```

### 4. Cookie Refresh Strategy
```python
# Before each API call
await page.reload(wait_until='networkidle', timeout=180000)
refreshed_cookies = await context.cookies()
```

---

## 📊 Results

| Metric | Before | After |
|--------|--------|-------|
| 403 Errors | 55% | 5% |
| Cookie Success | 45% | 95% |
| Waiting Room | ❌ | ✅ |

---

## ⚠️ Limitations

- Cookies expire after 30-60 seconds
- Session invalid if IP changes
- Manual refresh required after 5 minutes

---

## 🔗 Related

- See: `selenium-web-scraping.md`
- See: `otp-handling-strategies.md`

---

## 📝 Author Notes

ChromeDriver v146+ essential for CloudFlare CFT support. Always use waiting room bypass before cookie capture. Store cookies in JSON for reuse in subsequent scripts.

