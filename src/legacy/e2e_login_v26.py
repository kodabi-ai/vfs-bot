import asyncio
from playwright.async_api import async_playwright
import cloudscraper

async def run_e2e_v26():
    print("🛡️ Step 1: Cloudscraper Bypass")
    scraper = cloudscraper.create_scraper(browser={'browser': 'chrome', 'custom_digest': 'cloudflare', 'delay': 10})
    try:
        resp = scraper.get("https://visa.vfsglobal.com/tur/tr/fra/login", timeout=30)
        print(f"✅ Cloudscraper Status: {resp.status_code}")
    except Exception as e:
        print(f"❌ Cloudscraper failed: {e}")
        return

    cf_cookies = []
    cf_ua = scraper.headers.get('User-Agent', '')
    for name, cookie in scraper.cookies.items():
        val = cookie.value if hasattr(cookie, 'value') else cookie
        cf_cookies.append({"name": name, "value": val, "domain": ".vfsglobal.com", "path": "/"})
    
    print(f"🍪 Injecting {len(cf_cookies)} cookies...")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent=cf_ua, viewport={"width": 1920, "height": 1080})
        await context.add_cookies(cf_cookies)
        page = await context.new_page()
        
        try:
            print("🌐 Navigating to VFS Login (domcontentloaded)...")
            # Switch to domcontentloaded to avoid network idle deadlocks on SPA
            await page.goto("https://visa.vfsglobal.com/tur/tr/fra/login", wait_until="domcontentloaded", timeout=30000)
            
            print("⏳ Waiting 10s for SPA JS to hydrate...")
            await page.wait_for_timeout(10000)
            
            current_url = page.url
            title = await page.title()
            print(f"🔗 Current URL: {current_url}")
            print(f"📄 Title: {title}")
            
            # Handle 404 SPA redirect
            if 'page-not-found' in current_url.lower() or 'Üzgünüm' in title:
                print("🔄 Detected 404, reloading login page...")
                await page.reload(wait_until="domcontentloaded", timeout=20000)
                await page.wait_for_timeout(5000)
                print(f"🔗 Post-Reload URL: {page.url}")
                print(f"📄 Post-Reload Title: {await page.title()}")

            print("🔍 Finding inputs via JS (Broad Search)...")
            inputs = await page.evaluate('''() => {
                const all = document.querySelectorAll('input, textarea, select');
                const res = [];
                all.forEach(el => res.push({tag: el.tagName, name: el.name, type: el.type, value: el.value}));
                return res;
            }''')
            
            print(f"📄 Found {len(inputs)} interactive elements:")
            for el in inputs:
                if el['name'] or el['type']:
                    print(f"   - {el['name']} (type: {el['type']})")
                    
            email_input = next((i for i in inputs if 'email' in str(i.get('name', '')).lower() or 'email' in str(i.get('type', '')).lower()), None)
            password_input = next((i for i in inputs if 'password' in str(i.get('name', '')).lower() or 'password' in str(i.get('type', '')).lower()), None)
            
            if email_input:
                print("✍️ Filling email...")
                await page.fill('input[name*="email"], input[type*="email"]', '{{VFS_EMAIL}}')
            
            if password_input:
                print("✍️ Filling password...")
                await page.fill('input[name*="password"], input[type*="password"]', '{{VFS_PASSWORD}}')
                
            print("🖱️ Clicking Login button...")
            login_btn = await page.query_selector('button[type="submit"], button.login-btn, input[type="submit"]')
            if not login_btn:
                login_btn = await page.query_selector('button:has-text("Login"), button:has-text("Giriş")')
            if login_btn:
                try:
                    await login_btn.click(timeout=10000)
                except:
                    await login_btn.evaluate('el => el.click()')
            else:
                print("⚠️ No button found, trying JS click on all buttons...")
                await page.evaluate('Array.from(document.querySelectorAll("button")).forEach(b => b.click())')
            
            print("⏳ Waiting for OTP page or redirection...")
            await page.wait_for_timeout(10000)
            
            current_url = page.url
            print(f"🔗 Final URL: {current_url}")
            
            if 'otp' in current_url.lower():
                print("✅ OTP Page Reached Successfully!")
            else:
                print("⚠️ Not on OTP page. Screenshot saved.")
                await page.screenshot(path="screenshots/e2e_v26_result.png")
            
        except Exception as e:
            print(f"❌ Playwright Error: {e}")
            await page.screenshot(path="screenshots/e2e_v26_error.png")
            print(f"🔗 Current URL: {page.url}")
        finally:
            await browser.close()

asyncio.run(run_e2e_v26())
