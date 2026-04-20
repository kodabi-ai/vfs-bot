import asyncio
import os
from playwright.async_api import async_playwright
from datetime import datetime


async def real_integration_login():
    """Real integration login test to trigger OTP email"""
    
    # Credentials
    email = os.getenv("VFS_EMAIL", "mustafa.eke@live.com")
    password = os.getenv("VFS_PASSWORD", "Vfsglobal!5561!")
    target_url = "https://visa.vfsglobal.com/tur/tr/fra/login"
    
    print(f"="*80)
    print(f"🚀 REAL INTEGRATION TEST - {datetime.now()}")
    print(f"="*80)
    print(f"📧 Email: {email}")
    print(f"📱 Phone: 5468224662")
    print(f"🌐 URL: {target_url}")
    print(f"="*80)
    
    async with async_playwright() as p:
        # Launch browser (headless=False for visual verification, headless=True for Docker)
        print("\n📌 Step 1: Launching Playwright Chromium...")
        browser = await p.chromium.launch(headless=False, slow_mo=500)
        context = await browser.new_context(viewport={"width": 1920, "height": 1080})
        page = await context.new_page()
        
        # Navigate to login page
        print("\n📌 Step 2: Navigating to VFS Global login page...")
        try:
            await page.goto(target_url, wait_until="networkidle", timeout=60000)
            print("✅ Page loaded successfully")
        except Exception as e:
            print(f"⚠️ Navigation issue: {e}")
        
        # Take screenshot
        await page.screenshot(path="screenshots/real_login_start.png")
        print("📸 Screenshot saved: screenshots/real_login_start.png")
        
        # Wait for login form
        print("\n📌 Step 3: Waiting for login form...")
        try:
            await page.wait_for_selector("#email", timeout=30000)
            print("✅ Login form found")
        except Exception as e:
            print(f"⚠️ Form selector issue: {e}")
        
        # Fill credentials
        print("\n📌 Step 4: Filling credentials...")
        await page.fill("#email", email)
        await page.fill("#password", password)
        print(f"✅ Credentials filled for {email}")
        
        # Check if submit button enabled
        print("\n📌 Step 5: Waiting for submit button...")
        try:
            await page.wait_for_selector("button[mat-stroked-button]:enabled", timeout=60000)
            await page.click("button[mat-stroked-button]")
            print("✅ Login submitted")
        except Exception as e:
            print(f"⚠️ Submit button issue: {e}")
        
        # Wait for OTP trigger
        print("\n📌 Step 6: Waiting for OTP email to be sent...")
        await page.wait_for_timeout(30000)  # Wait 30 seconds for OTP to be sent
        
        # Take screenshot of result
        await page.screenshot(path="screenshots/real_login_otp_sent.png")
        print("📸 Screenshot saved: screenshots/real_login_otp_sent.png")
        
        # Wait for OTP screen
        print("\n📌 Step 7: Checking OTP screen...")
        try:
            await page.wait_for_selector("#otp", timeout=120000)
            print("✅ OTP screen loaded")
        except Exception as e:
            print(f"⏳ OTP screen not ready: {e}")
        
        # Capture cookies for future use
        cookies = await page.cookies()
        print(f"\n📦 Cookies captured: {len(cookies)} cookies")
        
        # Wait for user to check email
        print("\n📬 Please check your email inbox for OTP!")
        print(f"   Email: {email}")
        print(f"   OTP should arrive within 1-2 minutes")
        
        # Keep browser open for user verification
        print("\n🔍 Browser kept open - please verify OTP email received")
        print("   Press Enter in terminal to close browser after verification")
        
        await asyncio.Event().wait()  # Wait for manual close
        
        await browser.close()


if __name__ == "__main__":
    print("Starting real integration login test...")
    asyncio.run(real_integration_login())
