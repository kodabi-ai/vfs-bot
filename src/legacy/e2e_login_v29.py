import asyncio
from playwright.async_api import async_playwright
import cloudscraper

async def run_e2e_v29():
    print("🛡️ Step 1: Cloudscraper Bypass")
    scraper = cloudscraper.create_scraper(browser={'browser': 'chrome', 'custom_digest': 'cloudflare', 'delay': 10})
    try:
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
    
    print(f"🍪 Injecting {len(cf_cookies)} cookies...")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent=cf_ua, viewport={"width": 1920, "height": 1080})
        await context.add_cookies(cf_cookies)
        page = await context.new_page()
        
        try:
            target_url = "https://visa.vfsglobal.com/tur/tr/fra/login"
            print(f"🎯 Target: {target_url}")
            
            # 1. Init Angular Shell via root
            print("🌐 Initializing Angular Shell via root (/tur/tr/)...")
            await page.goto("https://visa.vfsglobal.com/tur/tr/", wait_until="load", timeout=15000)
            await page.wait_for_timeout(3000)
            
            # 2. Redirect to exact login route
            print("🔀 Redirecting to /tur/tr/fra/login...")
            await page.goto(target_url, wait_until="load", timeout=20000)
            print("⏳ Waiting 10s for SPA Login Component to hydrate...")
            await page.wait_for_timeout(10000)
            
            current_url = page.url
            title = await page.title()
            print(f"🔗 URL: {current_url}")
            print(f"📄 Title: {title}")
            
            # 3. Form Detection
            email_input = await page.query_selector('input[type="email"], input[name*="email"], input[placeholder*="e-posta"]')
            
            if email_input:
                print("✅ Login Form Bulundu!")
                await email_input.fill('{{VFS_EMAIL}}')
                
                password_input = await page.query_selector('input[type="password"]')
                if password_input:
                    await password_input.fill('{{VFS_PASSWORD}}')
                    
                print("🖱️ Login Butonuna Tıklanıyor...")
                login_btn = await page.query_selector('button[type="submit"]')
                if login_btn:
                    await login_btn.click()
                else:
                    await page.evaluate('document.querySelector("button")?.click()')
                    
                print("⏳ OTP Sayfası Bekleniyor...")
                await page.wait_for_timeout(15000)
                final_url = page.url
                print(f"🔗 Final URL: {final_url}")
                
                if 'otp' in final_url.lower() or 'verify' in final_url.lower():
                    print("✅ BAŞARILI: OTP Sayfasına Geçildi!")
                else:
                    print("⚠️ Hâlâ OTP'de değil. Screenshot kaydedildi.")
                    await page.screenshot(path="screenshots/e2e_v29_result.png")
            else:
                print("❌ Form Bulunamadı. SPA Re-init denemesi yapılıyor...")
                await page.reload(wait_until="load", timeout=15000)
                await page.wait_for_timeout(8000)
                
                email_input_retry = await page.query_selector('input[type="email"]')
                if email_input_retry:
                    print("✅ Re-init sonrası Form Bulundu! Dolduruluyor...")
                    await email_input_retry.fill('{{VFS_EMAIL}}')
                    password_input = await page.query_selector('input[type="password"]')
                    if password_input:
                        await password_input.fill('{{VFS_PASSWORD}}')
                    await page.evaluate('document.querySelector("button")?.click()')
                    await page.wait_for_timeout(10000)
                    print(f"🔗 Son URL: {page.url}")
                    await page.screenshot(path="screenshots/e2e_v29_result.png")
                else:
                    print("❌ Re-init sonrası bile form bulunamadı.")
                    await page.screenshot(path="screenshots/e2e_v29_result.png")
                    
        except Exception as e:
            print(f"❌ Playwright Error: {e}")
            await page.screenshot(path="screenshots/e2e_v29_error.png")
        finally:
            await browser.close()

asyncio.run(run_e2e_v29())
