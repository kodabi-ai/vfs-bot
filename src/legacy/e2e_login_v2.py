import asyncio
from playwright.async_api import async_playwright
import cloudscraper

async def run_e2e_flow_v2():
    # 1. Bypass Cloudflare using cloudscraper
    print("🛡️ Bypassing Cloudflare with cloudscraper...")
    scraper = cloudscraper.create_scraper()
    try:
        resp = scraper.get("https://visa.vfsglobal.com/tur/tr/fra/login", timeout=30)
        print(f"✅ Cloudscraper status: {resp.status_code}")
    except Exception as e:
        print(f"❌ Cloudscraper failed: {e}")
        return

    # Extract cookies
    cf_cookies = []
    for name, cookie in scraper.cookies.items():
        cf_cookies.append({
            "name": name,
            "value": cookie.value if hasattr(cookie, 'value') else cookie,
            "domain": ".vfsglobal.com",
            "path": "/"
        })
    print(f"🍪 Injecting {len(cf_cookies)} cookies into Playwright...")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        await context.add_cookies(cf_cookies)
        page = await context.new_page()
        
        try:
            print("🌐 Navigating to VFS Login (with cookies)...")
            await page.goto("https://visa.vfsglobal.com/tur/tr/fra/login", wait_until="domcontentloaded", timeout=30000)
            
            # Wait for inputs
            print("⏳ Waiting for form inputs...")
            await page.wait_for_selector("input[name]", timeout=15000)
            print("✅ Login form found!")

            print("✍️ Filling credentials...")
            await page.fill('input[name="email"]', 'mustafa.eke@live.com')
            await page.fill('input[name="password"]', 'Vfsglobal!5561!')
            
            print("🖱️ Clicking Login...")
            await page.click('button[type="submit"]')
            
            print("⏳ Waiting for OTP page...")
            try:
                await page.wait_for_url("**/otp*", timeout=30000)
                print("✅ OTP Page Reached Successfully!")
            except Exception as e:
                print(f"⚠️ Did not reach OTP page: {e}")
                await page.screenshot(path="screenshots/e2e_v2_after_submit.png")
                print(f"🔗 Current URL: {page.url}")
                
        except Exception as e:
            print(f"❌ Playwright Error: {e}")
            await page.screenshot(path="screenshots/e2e_v2_error.png")
        finally:
            await browser.close()

asyncio.run(run_e2e_flow_v2())