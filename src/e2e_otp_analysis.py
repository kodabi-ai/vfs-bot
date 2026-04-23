import asyncio
from playwright.async_api import async_playwright
import cloudscraper

async def run_otp_analysis():
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
            # 1. Root Init
            print("🌐 Initializing Root Shell...")
            await page.goto("https://visa.vfsglobal.com/tur/tr/", wait_until="networkidle", timeout=30000)
            
            # 2. Navigate to Login
            target_url = "https://visa.vfsglobal.com/tur/tr/fra/login"
            print(f"🔀 Navigating to Login...")
            await page.goto(target_url, wait_until="networkidle", timeout=30000)
            
            # 3. Robust Cloudflare Bypass (Iframe Removal)
            print("⏳ Waiting for CF Iframe Removal...")
            try:
                await page.wait_for_selector("iframe[src*='challenges/']", state="detached", timeout=60000)
                print("✅ CF Iframe Detached! Form should be rendering...")
            except Exception as e:
                print(f"⚠️ Iframe removal wait failed: {e}")

            # 4. V49: Spinner Removal & Label-based Detection
            print("⏳ V49: Waiting for Loading Overlays to Disappear...")
            try:
                await page.wait_for_selector(".spinner, .loading, .loader", state="detached", timeout=30000)
                print("✅ Overlays Cleared!")
            except Exception as e:
                print(f"⚠️ Overlay removal failed: {e}")

            print("⏳ V49: Searching for Inputs via Labels...")
            email_input = None
            password_input = None
            
            # V49 Strategy: Find labels containing keywords, then look for sibling inputs
            labels = await page.query_selector_all("label, span")
            input_candidates = await page.query_selector_all("input")
            
            for lbl in labels:
                try:
                    text = await lbl.inner_text()
                    if "E-posta" in text or "Şifre" in text:
                        # Look for immediate sibling input
                        sibling = await lbl.evaluate_handle("el => el.nextElementSibling")
                        if sibling and await sibling.evaluate("el => el.tagName === 'INPUT'"):
                            if "E-posta" in text:
                                email_input = sibling
                            else:
                                password_input = sibling
                            print(f"✅ Found '{text}' input at sibling")
                except Exception:
                    continue

            # Fallback: If label search didn't work, try finding the first two inputs manually
            if not email_input and input_candidates:
                print("⚠️ Label search failed. Manual fallback to input candidates...")
                visible_inputs = []
                for inp in input_candidates:
                    try:
                        if await inp.is_visible():
                            visible_inputs.append(inp)
                    except Exception:
                        pass
                
                if len(visible_inputs) >= 2:
                    email_input = visible_inputs[0]
                    password_input = visible_inputs[1]
                    print("✅ Found 2 visible inputs via fallback.")
                elif len(visible_inputs) == 1:
                    email_input = visible_inputs[0]
                    print("✅ Found 1 visible input via fallback.")

            if email_input:
                print("📧 Filling credentials...")
                await email_input.fill('mustafa.eke@live.com')
                print("✅ Email filled.")
                
                if password_input:
                    await password_input.fill('Vfsglobal!5561!')
                    print("✅ Password filled.")
                else:
                    print("⚠️ No password input found, trying to find type='password'...")
                    try:
                        pwd = await page.wait_for_selector('input[type="password"]', state="visible", timeout=5000)
                        await pwd.fill('Vfsglobal!5561!')
                        print("✅ Password filled (via type selector).")
                    except Exception:
                        pass

                print("🖱️ Looking for Login button...")
                login_btn = await page.wait_for_selector('button[type="submit"], input[type="submit"]', state="visible", timeout=5000)
                await login_btn.click()
                print("🔓 Login button clicked!")
                
                # Wait for result
                print("⏳ Waiting for Dashboard/OTP redirect...")
                await asyncio.sleep(20)
                
                final_url = page.url
                print(f"🔗 Final URL: {final_url}")
                
                if 'otp' in final_url:
                    print("✅ OTP Page Loaded. Searching for OTP Trigger...")
                    await asyncio.sleep(5)
                    
                    otp_btn_selector = "button:has-text('Gönder'), button:has-text('Send OTP'), button:has-text('Email OTP'), button:has-text('OTP')"
                    otp_btn = await page.query_selector(otp_btn_selector)
                    
                    if otp_btn:
                        print("✅ OTP Trigger Button Found! Clicking...")
                        await otp_btn.click()
                        await asyncio.sleep(5)
                        print("✅ OTP Trigger Clicked. Waiting for API Call...")
                    else:
                        print("⚠️ OTP Trigger Button NOT Found. Saving HTML...")
                        html = await page.content()
                        with open("/tmp/vfs_otp_analysis.html", "w", encoding="utf-8") as f:
                            f.write(html)
                        await page.screenshot(path="screenshots/e2e_otp_analysis.png")
                        return

                if 'fra/dashboard' in final_url or 'otp' in final_url:
                    print("✅ Login Completed!")
                else:
                    print("⚠️ Unexpected redirect.")
                    await page.screenshot(path="screenshots/e2e_otp_result.png")
                        
        except Exception as e:
            print(f"❌ Form interaction failed: {e}")
            print("📸 Saving debug screenshot...")
            await page.screenshot(path="screenshots/e2e_v49_debug.png")

    print("\n📡 API Calls Detected:")
    if api_calls:
        for call in api_calls:
            print(f"   {call['method']} {call['url']} -> {call['status']}")
    else:
        print("   No API calls detected during this run.")

asyncio.run(run_otp_analysis())
