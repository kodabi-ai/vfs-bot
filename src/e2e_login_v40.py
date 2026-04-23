import asyncio
from playwright.async_api import async_playwright
import cloudscraper

async def run_e2e_v40():
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
            
            # 3. V40: Robust Cloudflare Bypass Loop (Generic Click)
            print("⏳ V40: Robust Cloudflare 403201 Loop...")
            for attempt in range(4):
                print(f"   🔁 Check {attempt+1}: Is on 403201 page?")
                
                body_text = ""
                try:
                    body_text = await page.inner_text("body", timeout=3000)
                except:
                    pass
                
                if "403201" in body_text or "Check your browser successfully" in body_text:
                    print("   ✅ CF Challenge Detected! Clicking generic element...")
                    
                    # V40 Strategy: Click any visible button or link
                    clicked = False
                    try:
                        # Try clicking a button first
                        btn = await page.query_selector("button, input[type='button'], input[type='submit']")
                        if btn:
                            await btn.click()
                            print("   🖱️ Button Clicked!")
                            clicked = True
                        else:
                            # Try clicking a link (sometimes CF uses <a href='#'>) 
                            link = await page.query_selector("a")
                            if link:
                                await link.click()
                                print("   🖱️ Link Clicked!")
                                clicked = True
                    except Exception as e:
                        print(f"   ⚠️ Click failed: {e}")
                    
                    if clicked:
                        print("   ⏳ Waiting for redirection (10s)...")
                        await asyncio.sleep(10)
                    else:
                        print("   ⚠️ No element found, reloading (10s)...")
                        await page.reload(wait_until="domcontentloaded", timeout=20000)
                        await asyncio.sleep(10)
                else:
                    print("   ✅ Challenge Cleared!")
                    break # Exit loop if page changed

            # 4. Form Existence (Post-Challenge)
            print("⏳ V40: Waiting for Login Form...")
            try:
                # Wait for email input specifically
                email_input = await page.wait_for_selector('input[type="email"]', state="visible", timeout=15000)
                print("✅ Email input found!")
                
                # Fill credentials
                email_input.fill('mustafa.eke@live.com')
                print("📧 Email filled.")
                
                # Find password input
                pass_input = await page.wait_for_selector('input[type="password"]', state="visible", timeout=10000)
                pass_input.fill('Vfsglobal!5561!')
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
                    await page.screenshot(path="screenshots/e2e_v40_result.png")
                    
            except Exception as e:
                print(f"❌ Form interaction failed: {e}")
                print("📸 Saving debug screenshot...")
                await page.screenshot(path="screenshots/e2e_v40_debug.png")

        except Exception as e:
            print(f"❌ Error: {e}")
            await page.screenshot(path="screenshots/e2e_v40_error.png")
        finally:
            await browser.close()

asyncio.run(run_e2e_v40())
