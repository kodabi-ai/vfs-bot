import asyncio
from playwright.async_api import async_playwright
import cloudscraper

async def run_e2e_v35():
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
            # 1. Root Init
            print("🌐 Initializing Root Shell...")
            await page.goto("https://visa.vfsglobal.com/tur/tr/", wait_until="load", timeout=15000)
            
            # 2. First Cloudflare Clear
            print("⏳ Clearing First Cloudflare Challenge...")
            try:
                await page.locator('iframe[src*="challenge"]').first.wait_for(state="detached", timeout=20000)
                await page.wait_for_timeout(10000) # Extra buffer
                print("✅ First Challenge Cleared.")
            except:
                print("⚠️ First Challenge Timeout, continuing...")

            # 3. Navigate to Login
            target_url = "https://visa.vfsglobal.com/tur/tr/fra/login"
            print(f"🔀 Navigating to Login: {target_url}...")
            await page.goto(target_url, wait_until="load", timeout=20000)
            
            # 4. Second Cloudflare Clear (Crucial for SPA deep links)
            print("⏳ Clearing Second Cloudflare Challenge (Post-Nav)...")
            try:
                await page.locator('iframe[src*="challenge"]').first.wait_for(state="detached", timeout=20000)
                await page.wait_for_timeout(15000) # Extra buffer
                print("✅ Second Challenge Cleared.")
            except:
                print("⚠️ Second Challenge Timeout, continuing...")

            # 5. V35: Robust Waiting for Page Stability
            print("⏳ V35: Waiting for 'Successfully' text in page source...")
            try:
                await page.wait_for_function(
                    "() => document.body.innerText.includes('Successfully')",
                    timeout=30000
                )
                print("✅ Cloudflare Fully Passed (Text Match).")
            except:
                print("⚠️ 'Successfully' text not found in 30s, continuing...")

            # 6. V35: Wait for Angular Root (SPA Bootstrap)
            print("⏳ Waiting for Angular Root (`<vfs-app>`)...")
            try:
                await page.locator('vfs-app').first.wait_for(state="attached", timeout=15000)
                print("✅ Angular Root Attached. Waiting for Hydration...")
                await page.wait_for_timeout(10000)
            except:
                print("⚠️ Angular Root not found, continuing...")

            # 7. Find Form
            selectors = [
                'input[name="email"]',
                'input[type="email"]',
                'input[placeholder*="e-posta"]',
                'input[placeholder*="email"]',
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
                with open("/tmp/vfs_v35_dump.html", "w", encoding="utf-8") as f:
                    f.write(html)
                await page.screenshot(path="screenshots/e2e_v35_debug.png")
                await browser.close()
                return

            # 8. Fill Credentials
            await element.fill('{{VFS_EMAIL}}')
            print("📧 Email filled.")

            pass_sel = 'input[type="password"]'
            try:
                pass_el = await page.wait_for_selector(pass_sel, state="visible", timeout=5000)
                await pass_el.fill('{{VFS_PASSWORD}}')
                print("🔒 Password filled.")
            except:
                print("⚠️ Password not visible.")

            # 9. Click Login
            print("🖱️ Clicking Login...")
            btn_sel = 'button[type="submit"], button:has-text("Login"), button:has-text("Giriş")'
            btn = await page.wait_for_selector(btn_sel, state="visible", timeout=10000)
            await btn.click()
            
            # 10. Wait for OTP/Dashboard
            print("⏳ Waiting for OTP/Dashboard...")
            await asyncio.sleep(20)
            
            final_url = page.url
            print(f"🔗 Final URL: {final_url}")
            
            if 'otp' in final_url.lower() or 'verify' in final_url.lower() or 'dashboard' in final_url.lower():
                print("✅ BAŞARILI: OTP veya Dashboard'a Geçildi!")
                await page.screenshot(path="screenshots/e2e_v35_success.png")
            else:
                print("⚠️ Beklenmeyen Yönlendirme.")
                await page.screenshot(path="screenshots/e2e_v35_result.png")

        except Exception as e:
            print(f"❌ Error: {e}")
            await page.screenshot(path="screenshots/e2e_v35_error.png")
        finally:
            await browser.close()

asyncio.run(run_e2e_v35())
