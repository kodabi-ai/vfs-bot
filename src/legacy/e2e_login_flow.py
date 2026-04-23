import asyncio
from playwright.async_api import async_playwright

async def run_e2e_flow():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            print("🚀 Navigating to VFS Login...")
            await page.goto("https://visa.vfsglobal.com/tur/tr/fra/login", wait_until="domcontentloaded")
            
            # Wait for Cloudflare challenge to resolve by looking for any input with a 'name' attribute
            print("⏳ Waiting for login form inputs...")
            try:
                # Give Cloudflare plenty of time to resolve the challenge
                await page.wait_for_selector("input[name]", timeout=60000)
                print("✅ Login form found!")
            except Exception as e:
                print(f"⚠️ Timeout waiting for inputs: {e}")
                await page.screenshot(path="screenshots/e2e_timeout.png")
                return

            # Fill credentials
            print("✍️ Filling credentials...")
            await page.fill('input[name="email"]', '{{VFS_EMAIL}}')
            await page.fill('input[name="password"]', '{{VFS_PASSWORD}}')
            
            # Click Login button
            print("🖱️ Clicking Login...")
            await page.click('button[type="submit"]')
            
            # Wait for OTP page
            print("⏳ Waiting for OTP page...")
            try:
                await page.wait_for_url("**/otp*", timeout=30000)
                print("✅ OTP Page Reached!")
            except Exception as e:
                print(f"⚠️ Did not reach OTP page: {e}")
                await page.screenshot(path="screenshots/e2e_after_submit.png")
                print(f"🔗 Current URL: {page.url}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            await browser.close()

asyncio.run(run_e2e_flow())
