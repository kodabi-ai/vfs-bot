import asyncio
from playwright.async_api import async_playwright
import cloudscraper
import os

async def run_e2e_v28():
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
            # Strategy: Force navigation to explicit account-login if login fails
            # VFS Global SPA often redirects /login to /account-login
            pages_to_try = [
                "https://visa.vfsglobal.com/tur/tr/fra/login",
                "https://visa.vfsglobal.com/tur/tr/fra/account-login"
            ]
            
            target_found = False
            for url in pages_to_try:
                print(f"🌐 Trying route: {url}...")
                await page.goto(url, wait_until="load", timeout=30000)
                await page.wait_for_timeout(5000)
                
                # Check for login form or email input
                email_input = await page.query_selector('input[type="email"], input[name*="email"], input[placeholder*="e-posta"], input[placeholder*="email"]')
                
                if email_input:
                    print("✅ Login form detected!")
                    target_found = True
                    break
                else:
                    print(f"⚠️ Login form NOT found on {url}. Checking if on Search page...")
                    search_handler = await page.query_selector('input[name="vendor-search-handler"]')
                    if search_handler:
                        print("🔄 On Search page. Clicking Login button...")
                        login_btn = await page.query_selector('button:has-text("Login"), button:has-text("Giriş"), a:has-text("Login"), a:has-text("Giriş")')
                        if login_btn:
                            await login_btn.click()
                            await page.wait_for_timeout(5000)
                            email_input = await page.query_selector('input[type="email"]')
                            if email_input:
                                print("✅ Successfully routed to Login!")
                                target_found = True
                                break
                        else:
                            print("⚠️ No login button found on Search page. Trying manual route...")
                            await page.goto("https://visa.vfsglobal.com/tur/tr/fra/account-login", wait_until="load", timeout=20000)
                            await page.wait_for_timeout(5000)
                            email_input = await page.query_selector('input[type="email"]')
                            if email_input:
                                print("✅ Successfully routed to Login!")
                                target_found = True
                                break
                            else:
                                print("⚠️ Still no email input. Saving HTML dump.")
                                await page.screenshot(path="screenshots/e2e_v28_debug.png")
                                html_dump = await page.content()
                                with open("/tmp/vfs_v28_dump.html", "w", encoding="utf-8") as f:
                                    f.write(html_dump)
                                print(f"📝 HTML dump saved to /tmp/vfs_v28_dump.html")
                    else:
                        print(f"⚠️ Not on login or search page. Saving screenshot.")
                        await page.screenshot(path=f"screenshots/e2e_v28_{url.split('/')[-1]}.png")
            
            if target_found:
                print("✍️ Filling credentials...")
                await email_input.fill('mustafa.eke@live.com')
                
                password_input = await page.query_selector('input[type="password"]')
                if password_input:
                    await password_input.fill('Vfsglobal!5561!')
                    await password_input.fill('Vfsglobal!5561!') # Double fill for some SPAs
                
                print("🖱️ Clicking Login button...")
                login_btn = await page.query_selector('button[type="submit"]')
                if not login_btn:
                    login_btn = await page.query_selector('button:has-text("Login"), button:has-text("Giriş")')
                
                if login_btn:
                    try:
                        await login_btn.click(timeout=10000)
                    except:
                        await login_btn.evaluate('el => el.click()')
                
                print("⏳ Waiting for OTP/Redirect...")
                await page.wait_for_timeout(10000)
                
                final_url = page.url
                print(f"🔗 Final URL: {final_url}")
                
                if 'otp' in final_url.lower() or 'verify' in final_url.lower() or 'dashboard' in final_url.lower():
                    print("✅ OTP/Dashboard Reached Successfully!")
                else:
                    print("⚠️ Not on OTP page. Screenshot saved.")
                    await page.screenshot(path="screenshots/e2e_v28_result.png")
                    print("💾 HTML dump available at /tmp/vfs_v28_dump.html")
            else:
                print("❌ Failed to find login form on any route.")
                
        except Exception as e:
            print(f"❌ Playwright Error: {e}")
            await page.screenshot(path="screenshots/e2e_v28_error.png")
        finally:
            await browser.close()

asyncio.run(run_e2e_v28())
