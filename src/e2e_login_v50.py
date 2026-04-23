import asyncio
from playwright.async_api import async_playwright
import cloudscraper

async def run_v50():
    print("🚀 V50: Content-Aware Login Strategy")
    
    # 1. Cloudscraper Bypass
    print("🛡️ Step 1: Cloudscraper Bypass")
    scraper = cloudscraper.create_scraper(browser={'browser': 'chrome', 'custom_digest': 'cloudflare', 'delay': 10})
    resp1 = scraper.get("https://visa.vfsglobal.com/tur/tr/", timeout=20)
    print(f"✅ Root Status: {resp1.status_code}")
    resp2 = scraper.get("https://visa.vfsglobal.com/tur/tr/fra/login", timeout=20)
    print(f"✅ Login Status: {resp2.status_code}")
    print('✅ Cloudscraper Bypass Successful.')
    except Exception as e:
        print(f"❌ Cloudscraper failed: {e}")
        return

    cf_cookies = []
    cf_ua = scraper.headers.get('User-Agent', '')
    for name, cookie in scraper.cookies.items():
        val = cookie.value if hasattr(cookie, 'value') else cookie
        cf_cookies.append({"name": name, "value": val, "domain": ".vfsglobal.com", "path": "/"})
    
    print(f"🍪 Injecting {len(cf_cookies)} cookies...")

    api_calls = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent=cf_ua, viewport={"width": 1920, "height": 1080})
        await context.add_cookies(cf_cookies)
        page = await context.new_page()
        
        def handle_response(response):
            if 'api' in response.url or 'auth' in response.url:
                api_calls.append({
                    'url': response.url,
                    'status': response.status,
                    'method': response.request.method
                })
                print(f"📡 API Call: {response.request.method} {response.url} -> {response.status}")

        page.on('response', handle_response)
        
        try:
            # 1. Root Shell Init
            print("🌐 Initializing Root Shell...")
            await page.goto("https://visa.vfsglobal.com/tur/tr/", wait_until="load", timeout=30000)
            
            # 2. Navigate to Login
            target_url = "https://visa.vfsglobal.com/tur/tr/fra/login"
            print(f"🔀 Navigating to Login...")
            await page.goto(target_url, wait_until="load", timeout=30000)
            
            # 3. Robust Cloudflare Bypass (Iframe Removal)
            print("⏳ Waiting for CF Iframe Removal...")
            try:
                await page.wait_for_selector("iframe[src*='challenges/']", state="detached", timeout=45000)
                print("✅ CF Iframe Detached! Form should be rendering...")
            except Exception as e:
                print(f"⚠️ Iframe removal wait failed: {e}")

            # 4. V50: Content-Aware Wait
            print("⏳ V50: Waiting for 'E-posta' text content to confirm SPA render...")
            try:
                await page.wait_for_function("document.body.innerText.includes('E-posta')", timeout=40000)
                print("✅ 'E-posta' text detected! Form is likely ready.")
            except Exception as e:
                print(f"⚠️ Content wait timeout: {e}")
                print("🔄 Reloading page to force refresh...")
                await page.reload(wait_until="load", timeout=30000)
                await page.wait_for_function("document.body.innerText.includes('E-posta')", timeout=30000)

            # 5. Locate Inputs
            print("🔍 Searching for visible inputs...")
            email_input = None
            password_input = None
            
            # Try to find visible inputs now that content is confirmed
            try:
                # Wait briefly for visible inputs after text detection
                email_input = await page.wait_for_selector("input[type='text'], input[type='email']", state="visible", timeout=10000)
                print("✅ Email Input Found.")
                
                password_input = await page.wait_for_selector("input[type='password']", state="visible", timeout=10000)
                print("✅ Password Input Found.")
            except Exception as e:
                print(f"⚠️ Input selector error: {e}")
                print("🔄 Trying broader fallback selector...")
                inputs = await page.query_selector_all("input:not([type='hidden'])")
                visible_inputs = []
                for inp in inputs:
                    try:
                        if await inp.is_visible():
                            visible_inputs.append(inp)
                    except Exception:
                        pass
                
                if len(visible_inputs) >= 2:
                    email_input = visible_inputs[0]
                    password_input = visible_inputs[1]
                    print("✅ Fallback Inputs Found.")
                else:
                    print("❌ No visible inputs found.")
                    await page.screenshot(path="screenshots/e2e_v50_debug.png")

            if email_input:
                print("📧 Filling credentials...")
                await email_input.fill('mustafa.eke@live.com')
                print("✅ Email filled.")
                
                if password_input:
                    await password_input.fill('Vfsglobal!5561!')
                    print("✅ Password filled.")
                else:
                    print("⚠️ No password input found.")

                print("🖱️ Looking for Login button...")
                # Check for specific button text or generic submit
                login_btn = await page.wait_for_selector('button:has-text("Giriş Yap"), button[type="submit"]', state="visible", timeout=5000)
                await login_btn.click()
                print("🔓 Login button clicked!")
                
                # Wait for result
                print("⏳ Waiting for Dashboard/OTP redirect...")
                await asyncio.sleep(20)
                
                final_url = page.url
                print(f"🔗 Final URL: {final_url}")
                
                if 'otp' in final_url or 'fra/dashboard' in final_url:
                    print("✅ Login Completed!")
                else:
                    print("⚠️ Unexpected redirect.")
                    await page.screenshot(path="screenshots/e2e_v50_result.png")
        
        except Exception as e:
            print(f"❌ Interaction failed: {e}")
            await page.screenshot(path="screenshots/e2e_v50_error.png")

    print("\n📡 API Calls Detected:")
    if api_calls:
        for call in api_calls:
            print(f"   {call['method']} {call['url']} -> {call['status']}")
    else:
        print("   No API calls detected.")

asyncio.run(run_v50())