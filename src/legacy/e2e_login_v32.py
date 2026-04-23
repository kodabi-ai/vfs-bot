import asyncio
from playwright.async_api import async_playwright
import cloudscraper

async def run_e2e_v32():
    print("🛡️ Step 1: Cloudscraper Bypass")
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
            # 1. Init Shell
            print("🌐 Initializing Angular Shell...")
            await page.goto("https://visa.vfsglobal.com/tur/tr/", wait_until="load", timeout=15000)
            await page.wait_for_timeout(3000)
            
            # 2. Navigate to Login
            target_url = "https://visa.vfsglobal.com/tur/tr/fra/login"
            print(f"🔀 Navigating to Login: {target_url}...")
            await page.goto(target_url, wait_until="load", timeout=20000)
            
            # 3. Wait for Cloudflare Challenge to Detach
            print("⏳ Waiting for Cloudflare Challenge to clear...")
            try:
                await page.locator('iframe[src*="challenge"]').first.wait_for(state="detached", timeout=15000)
                print("✅ Cloudflare cleared.")
            except:
                print("⚠️ Cloudflare iframe wait timed out, continuing...")

            # 4. Wait for Body/App Root to stabilize
            print("⏳ Waiting for SPA rendering...")
            try:
                await page.wait_for_selector("body", state="visible", timeout=10000)
            except:
                pass

            # 5. Find Form - Multiple attempts
            selectors = [
                'input[name="email"]',
                'input[type="email"]',
                'input[placeholder*="E-posta"]',
                'input[placeholder*="e-posta"]',
                'input[name="username"]'
            ]
            
            element = None
            for i, sel in enumerate(selectors, 1):
                print(f"   Check {i}: {sel}...")
                try:
                    element = await page.wait_for_selector(sel, state="visible", timeout=5000)
                    print(f"✅ Form found with selector: {sel}")
                    break
                except:
                    continue
            
            if not element:
                print("❌ No form found. Saving debug info...")
                html = await page.content()
                with open("/tmp/vfs_v32_dump.html", "w", encoding="utf-8") as f:
                    f.write(html)
                await page.screenshot(path="screenshots/e2e_v32_debug.png")
                await browser.close()
                return

            # 6. Fill
            email = element.get_attribute("name") or "email_field"
            await element.fill('{{VFS_EMAIL}}')
            print(f"📧 Email filled to: {email}")

            # Password field
            pass_sel = 'input[type="password"]'
            try:
                pass_el = await page.wait_for_selector(pass_sel, state="visible", timeout=5000)
                await pass_el.fill('{{VFS_PASSWORD}}')
                print("🔒 Password filled.")
            except:
                print("⚠️ Password not visible.")

            # 7. Click Login
            print("🖱️ Clicking Login...")
            btn_sel = 'button[type="submit"], button:has-text("Login"), button:has-text("Giriş")'
            btn = await page.wait_for_selector(btn_sel, state="visible", timeout=10000)
            await btn.click()
            
            # 8. Wait for Result
            print("⏳ Waiting for OTP/Dashboard...")
            await asyncio.sleep(15)
            
            final_url = page.url
            print(f"🔗 Final URL: {final_url}")
            
            if 'otp' in final_url.lower() or 'verify' in final_url.lower() or 'dashboard' in final_url.lower():
                print("✅ BAŞARILI: OTP veya Dashboard'a Geçildi!")
            else:
                print("⚠️ Beklenmeyen Yönlendirme.")
                await page.screenshot(path="screenshots/e2e_v32_result.png")

        except Exception as e:
            print(f"❌ Error: {e}")
            await page.screenshot(path="screenshots/e2e_v32_error.png")
        finally:
            await browser.close()

asyncio.run(run_e2e_v32())
