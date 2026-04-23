import asyncio
from playwright.async_api import async_playwright
import cloudscraper

async def run_e2e_v5():
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
            print("🌐 Navigating to VFS Login (domcontentloaded)...")
            await page.goto("https://visa.vfsglobal.com/tur/tr/fra/login", wait_until="domcontentloaded", timeout=30000)
            
            # Explicit wait for Cloudflare JS Challenge (usually takes 10-30s)
            print("⏳ Waiting 30s for Cloudflare Challenge to resolve...")
            await page.wait_for_timeout(30000)
            
            print("🔍 Checking for form inputs...")
            try:
                await page.wait_for_selector('input[name="email"]', timeout=15000)
                print("✅ Email input found!")
            except Exception as e:
                print(f"⚠️ Email input timeout: {e}")
                await page.screenshot(path="screenshots/e2e_v5_timeout.png")
                content = await page.inner_html('body')
                print(f"Body snippet: {content[:500]}")
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
            await page.screenshot(path="screenshots/e2e_v5_error.png")
        finally:
            await browser.close()

asyncio.run(run_e2e_v5())
