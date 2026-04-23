import asyncio
from playwright.async_api import async_playwright
import cloudscraper

async def run_e2e_v7():
    print("🛡️ Step 1: Cloudscraper Bypass")
    scraper = cloudscraper.create_scraper(
        browser={'browser': 'chrome', 'custom_digest': 'cloudflare', 'delay': 10}
    )
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
            await page.goto("https://visa.vfsglobal.com/tur/tr/fra/login", wait_until="networkidle", timeout=60000)
            
            print("⏳ Waiting 10s for Angular UI to fully render...")
            await page.wait_for_timeout(10000)
            
            print("🔍 Finding inputs via JS...")
            inputs = await page.evaluate('''() => Array.from(document.querySelectorAll('input')).map(el => ({name: el.name, type: el.type, id: el.id}))''')
            for inp in inputs:
                print(f"   - {inp['name']}")
                
            email_input = next((i for i in inputs if 'email' in i['name'].lower()), None)
            password_input = next((i for i in inputs if 'password' in i['name'].lower()), None)
            
            if email_input:
                print("✍️ Filling email...")
                await page.fill(f'input[name="{email_input["name"]}"]', '{{VFS_EMAIL}}')
            if password_input:
                print("✍️ Filling password...")
                await page.fill(f'input[name="{password_input["name"]}"]', '{{VFS_PASSWORD}}')
                
            print("🖱️ Clicking Login...")
            await page.click('button[type="submit"]')
            
            print("⏳ Waiting for OTP page...")
            await page.wait_for_url("**/otp*", timeout=30000)
            print("✅ OTP Page Reached Successfully!")
            
        except Exception as e:
            print(f"❌ Playwright Error: {e}")
            await page.screenshot(path="screenshots/e2e_v7_error.png")
        finally:
            await browser.close()

asyncio.run(run_e2e_v7())
