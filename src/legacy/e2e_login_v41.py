import asyncio
from playwright.async_api import async_playwright
import cloudscraper

async def run_e2e_v41():
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
            print("🌐 Initializing Root Shell (Network Idle)...")
            await page.goto("https://visa.vfsglobal.com/tur/tr/", wait_until="networkidle", timeout=30000)
            
            # 2. Navigate to Login
            target_url = "https://visa.vfsglobal.com/tur/tr/fra/login"
            print(f"🔀 Navigating to Login: {target_url}...")
            await page.goto(target_url, wait_until="networkidle", timeout=30000)
            
            # 3. V41: Robust Cloudflare Bypass (Iframe & JS Click)
            print("⏳ V41: Robust Cloudflare 403201 Loop (Iframe Detection)...")
            for attempt in range(4):
                print(f"   🔁 Check {attempt+1}: Is on 403201 page?")
                
                body_text = ""
                try:
                    body_text = await page.inner_text("body", timeout=3000)
                except:
                    pass
                
                if "403201" in body_text or "Check your browser successfully" in body_text:
                    print("   ✅ CF Challenge Detected! Inspecting DOM...")
                    
                    clicked = False
                    try:
                        # V41: Check for Iframe
                        iframe = await page.query_selector("iframe")
                        target_frame = page
                        
                        if iframe:
                            print("   🕵️ Detected CF Iframe! Attempting frame switch...")
                            try:
                                frame = await iframe.content_frame()
                                if frame:
                                    target_frame = frame
                                    print("   ✅ Successfully switched to Iframe context.")
                                else:
                                    print("   ⚠️ content_frame() returned None.")
                            except Exception as e:
                                print(f"   ⚠️ Frame switch failed: {e}")

                        # Search for button in target frame
                        btn = await target_frame.query_selector("input[type='button'], input[type='submit'], button")
                        if not btn:
                            btn = await target_frame.query_selector("a") # Fallback to link
                        
                        if btn:
                            print("   🖱️ Found element, clicking...")
                            await btn.click()
                            clicked = True
                        else:
                            print("   🖱️ No element in frame, trying JS direct click...")
                            js_click = """
                                const btn = document.querySelector('input[type="button"], input[type="submit"]');
                                if (btn) { btn.click(); return true; }
                                return false;
                            """
                            result = await page.evaluate(js_click)
                            if result:
                                clicked = True
                                print("   ✅ JS Click Success!")
                    except Exception as e:
                        print(f"   ⚠️ Click logic error: {e}")
                    
                    if clicked:
                        print("   ⏳ Waiting for page reload/stability (10s)...")
                        await asyncio.sleep(10)
                    else:
                        print("   ⚠️ No click successful, reloading (10s)...")
                        await page.reload(wait_until="domcontentloaded", timeout=20000)
                        await asyncio.sleep(10)
                else:
                    print("   ✅ Challenge Cleared! Navigating to Form...")
                    break # Exit loop if page changed

            # 4. Form Existence (Post-Challenge)
            print("⏳ V41: Waiting for Login Form...")
            try:
                # Wait for email input specifically
                email_input = await page.wait_for_selector('input[type="email"]', state="visible", timeout=15000)
                print("✅ Email input found!")
                
                # Fill credentials
                email_input.fill('{{VFS_EMAIL}}')
                print("📧 Email filled.")
                
                # Find password input
                pass_input = await page.wait_for_selector('input[type="password"]', state="visible", timeout=10000)
                pass_input.fill('{{VFS_PASSWORD}}')
                print("🔒 Password filled.")
                
                # Click Login button
                print("🖱️ Looking for Login button...")
                login_btn = await page.wait_for_selector('button[type="submit"]', state="visible", timeout=5000)
                await login_btn.click()
                print("🔓 Login button clicked!")
                
                # Wait for result
                print("⏳ Waiting for Dashboard/OTP redirect...")
                await asyncio.sleep(20)
                
                final_url = page.url
                print(f"🔗 Final URL: {final_url}")
                if 'fra/dashboard' in final_url or 'otp' in final_url:
                    print("✅ BAŞARILI: Login Completed!")
                else:
                    print("⚠️ Unexpected redirect.")
                    await page.screenshot(path="screenshots/e2e_v41_result.png")
                    
            except Exception as e:
                print(f"❌ Form interaction failed: {e}")
                print("📸 Saving debug screenshot...")
                await page.screenshot(path="screenshots/e2e_v41_debug.png")

        except Exception as e:
            print(f"❌ Error: {e}")
            await page.screenshot(path="screenshots/e2e_v41_error.png")
        finally:
            await browser.close()

asyncio.run(run_e2e_v41())
