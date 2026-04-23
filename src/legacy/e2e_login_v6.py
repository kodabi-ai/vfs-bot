import asyncio
from playwright.async_api import async_playwright
import cloudscraper

async def run_e2e_v6():
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
        cf_cookies.append({
            "name": name,
            "value": val,
            "domain": ".vfsglobal.com",
            "path": "/"
        })
    
    print(f"🍪 Injecting {len(cf_cookies)} cookies into Playwright...")
    print(f"🕵️  Using User-Agent: {cf_ua[:60]}...")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent=cf_ua,
            viewport={"width": 1920, "height": 1080}
        )
        await context.add_cookies(cf_cookies)
        page = await context.new_page()
        
        try:
            print("🌐 Navigating to VFS Login...")
            await page.goto("https://visa.vfsglobal.com/tur/tr/fra/login", wait_until="networkidle", timeout=45000)
            
            # Wait for Angular app to hydrate / Cloudflare JS to run
            print("⏳ Waiting 45s for Cloudflare & Angular to initialize...")
            await page.wait_for_timeout(45000)
            
            # Use JS to find inputs to bypass Angular encapsulation
            print("🔍 Finding inputs via JS...")
            inputs = await page.evaluate('''() => {
                return Array.from(document.querySelectorAll('input')).map(el => ({
                    name: el.name,
                    type: el.type,
                    id: el.id,
                    placeholder: el.placeholder
                }));
            }''')
            
            print(f"📄 Found {len(inputs)} inputs:")
            for inp in inputs:
                print(f"   - {inp['name']} (type: {inp['type']}, id: {inp['id']})")
                
            if not inputs:
                await page.screenshot(path="screenshots/e2e_v6_timeout.png")
                print("⚠️ No inputs found.")
                return

            email_input = next((i for i in inputs if 'email' in i['name'].lower()), None)
            password_input = next((i for i in inputs if 'password' in i['name'].lower()), None)
            
            if email_input:
                selector_email = f'input[name="{email_input["name"]}"]'
                print("✍️ Filling email...")
                await page.fill(selector_email, 'mustafa.eke@live.com')
            if password_input:
                selector_password = f'input[name="{password_input["name"]}"]'
                print("✍️ Filling password...")
                await page.fill(selector_password, 'Vfsglobal!5561!')
            
            print("🖱️ Clicking Login...")
            await page.click('button[type="submit"]')
            
            print("⏳ Waiting for OTP page...")
            await page.wait_for_url("**/otp*", timeout=30000)
            print("✅ OTP Page Reached Successfully!")
            
        except Exception as e:
            print(f"❌ Playwright Error: {e}")
            await page.screenshot(path="screenshots/e2e_v6_error.png")
        finally:
            await browser.close()

asyncio.run(run_e2e_v6())
