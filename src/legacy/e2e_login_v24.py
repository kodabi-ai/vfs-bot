import asyncio
from playwright.async_api import async_playwright
import cloudscraper

async def run_e2e_v24():
    print("🛡️ Step 1: Dual-Path Cloudscraper Bypass")
    scraper = cloudscraper.create_scraper(browser={'browser': 'chrome', 'custom_digest': 'cloudflare', 'delay': 10})
    
    # Path 1: Main Portal
    try:
        resp_main = scraper.get("https://visa.vfsglobal.com/tur/tr/", timeout=30)
        print(f"🏠 Main Portal Status: {resp_main.status_code}")
    except Exception as e:
        print(f"❌ Main Portal Failed: {e}")
        return

    # Path 2: Login Page
    try:
        resp_login = scraper.get("https://visa.vfsglobal.com/tur/tr/fra/login", timeout=30)
        print(f"🔑 Login Page Status: {resp_login.status_code}")
    except Exception as e:
        print(f"❌ Login Page Failed: {e}")
        return

    cf_cookies = []
    cf_ua = scraper.headers.get('User-Agent', '')
    
    # Merge cookies
    for name, cookie in scraper.cookies.items():
        val = cookie.value if hasattr(cookie, 'value') else cookie
        cf_cookies.append({"name": name, "value": val, "domain": ".vfsglobal.com", "path": "/"})
    
    print(f"🍪 Injecting {len(cf_cookies)} merged cookies...")
    for c in cf_cookies:
        print(f"   - {c['name']} = {c['value'][:10]}...")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent=cf_ua, viewport={"width": 1920, "height": 1080})
        await context.add_cookies(cf_cookies)
        page = await context.new_page()
        
        try:
            print("🌐 Navigating to VFS Login...")
            await page.goto("https://visa.vfsglobal.com/tur/tr/fra/login", wait_until="domcontentloaded", timeout=30000)
            
            print("⏳ Waiting 5s for Cloudflare & Angular to settle...")
            await page.wait_for_timeout(5000)
            
            current_url = page.url
            print(f"🔗 URL after load: {current_url}")
            print(f"📄 Title: {await page.title()}")

            # Handle 404 Redirect
            if 'page-not-found' in current_url.lower():
                print("🔄 Detected 404, reloading login page...")
                await page.goto("https://visa.vfsglobal.com/tur/tr/fra/login", wait_until="domcontentloaded", timeout=30000)
                await page.wait_for_timeout(5000)
                print(f"🔗 URL after reload: {page.url}")

            # Detect Inputs
            print("🔍 Finding inputs via JS...")
            inputs = await page.evaluate('''() => {
                const all = Array.from(document.querySelectorAll('input'));
                return all.filter(el => el.type === 'email' || el.type === 'password' || el.name.includes('email') || el.name.includes('password'));
            }''')
            
            print(f"📄 Found {len(inputs)} relevant inputs:")
            for inp in inputs:
                print(f"   - {inp.name} (type: {inp.type})")
                
            email_input = next((i for i in inputs if 'email' in i['type'].lower() or 'email' in i['name'].lower()), None)
            password_input = next((i for i in inputs if 'password' in i['type'].lower() or 'password' in i['name'].lower()), None)
            
            if email_input:
                print("✍️ Filling email...")
                await page.fill('input[type="email"]', '{{VFS_EMAIL}}')
            
            if password_input:
                print("✍️ Filling password...")
                await page.fill('input[type="password"]', '{{VFS_PASSWORD}}')
                
            print("🖱️ Clicking Login button...")
            login_btn = await page.query_selector('button[type="submit"]')
            if not login_btn:
                login_btn = await page.query_selector('button.login-btn')
            if login_btn:
                try:
                    await login_btn.click(timeout=10000)
                except:
                    await login_btn.evaluate('el => el.click()')
            else:
                print("⚠️ No button found, trying JS click...")
                await page.evaluate('document.querySelector("button")?.click()')
            
            print("⏳ Waiting for OTP page or redirection...")
            await page.wait_for_timeout(10000)
            
            current_url = page.url
            print(f"🔗 Final URL: {current_url}")
            
            if 'otp' in current_url.lower():
                print("✅ OTP Page Reached Successfully!")
            else:
                print("⚠️ Not on OTP page. Screenshot saved.")
                await page.screenshot(path="screenshots/e2e_v24_result.png")
            
        except Exception as e:
            print(f"❌ Playwright Error: {e}")
            await page.screenshot(path="screenshots/e2e_v24_error.png")
            print(f"🔗 Current URL: {page.url}")
        finally:
            await browser.close()

asyncio.run(run_e2e_v24())
