import asyncio
import logging
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class VFSLoginBot:
    def __init__(self, email: str = None, password: str = None):
        from config import EMAIL, PASSWORD
        self.email = email or EMAIL
        self.password = password or PASSWORD
        self.scraper = None
        self.browser = None
        self.context = None
        self.page = None

    async def initialize_scraper(self):
        import cloudscraper
        logger.info("🛡️ Step 1: Initializing Cloudscraper...")
        self.scraper = cloudscraper.create_scraper(
            browser={'browser': 'chrome', 'custom_digest': 'cloudflare', 'delay': 10}
        )
        try:
            resp1 = self.scraper.get("https://visa.vfsglobal.com/tur/tr/", timeout=20)
            logger.info(f"✅ Root Status: {resp1.status_code}")
            resp2 = self.scraper.get("https://visa.vfsglobal.com/tur/tr/fra/login", timeout=20)
            logger.info(f"✅ Login Status: {resp2.status_code}")
            logger.info("✅ Cloudscraper Bypass Successful.")
        except Exception as e:
            logger.error(f"❌ Cloudscraper failed: {e}")
            raise

    def extract_cookies(self) -> list:
        cf_cookies = []
        cf_ua = self.scraper.headers.get('User-Agent', '')
        for name, cookie in self.scraper.cookies.items():
            val = cookie.value if hasattr(cookie, 'value') else cookie
            cf_cookies.append({
                "name": name,
                "value": val,
                "domain": ".vfsglobal.com",
                "path": "/"
            })
        logger.info(f"🍪 Extracted {len(cf_cookies)} cookies.")
        return cf_cookies, cf_ua

    async def initialize_browser(self, cookies: list, ua: str):
        from playwright.async_api import async_playwright
        logger.info("🌐 Initializing Playwright Browser...")
        self.browser = await async_playwright().start()
        self.context = await self.browser.chromium.launch_persistent_context(
            user_data_dir="/tmp/vfs-browser",
            headless=True,
            user_agent=ua,
            viewport={"width": 1920, "height": 1080}
        )
        self.page = await self.context.new_page()
        await self.context.add_cookies(cookies)
        logger.info("✅ Browser Context Initialized with Cookies.")

    async def wait_for_cf_bypass(self):
        from config import CF_IFRAME_SELECTOR, CLOUDFLARE_TIMEOUT
        logger.info("⏳ Waiting for CF Iframe Removal...")
        try:
            await self.page.wait_for_selector(CF_IFRAME_SELECTOR, state="detached", timeout=CLOUDFLARE_TIMEOUT)
            logger.info("✅ CF Iframe Detached!")
        except Exception as e:
            logger.warning(f"⚠️ Iframe removal wait failed: {e}")

    async def wait_for_spa_render(self):
        from config import CONTENT_AWAIT_TIMEOUT
        logger.info("⏳ Waiting for SPA 'E-posta' content...")
        try:
            await self.page.wait_for_function("document.body.innerText.includes('E-posta')", timeout=CONTENT_AWAIT_TIMEOUT)
            logger.info("✅ SPA Render Detected.")
        except Exception as e:
            logger.warning(f"⚠️ SPA render timeout: {e}")
            await self.page.reload(wait_until="load", timeout=30000)
            await self.page.wait_for_function("document.body.innerText.includes('E-posta')", timeout=CONTENT_AWAIT_TIMEOUT)

    async def fill_credentials(self):
        from config import EMAIL_INPUT_SELECTOR, PASSWORD_INPUT_SELECTOR, FORM_FILL_TIMEOUT
        logger.info("📧 Filling credentials...")
        try:
            email_input = await self.page.wait_for_selector(EMAIL_INPUT_SELECTOR, state="visible", timeout=FORM_FILL_TIMEOUT)
            password_input = await self.page.wait_for_selector(PASSWORD_INPUT_SELECTOR, state="visible", timeout=FORM_FILL_TIMEOUT)
            
            await email_input.fill(self.email)
            logger.info("✅ Email filled.")
            
            await password_input.fill(self.password)
            logger.info("✅ Password filled.")
        except Exception as e:
            logger.error(f"❌ Failed to fill credentials: {e}")
            raise

    async def submit_login(self):
        from config import LOGIN_BUTTON_SELECTOR
        logger.info("🖱️ Submitting login form...")
        try:
            login_btn = await self.page.wait_for_selector(LOGIN_BUTTON_SELECTOR, state="visible", timeout=5000)
            await login_btn.click()
            logger.info("🔓 Login button clicked!")
            
            logger.info("⏳ Waiting for Dashboard/OTP redirect...")
            await asyncio.sleep(20)
            
            final_url = self.page.url
            logger.info(f"🔗 Final URL: {final_url}")
            
            if 'otp' in final_url or 'fra/dashboard' in final_url:
                logger.info("✅ Login Completed!")
                return True
            else:
                logger.warning("⚠️ Unexpected redirect.")
                await self.page.screenshot(path="screenshots/login_result.png")
                return False
        except Exception as e:
            logger.error(f"❌ Login submission failed: {e}")
            await self.page.screenshot(path="screenshots/login_error.png")
            return False

    async def run(self):
        await self.initialize_scraper()
        cookies, ua = self.extract_cookies()
        await self.initialize_browser(cookies, ua)
        
        try:
            await self.page.goto("https://visa.vfsglobal.com/tur/tr/fra/login", wait_until="load", timeout=30000)
            await self.wait_for_cf_bypass()
            await self.wait_for_spa_render()
            await self.fill_credentials()
            success = await self.submit_login()
            return success
        finally:
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()

if __name__ == "__main__":
    bot = VFSLoginBot()
    asyncio.run(bot.run())
