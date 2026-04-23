import asyncio
from playwright.async_api import async_playwright
import cloudscraper

async def run_e2e_v37():
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
                await page.wait_for_timeout(10000)
                print("✅ First Challenge Cleared.")
            except:
                print("⚠️ First Challenge Timeout, continuing...")

            # 3. Navigate to Login
            target_url = "https://visa.vfsglobal.com/tur/tr/fra/login"
            print(f"🔀 Navigating to Login: {target_url}...")
            await page.goto(target_url, wait_until="load", timeout=20000)
            
            # 4. Second Cloudflare Clear
            print("⏳ Clearing Second Cloudflare Challenge (Post-Nav)...")
            try:
                await page.locator('iframe[src*="challenge"]').first.wait_for(state="detached", timeout=20000)
                await page.wait_for_timeout(15000)
                print("✅ Second Challenge Cleared.")
            except:
                print("⚠️ Second Challenge Timeout, continuing...")

            # 5. V37: Check for 'Check your browser successfully' page
            print("⏳ V37: Checking for CF Success Page...")
            body_text = await page.inner_text("body", timeout=5000)
            
            if "Check your browser successfully" in body_text or "successfully" in body_text.lower():
                print("✅ CF Success Page Detected! Looking for Proceed Button...")
                # Try to find any clickable element to proceed
                try:
                    # Common selectors for CF proceed button
                    proceed_btn = await page.query_selector("input[type='button'], input[type='submit'], button, a[href='#']")
                    if proceed_btn:
                        print("🖱️ Clicking Proceed Button...")
                        await proceed_btn.click()
                        print("⏳ Waiting for redirect after click...")
                        await page.wait_for_timeout(20000) # Wait for redirect
                    else:
                        print("⚠️ No proceed button found, reloading...")
                        await page.reload(wait_until="load", timeout=20000)
                        await page.wait_for_timeout(15000)
                except Exception as e:
                    print(f"⚠️ Proceed Button Error: {e}")
                    await page.reload(wait_until="load", timeout=20000)
            
            # 6. Form Existence Loop
            print("⏳ V37: Robust Wait for Form...")
            element = None
            selectors = [
                'input[name="email"]',
                'input[type="email"]',
                'input[placeholder*="e-posta"]',
                'input[placeholder*="email"]',
                'input[name="username"]'
            ]
            
            max_retries = 3
            for attempt in range(max_retries + 1):
                if attempt > 0:
                    print(f"   🔄 Attempt {attempt+1}: Reloading...")
                    await page.reload(wait_until="load", timeout=20000)
                    await page.wait_for_timeout(15000)
                
                for i, sel in enumerate(selectors, 1):
                    try:
                        element = await page.wait_for_selector(sel, state="visible", timeout=30000)
                        print(f"✅ Form found with selector: {sel}")
                        break
                    except:
                        continue
                
                if element:
                    break

            if not element:
                print("❌ No form found after retries. Saving debug info...")
                html = await page.content()
                with open("/tmp/vfs_v37_dump.html", "w", encoding="utf-8") as f:
                    f.write(html)
                await page.screenshot(path="screenshots/e2e_v37_debug.png")
                await browser.close()
                return

            # 7. Fill Credentials
            await element.fill('mustafa.eke@live.com')
            print("📧 Email filled.")

            pass_sel = 'input[type="password"]'
            try:
                pass_el = await page.wait_for_selector(pass_sel, state="visible", timeout=5000)
                await pass_el.fill('Vfsglobal!5561!')
                print("🔒 Password filled.")
            except:
                print("⚠️ Password not visible.")

            # 8. Click Login
            print("🖱️ Clicking Login...")
            btn_sel = 'button[type="submit"], button:has-text("Login"), button:has-text("Giriş")'
            btn = await page.wait_for_selector(btn_sel, state="visible", timeout=10000)
            await btn.click()
            
            # 9. Wait for OTP/Dashboard
            print("⏳ Waiting for OTP/Dashboard...")
            await asyncio.sleep(20)
            
            final_url = page.url
            print(f"🔗 Final URL: {final_url}")
            
            if 'otp' in final_url.lower() or 'verify' in final_url.lower() or 'dashboard' in final_url.lower():
                print("✅ BAŞARILI: OTP veya Dashboard'a Geçildi!")
                await page.screenshot(path="screenshots/e2e_v37_success.png")
            else:
                print("⚠️ Beklenmeyen Yönlendirme.")
                await page.screenshot(path="screenshots/e2e_v37_result.png")

        except Exception as e:
            print(f"❌ Error: {e}")
            await page.screenshot(path="screenshots/e2e_v37_error.png")
        finally:
            await browser.close()

asyncio.run(run_e2e_v37())
