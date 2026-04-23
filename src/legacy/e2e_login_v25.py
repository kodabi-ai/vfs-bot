import asyncio
from playwright.async_api import async_playwright
import cloudscraper

async def run_e2e_v25():
    print("🛡️ Step 1: Cloudscraper Bypass (Strict UA Sync)")
    scraper = cloudscraper.create_scraper(browser={'browser': 'chrome', 'custom_digest': 'cloudflare', 'delay': 10})
    try:
        # Visit base to get global cookies
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
    
    print(f"🍪 Injecting {len(cf_cookies)} cookies (UA: {cf_ua[:50]}...)")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent=cf_ua, viewport={"width": 1920, "height": 1080})
        await context.add_cookies(cf_cookies)
        page = await context.new_page()
        
        try:
            print("🌐 Navigating to VFS Login...")
            # Try networkidle first, fallback logic handles timeouts
            await page.goto("https://visa.vfsglobal.com/tur/tr/fra/login", wait_until="networkidle", timeout=40000)
            
            print("⏳ Waiting for SPA/Cloudflare to settle...")
            # Wait for login form to appear or 404 to resolve
            try:
                await page.wait_for_selector('input[type="email"]', timeout=10000)
                print("✅ Login form found directly!")
            except:
                print("⏳ Waiting additional 5s for rendering...")
                await page.wait_for_timeout(5000)

            current_url = page.url
            title = await page.title()
            print(f"🔗 Current URL: {current_url}")
            print(f"📄 Title: {title}")

            # Handle 404 Gracefully
            if 'page-not-found' in current_url.lower() or 'Üzgünüm' in title:
                print("🔄 Detected 404/Empty, waiting for SPA redirect...")
                await page.wait_for_timeout(10000)
                # Check if URL changed to a valid route or title changed
                new_url = page.url
                new_title = await page.title()
                print(f"🔗 Post-wait URL: {new_url}")
                print(f"📄 Post-wait Title: {new_title}")
                if 'page-not-found' in new_url.lower():
                    await page.reload(wait_until="networkidle", timeout=30000)
                    print("🔄 Reloaded due to persistent 404.")

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
            await page.wait_for_timeout(15000)
            
            current_url = page.url
            print(f"🔗 Final URL: {current_url}")
            
            if 'otp' in current_url.lower():
                print("✅ OTP Page Reached Successfully!")
            else:
                print("⚠️ Not on OTP page. Screenshot saved.")
                await page.screenshot(path="screenshots/e2e_v25_result.png")
                await page.screenshot(path="screenshots/e2e_v25_full.png", full_page=True)
            
        except Exception as e:
            print(f"❌ Playwright Error: {e}")
            await page.screenshot(path="screenshots/e2e_v25_error.png")
            print(f"🔗 Current URL: {page.url}")
        finally:
            await browser.close()

asyncio.run(run_e2e_v25())
