import asyncio
from playwright.async_api import async_playwright
import cloudscraper

async def run_e2e_v14():
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
            await page.goto("https://visa.vfsglobal.com/tur/tr/fra/login", wait_until="domcontentloaded", timeout=30000)
            
            print("⏳ Waiting 45s for Cloudflare Challenge to resolve...")
            await page.wait_for_timeout(45000)
            
            print("⏳ Waiting 10s for Angular UI to hydrate...")
            await page.wait_for_timeout(10000)
            
            print("🔍 Finding inputs in main frame...")
            main_inputs = await page.evaluate('''() => {
                const all = Array.from(document.querySelectorAll('input'));
                return all.map(el => ({
                    frame: 'main',
                    name: el.name, 
                    type: el.type, 
                    id: el.id, 
                    placeholder: el.placeholder
                }));
            }''')
            print(f"📄 Found {len(main_inputs)} inputs in main frame.")
            for inp in main_inputs:
                print(f"   - {inp['name']} (type: {inp['type']})")
                
            email_input = next((i for i in main_inputs if i.get('type') == 'email' or 'email' in (i.get('name') or '').lower()), None)
            password_input = next((i for i in main_inputs if i.get('type') == 'password' or 'password' in (i.get('name') or '').lower()), None)
            
            if email_input:
                print(f"✍️ Filling email (type='email')...")
                try:
                    await page.fill('input[type="email"]', 'mustafa.eke@live.com', timeout=10000)
                except:
                    await page.evaluate('document.querySelector("input[type=\'email\']")?.value = "mustafa.eke@live.com"')
            
            if password_input:
                print(f"✍️ Filling password (type='password')...")
                try:
                    await page.fill('input[type="password"]', 'Vfsglobal!5561!', timeout=10000)
                except:
                    await page.evaluate('document.querySelector("input[type=\'password\']")?.value = "Vfsglobal!5561!"')
                
            print("🖱️ Clicking Login button...")
            login_btn = await page.query_selector('button[type="submit"]')
            if not login_btn:
                login_btn = await page.query_selector('button.login-btn')
            if not login_btn:
                login_btn = await page.query_selector('button#loginBtn')
            
            if login_btn:
                try:
                    await login_btn.click(timeout=10000)
                except:
                    print("⚠️ Standard click failed, using JS click...")
                    await login_btn.evaluate('el => el.click()')
            else:
                print("⚠️ No specific button found, attempting JS click on first button...")
                await page.evaluate('document.querySelector("button")?.click()')
            
            print("⏳ Waiting for OTP page or redirection...")
            await page.wait_for_timeout(10000)
            
            current_url = page.url
            print(f"🔗 Final URL: {current_url}")
            
            if 'otp' in current_url.lower():
                print("✅ OTP Page Reached Successfully!")
            else:
                print("⚠️ Not on OTP page. Screenshot saved.")
                await page.screenshot(path="screenshots/e2e_v14_result.png")
            
        except Exception as e:
            print(f"❌ Playwright Error: {e}")
            await page.screenshot(path="screenshots/e2e_v14_error.png")
            print(f"🔗 Current URL: {page.url}")
        finally:
            await browser.close()

asyncio.run(run_e2e_v14())
