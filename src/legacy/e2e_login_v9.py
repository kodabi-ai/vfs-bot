import asyncio
from playwright.async_api import async_playwright
import cloudscraper

async def run_e2e_v9():
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
            
            # Explicit wait for Cloudflare JS Challenge (often takes 30-60s)
            print("⏳ Waiting 45s for Cloudflare Challenge to resolve...")
            await page.wait_for_timeout(45000)
            
            # Wait for Cloudflare iframe to disappear (challenge solved)
            try:
                await page.wait_for_selector("#cf-hcaptcha-container", state="hidden", timeout=30000)
                print("✅ Cloudflare Challenge Solved!")
            except:
                print("⚠️ Cloudflare iframe not found or already gone (Good)")

            print("⏳ Waiting 15s for Angular UI to hydrate...")
            await page.wait_for_timeout(15000)
            
            print("🔍 Finding inputs via JS (Bypasses Angular Encapsulation)...")
            inputs = await page.evaluate('''() => {
                const all = Array.from(document.querySelectorAll('input'));
                return all.map(el => ({
                    name: el.name, 
                    type: el.type, 
                    id: el.id, 
                    placeholder: el.placeholder
                }));
            }''')
            
            print(f"📄 Found {len(inputs)} inputs:")
            for inp in inputs:
                print(f"   - {inp['name']} (type: {inp['type']})")
                
            email_input = next((i for i in inputs if 'email' in i.get('name', '').lower()), None)
            password_input = next((i for i in inputs if 'password' in i.get('name', '').lower()), None)
            
            if email_input:
                print("✍️ Filling email...")
                selector = f'input[name="{email_input["name"]}"]'
                await page.fill(selector, 'mustafa.eke@live.com')
            
            if password_input:
                print("✍️ Filling password...")
                selector = f'input[name="{password_input["name"]}"]'
                await page.fill(selector, 'Vfsglobal!5561!')
                
            print("🖱️ Clicking Login...")
            await page.click('button[type="submit"]')
            
            print("⏳ Waiting for OTP page...")
            await page.wait_for_url("**/otp*", timeout=30000)
            print("✅ OTP Page Reached Successfully!")
            
        except Exception as e:
            print(f"❌ Playwright Error: {e}")
            await page.screenshot(path="screenshots/e2e_v9_error.png")
            print(f"🔗 Current URL: {page.url}")
            body = await page.inner_html('body')
            print(f"📄 Body snippet: {body[:500]}")
        finally:
            await browser.close()

asyncio.run(run_e2e_v9())