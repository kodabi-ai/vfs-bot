import asyncio
from playwright.async_api import async_playwright
import cloudscraper

async def run_e2e_v31():
    print("🛡️ Step 1: Cloudscraper Bypass (Fresh Session)")
    scraper = cloudscraper.create_scraper(browser={'browser': 'chrome', 'custom_digest': 'cloudflare', 'delay': 10})
    try:
        scraper.get("https://visa.vfsglobal.com/tur/tr/", timeout=20)
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
            # 1. Init Angular Shell
            print("🌐 Initializing Angular Shell via root (/tur/tr/)...")
            await page.goto("https://visa.vfsglobal.com/tur/tr/", wait_until="load", timeout=15000)
            
            # 2. Navigate to Login
            target_url = "https://visa.vfsglobal.com/tur/tr/fra/login"
            print(f"🔀 Navigating to Login: {target_url}...")
            await page.goto(target_url, wait_until="load", timeout=20000)
            
            # 3. Robust Wait for Cloudflare Challenge to Clear
            print("⏳ Waiting for Cloudflare Challenge to clear...")
            try:
                # Wait for iframe to disappear
                await page.locator('iframe[src*="challenge"]').first.wait_for(state="detached", timeout=15000)
                print("✅ Cloudflare cleared.")
            except:
                print("⚠️ Cloudflare iframe wait timed out, continuing...")

            # 4. Wait for Login Form (Specific selector)
            print("⏳ Waiting for Login Form to render (Max 30s)...")
            selectors = [
                'input[name="email"]',
                'input[type="email"]',
                'input[placeholder*="E-posta"]',
                'input[placeholder*="e-posta"]',
                'input[name="username"]'
            ]
            
            element = None
            for sel in selectors:
                print(f"   Trying selector: {sel}...")
                try:
                    element = await page.wait_for_selector(sel, state="visible", timeout=5000)
                    print(f"✅ Form found with selector: {sel}")
                    break
                except:
                    continue
            
            if not element:
                print("❌ No form selector found in 30s. Saving HTML dump...")
                html = await page.content()
                with open("/tmp/vfs_v31_dump.html", "w", encoding="utf-8") as f:
                    f.write(html)
                await page.screenshot(path="screenshots/e2e_v31_debug.png")
                await browser.close()
                return

            # 5. Fill Credentials
            await element.fill('{{VFS_EMAIL}}')
            print("📧 Email filled.")

            password_selector = 'input[type="password"], input[name="password"]'
            pass_element = await page.wait_for_selector(password_selector, state="visible", timeout=5000)
            if pass_element:
                await pass_element.fill('{{VFS_PASSWORD}}')
                print("🔒 Password filled.")
            else:
                print("⚠️ Password field not visible.")

            # 6. Click Login
            login_selector = 'button[type="submit"], button:has-text("Login"), button:has-text("Giriş")'
            login_btn = await page.wait_for_selector(login_selector, state="visible", timeout=10000)
            await login_btn.click()
            print("🖱️ Login clicked.")

            # 7. Wait for OTP/Redirect
            print("⏳ Waiting for OTP/Dashboard Redirect...")
            await asyncio.sleep(20)
            
            final_url = page.url
            print(f"🔗 Final URL: {final_url}")
            
            if 'otp' in final_url.lower() or 'verify' in final_url.lower() or 'dashboard' in final_url.lower():
                print("✅ BAŞARILI: Login ve OTP Sayfasına Geçildi!")
            else:
                print("⚠️ Yönlendirme beklenenden farklı. Screenshot kaydedildi.")
                await page.screenshot(path="screenshots/e2e_v31_result.png")

        except Exception as e:
            print(f"❌ Playwright Error: {e}")
            await page.screenshot(path="screenshots/e2e_v31_error.png")
        finally:
            await browser.close()

asyncio.run(run_e2e_v31())
