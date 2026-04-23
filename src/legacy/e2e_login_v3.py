import asyncio
from playwright.async_api import async_playwright
import cloudscraper

async def run_e2e_v3():
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
            await page.goto("https://visa.vfsglobal.com/tur/tr/fra/login", wait_until="domcontentloaded", timeout=30000)
            
            # Check if 403201 is still there
            await page.wait_for_timeout(5000)
            content = await page.inner_html('pre')
            print(f"🔍 Initial body check: {content[:50]}")
            
            if '403201' in content:
                print("⏳ Cloudflare still active. Waiting for resolution...")
                try:
                    await page.wait_for_selector('pre:not(:has-text("403201"))', timeout=30000)
                    print("✅ Cloudflare challenge resolved!")
                except:
                    print("⚠️ Still waiting...")
                    await page.wait_for_timeout(15000)

            print("⏳ Waiting for form inputs...")
            try:
                await page.wait_for_selector("input[name]", timeout=45000)
                print("✅ Login form found!")
            except Exception as e:
                print(f"⚠️ Selector timeout: {e}")
                await page.screenshot(path="screenshots/e2e_v3_timeout.png")
                return

            print("✍️ Filling credentials...")
            await page.fill('input[name="email"]', '{{VFS_EMAIL}}')
            await page.fill('input[name="password"]', '{{VFS_PASSWORD}}')
            
            print("🖱️ Clicking Login...")
            await page.click('button[type="submit"]')
            
            print("⏳ Waiting for OTP page...")
            await page.wait_for_url("**/otp*", timeout=30000)
            print("✅ OTP Page Reached Successfully!")
            
        except Exception as e:
            print(f"❌ Playwright Error: {e}")
            await page.screenshot(path="screenshots/e2e_v3_error.png")
        finally:
            await browser.close()

asyncio.run(run_e2e_v3())
