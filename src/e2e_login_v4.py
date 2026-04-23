import asyncio
from playwright.async_api import async_playwright
import cloudscraper

async def run_e2e_v4():
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
    for c in cf_cookies:
        print(f"   - {c['name']} = {c['value'][:20]}...")
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
            await page.goto("https://visa.vfsglobal.com/tur/tr/fra/login", wait_until="networkidle", timeout=30000)
            
            # Check for 403
            content = await page.inner_html('body')
            if '403201' in content:
                print("⏳ Cloudflare challenge still active. Waiting for resolution...")
                try:
                    await page.wait_for_timeout(30000) # Wait 30s for JS challenge
                except:
                    pass
            
            # Try to find inputs again
            print("⏳ Waiting for form inputs...")
            try:
                await page.wait_for_selector("input[name]", timeout=20000)
                print("✅ Login form found!")
            except Exception as e:
                print(f"⚠️ Selector timeout: {e}")
                await page.screenshot(path="screenshots/e2e_v4_timeout.png")
                print("Dumping body snippet...")
                fresh_content = await page.inner_html('body')
                print(fresh_content[:500])
                return

            print("✍️ Filling credentials...")
            await page.fill('input[name="email"]', 'mustafa.eke@live.com')
            await page.fill('input[name="password"]', 'Vfsglobal!5561!')
            
            print("🖱️ Clicking Login...")
            await page.click('button[type="submit"]')
            
            print("⏳ Waiting for OTP page...")
            await page.wait_for_url("**/otp*", timeout=30000)
            print("✅ OTP Page Reached Successfully!")
            
        except Exception as e:
            print(f"❌ Playwright Error: {e}")
            await page.screenshot(path="screenshots/e2e_v4_error.png")
        finally:
            await browser.close()

asyncio.run(run_e2e_v4())
