import asyncio
from playwright.async_api import async_playwright
import cloudscraper

async def run_e2e_v17():
    print("🛡️ Step 1: Cloudscraper Bypass (Fresh Cookies)")
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
            print("🌐 Navigating to VFS Login...")
            await page.goto("https://visa.vfsglobal.com/tur/tr/fra/login", wait_until="domcontentloaded", timeout=30000)
            
            # Dynamic wait for Cloudflare Challenge
            print("⏳ Waiting for Cloudflare Challenge to resolve (Max 45s)...")
            try:
                await page.wait_for_selector("#cf-hcaptcha-container", state="detached", timeout=45000)
                print("✅ Cloudflare Challenge Solved!")
            except Exception:
                print("⚠️ Cloudflare challenge timeout. Proceeding anyway.")
            
            print("⏳ Waiting 5s for Angular UI to hydrate...")
            await page.wait_for_timeout(5000)
            
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
                await page.fill('input[type="email"]', 'mustafa.eke@live.com')
            
            if password_input:
                print("✍️ Filling password...")
                await page.fill('input[type="password"]', 'Vfsglobal!5561!')
                
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
                await page.evaluate('document.querySelector("button")?.click()')
            
            print("⏳ Waiting for OTP page or redirection...")
            await page.wait_for_timeout(10000)
            
            current_url = page.url
            print(f"🔗 Final URL: {current_url}")
            
            if 'otp' in current_url.lower():
                print("✅ OTP Page Reached Successfully!")
            else:
                print("⚠️ Not on OTP page. Screenshot saved.")
                await page.screenshot(path="screenshots/e2e_v17_result.png")
            
        except Exception as e:
            print(f"❌ Playwright Error: {e}")
            await page.screenshot(path="screenshots/e2e_v17_error.png")
            print(f"🔗 Current URL: {page.url}")
        finally:
            await browser.close()

asyncio.run(run_e2e_v17())
