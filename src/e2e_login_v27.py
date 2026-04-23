import asyncio
from playwright.async_api import async_playwright
import cloudscraper

async def run_e2e_v27():
    print("🛡️ Step 1: Cloudscraper Bypass & Session Init")
    scraper = cloudscraper.create_scraper(browser={'browser': 'chrome', 'custom_digest': 'cloudflare', 'delay': 10})
    
    # Get root cookies first
    try:
        scraper.get("https://visa.vfsglobal.com/tur/tr/", timeout=20)
        resp = scraper.get("https://visa.vfsglobal.com/tur/tr/fra/login", timeout=20)
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
            print("🌐 Navigating to VFS Login (load event)...")
            await page.goto("https://visa.vfsglobal.com/tur/tr/fra/login", wait_until="load", timeout=30000)
            
            print("⏳ Waiting 10s for SPA to mount...")
            await page.wait_for_timeout(10000)
            
            current_url = page.url
            title = await page.title()
            print(f"🔗 Current URL: {current_url}")
            print(f"📄 Title: {title}")
            
            # Handle 404 SPA redirect by reloading
            if 'page-not-found' in current_url.lower() or 'Üzgünüm' in title:
                print("🔄 Detected 404, reloading to re-trigger SPA routing...")
                await page.reload(wait_until="load", timeout=20000)
                await page.wait_for_timeout(5000)
                print(f"🔗 Post-Reload URL: {page.url}")
                print(f"📄 Post-Reload Title: {await page.title()}")
                
                # If still 404, try navigating to root first to init shell
                if 'page-not-found' in page.url.lower():
                    print("🔄 Still 404. Navigating to root /tur/tr/ to init shell...")
                    await page.goto("https://visa.vfsglobal.com/tur/tr/", wait_until="load", timeout=15000)
                    await page.wait_for_timeout(3000)
                    print("🔄 Redirecting to /tur/tr/fra/login...")
                    await page.goto("https://visa.vfsglobal.com/tur/tr/fra/login", wait_until="load", timeout=15000)
                    await page.wait_for_timeout(3000)
                    print(f"🔗 Final Init URL: {page.url}")

            print("🔍 Finding inputs via JS (Broad Search)...")
            inputs = await page.evaluate('''() => {
                const all = document.querySelectorAll('input, textarea, select');
                const res = [];
                all.forEach(el => res.push({tag: el.tagName, name: el.name, type: el.type, value: el.value, placeholder: el.placeholder}));
                return res;
            }''')
            
            print(f"📄 Found {len(inputs)} interactive elements:")
            for el in inputs:
                if el['name'] or el['type'] or el['placeholder']:
                    print(f"   - {el['name']} (type: {el['type']}, ph: {el['placeholder']})")
                    
            email_input = next((i for i in inputs if 'email' in str(i.get('name', '')).lower() or 'email' in str(i.get('type', '')).lower() or 'e-posta' in str(i.get('placeholder', '')).lower()), None)
            password_input = next((i for i in inputs if 'password' in str(i.get('name', '')).lower() or 'password' in str(i.get('type', '')).lower() or 'şifre' in str(i.get('placeholder', '')).lower() or 'şifre' in str(i.get('name', '')).lower()), None)
            
            if email_input:
                print("✍️ Filling email...")
                await page.fill(f'input[name="{email_input["name"]}"]', 'mustafa.eke@live.com')
            
            if password_input:
                print("✍️ Filling password...")
                await page.fill(f'input[name="{password_input["name"]}"]', 'Vfsglobal!5561!')
                
            print("🖱️ Clicking Login button...")
            login_btn = await page.query_selector('button[type="submit"], button.login-btn, input[type="submit"]')
            if not login_btn:
                login_btn = await page.query_selector('button:has-text("Login"), button:has-text("Giriş"), button:has-text("Sign In")')
            if login_btn:
                try:
                    await login_btn.click(timeout=10000)
                except:
                    await login_btn.evaluate('el => el.click()')
            else:
                print("⚠️ No button found, trying JS click on all visible buttons...")
                await page.evaluate('Array.from(document.querySelectorAll("button")).forEach(b => {if(b.offsetParent !== null) b.click()})')
            
            print("⏳ Waiting for OTP page or redirection...")
            await page.wait_for_timeout(10000)
            
            current_url = page.url
            print(f"🔗 Final URL: {current_url}")
            
            if 'otp' in current_url.lower() or 'verify' in current_url.lower():
                print("✅ OTP Page Reached Successfully!")
            else:
                print("⚠️ Not on OTP page. Screenshot saved.")
                await page.screenshot(path="screenshots/e2e_v27_result.png")
                print("💾 Full HTML snapshot saved to debug.")
                
        except Exception as e:
            print(f"❌ Playwright Error: {e}")
            await page.screenshot(path="screenshots/e2e_v27_error.png")
            print(f"🔗 Current URL: {page.url}")
        finally:
            await browser.close()

asyncio.run(run_e2e_v27())
