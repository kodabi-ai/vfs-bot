import asyncio
from playwright.async_api import async_playwright
import cloudscraper

async def run_e2e_v13():
    print("🛡️ Step 1: Cloudscraper Bypass")
    scraper = cloudscraper.create_scraper(browser={'browser': 'chrome', 'custom_digest': 'cloudflare', 'delay': 10})
    try:
        resp = scraper.get("https://visa.vfsglobal.com/tur/tr/fra/login", timeout=30)
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
            print("🌐 Navigating to VFS Login (domcontentloaded)...")
            await page.goto("https://visa.vfsglobal.com/tur/tr/fra/login", wait_until="domcontentloaded", timeout=30000)
            
            print("⏳ Waiting 45s for Cloudflare Challenge to resolve...")
            await page.wait_for_timeout(45000)
            
            print("⏳ Waiting 15s for Angular UI to hydrate...")
            await page.wait_for_timeout(15000)
            
            # Check main frame and iframes
            print("🔍 Finding inputs via JS across all frames...")
            inputs_data = []
            for frame in page.frames:
                try:
                    frame_inputs = await frame.evaluate('''() => {
                        const all = Array.from(document.querySelectorAll('input'));
                        return all.map(el => ({
                            frame: frame.name || frame.url,
                            name: el.name, 
                            type: el.type, 
                            id: el.id, 
                            placeholder: el.placeholder
                        }));
                    }''')
                    inputs_data.extend(frame_inputs)
                except:
                    pass
                    
            print(f"📄 Found {len(inputs_data)} total inputs across frames:")
            for inp in inputs_data:
                print(f"   - Frame: {inp['frame'][:30]}... | {inp['name']} (type: {inp['type']})")
                
            email_input = next((i for i in inputs_data if 'email' in (i.get('name') or '').lower() or i.get('type') == 'email'), None)
            password_input = next((i for i in inputs_data if 'password' in (i.get('name') or '').lower() or i.get('type') == 'password'), None)
            
            if email_input:
                target_frame = next((f for f in page.frames if f.name == email_input['frame']), page.main_frame)
                selector = f'input[type="email"]'
                if email_input['name']:
                    selector = f'input[name="{email_input["name"]}"]'
                print(f"✍️ Filling email in frame: {email_input['frame']}")
                try:
                    await target_frame.fill(selector, 'mustafa.eke@live.com', timeout=10000)
                except:
                    await target_frame.evaluate(f'document.querySelector(\'input[name="{email_input["name"]}"]\')?.value = "mustafa.eke@live.com"')
            
            if password_input:
                target_frame = next((f for f in page.frames if f.name == password_input['frame']), page.main_frame)
                selector = f'input[type="password"]'
                if password_input['name']:
                    selector = f'input[name="{password_input["name"]}"]'
                print(f"✍️ Filling password in frame: {password_input['frame']}")
                try:
                    await target_frame.fill(selector, 'Vfsglobal!5561!', timeout=10000)
                except:
                    await target_frame.evaluate(f'document.querySelector(\'input[name="{password_input["name"]}"]\')?.value = "Vfsglobal!5561!"')
                
            print("🖱️ Clicking Login button...")
            login_btn = await page.query_selector('button[type="submit"]')
            if not login_btn:
                login_btn = await page.query_selector('button.login-btn')
            if not login_btn:
                login_btn = await page.query_selector('button#loginBtn')
            
            if login_btn:
                await login_btn.click(timeout=10000)
            else:
                print("⚠️ No button found, attempting JS click on first button...")
                await page.evaluate('document.querySelector("button")?.click()')
            
            print("⏳ Waiting for OTP page or redirection...")
            await page.wait_for_timeout(10000)
            
            current_url = page.url
            print(f"🔗 Final URL: {current_url}")
            
            if 'otp' in current_url.lower():
                print("✅ OTP Page Reached Successfully!")
            else:
                print("⚠️ Not on OTP page. Screenshot saved.")
                await page.screenshot(path="screenshots/e2e_v13_result.png")
            
        except Exception as e:
            print(f"❌ Playwright Error: {e}")
            await page.screenshot(path="screenshots/e2e_v13_error.png")
            print(f"🔗 Current URL: {page.url}")
        finally:
            await browser.close()

asyncio.run(run_e2e_v13())
