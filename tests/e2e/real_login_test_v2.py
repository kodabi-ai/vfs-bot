import asyncio
import os
from playwright.async_api import async_playwright
from datetime import datetime


async def real_integration_login():
    """Real integration login test (Headless Mode) to trigger OTP email"""
    
    # Credentials
    email = os.getenv("VFS_EMAIL", "{{VFS_EMAIL}}")
    password = os.getenv("VFS_PASSWORD", "{{VFS_PASSWORD}}")
    target_url = "https://visa.vfsglobal.com/tur/tr/fra/login"
    
    print(f"="*80)
    print(f"🚀 REAL INTEGRATION TEST - {datetime.now()}")
    print(f"="*80)
    print(f"📧 Email: {email}")
    print(f"📱 Phone: {{VFS_PHONE}}")
    print(f"🌐 URL: {target_url}")
    print(f"="*80)
    
    async with async_playwright() as p:
        # Launch browser (headless=True for Docker container)
        print("\n📌 Step 1: Launching Playwright Chromium (Headless)...")
        browser = await p.chromium.launch(headless=True, slow_mo=300)
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        # Navigate to login page
        print("\n📌 Step 2: Navigating to VFS Global login page...")
        try:
            await page.goto(target_url, wait_until="networkidle", timeout=60000)
            print("✅ Page loaded successfully")
        except Exception as e:
            print(f"⚠️ Navigation issue: {e}")
            await page.screenshot(path="screenshots/real_login_start_fail.png")
        
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
        
        # Take screenshot after submit
        await page.screenshot(path="screenshots/real_login_after_submit.png")
        print("📸 Screenshot saved: screenshots/real_login_after_submit.png")
        
        # Wait for OTP trigger (30 seconds for email to be sent)
        print("\n📌 Step 6: Waiting for OTP email trigger (30s)...")
        await page.wait_for_timeout(30000)
        
        # Take screenshot of result
        await page.screenshot(path="screenshots/real_login_otp_trigged.png")
        print("📸 Screenshot saved: screenshots/real_login_otp_trigged.png")
        
        # Check page content for OTP indicators
        page_text = await page.content()
        if "otp" in page_text.lower() or "OTP" in page_text:
            print("✅ OTP page detected!")
        else:
            print("⏳ Waiting for OTP page to load...")
        
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
    print("Starting real integration login test (headless)...")
    asyncio.run(real_integration_login())
