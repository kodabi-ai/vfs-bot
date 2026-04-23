import asyncio
from playwright.async_api import async_playwright
import cloudscraper

async def run_e2e_v30():
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
            await page.wait_for_timeout(5000)
            
            # 2. Navigate to Login
            target_url = "https://visa.vfsglobal.com/tur/tr/fra/login"
            print(f"🔀 Navigating to Login: {target_url}...")
            await page.goto(target_url, wait_until="load", timeout=20000)
            
            # 3. Strict SPA Hydration Wait
            print("⏳ Waiting 10s for SPA Login Form to fully hydrate...")
            await page.wait_for_timeout(10000)
            
            current_url = page.url
            title = await page.title()
            print(f"🔗 URL: {current_url}")
            print(f"📄 Title: {title}")
            
            # 4. Robust Input Detection
            email_input = await page.query_selector('input[name="email"], input[name="username"], input[type="email"], input[placeholder*="e-posta"], input[placeholder*="email"]')
            
            if email_input:
                print("✅ Login Form Detected!")
                await email_input.fill('mustafa.eke@live.com')
                
                password_input = await page.query_selector('input[name="password"], input[type="password"]')
                if password_input:
                    await password_input.fill('Vfsglobal!5561!')
                    print("🔒 Credentials filled.")
                else:
                    print("⚠️ Password input not found via standard selectors. Saving HTML dump...")
                    html = await page.content()
                    with open("/tmp/vfs_v30_dump.html", "w") as f:
                        f.write(html)
                    print("💾 Dump saved to /tmp/vfs_v30_dump.html")
                    await page.screenshot(path="screenshots/e2e_v30_debug.png")
                    return # End if password missing to debug
                    
                print("🖱️ Clicking Login Button...")
                login_btn = await page.query_selector('button[type="submit"], button:has-text("Login"), button:has-text("Giriş")')
                if login_btn:
                    await login_btn.click()
                else:
                    await page.evaluate('document.querySelector("button")?.click()')
                
                print("⏳ Waiting for OTP/Dashboard Redirect...")
                await page.wait_for_timeout(15000)
                
                final_url = page.url
                print(f"🔗 Final URL: {final_url}")
                
                if 'otp' in final_url.lower() or 'verify' in final_url.lower() or 'dashboard' in final_url.lower():
                    print("✅ BAŞARILI: Login ve OTP Sayfasına Geçildi!")
                else:
                    print("⚠️ Yönlendirme beklenenden farklı. Screenshot kaydedildi.")
                    await page.screenshot(path="screenshots/e2e_v30_result.png")
            else:
                print("❌ Form Bulunamadı. /account-login rotasına geçiliyor...")
                await page.goto("https://visa.vfsglobal.com/tur/tr/fra/account-login", wait_until="load", timeout=15000)
                await page.wait_for_timeout(5000)
                
                email_input_backup = await page.query_selector('input[type="email"], input[name="email"]')
                if email_input_backup:
                    print("✅ account-login formu bulundu! Dolduruluyor...")
                    await email_input_backup.fill('mustafa.eke@live.com')
                    password_input = await page.query_selector('input[type="password"]')
                    if password_input:
                        await password_input.fill('Vfsglobal!5561!')
                    await page.evaluate('document.querySelector("button")?.click()')
                    await page.wait_for_timeout(10000)
                    print(f"🔗 Son URL: {page.url}")
                    await page.screenshot(path="screenshots/e2e_v30_result.png")
                else:
                    print("❌ account-login formu da bulunamadı. HTML dump kaydedildi.")
                    await page.screenshot(path="screenshots/e2e_v30_debug.png")
                    
        except Exception as e:
            print(f"❌ Playwright Error: {e}")
            await page.screenshot(path="screenshots/e2e_v30_error.png")
        finally:
            await browser.close()

asyncio.run(run_e2e_v30())
