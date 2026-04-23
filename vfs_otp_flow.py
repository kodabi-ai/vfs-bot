import asyncio
import logging
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class VFSOTPManager:
    def __init__(self, email: str = None, password: str = None, phone: str = None):
        from config import EMAIL, PASSWORD, PHONE
        self.email = email or EMAIL
        self.password = password or PASSWORD
        self.phone = phone or PHONE
        self.scraper = None
        self.browser = None
        self.context = None
        self.page = None
        self.api_calls = []

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
            user_data_dir="/tmp/vfs-browser-otp",
            headless=True,
            user_agent=ua,
            viewport={"width": 1920, "height": 1080}
        )
        self.page = await self.context.new_page()
        await self.context.add_cookies(cookies)
        logger.info("✅ Browser Context Initialized with Cookies.")

    async def setup_network_monitoring(self):
        logger.info("🔍 Setting up API monitoring...")
        def handle_response(response):
            if 'api' in response.url or 'auth' in response.url:
                self.api_calls.append({
                    'url': response.url,
                    'status': response.status,
                    'method': response.request.method
                })
                logger.info(f"📡 API Call: {response.request.method} {response.url} -> {response.status}")
        self.page.on('response', handle_response)

    async def wait_for_cf_bypass(self):
        from config import CF_IFRAME_SELECTOR, CLOUDFLARE_TIMEOUT
        logger.info("⏳ Waiting for CF Iframe Removal...")
        try:
            await self.page.wait_for_selector(CF_IFRAME_SELECTOR, state="detached", timeout=CLOUDFLARE_TIMEOUT)
            logger.info("✅ CF Iframe Detached!")
        except Exception as e:
            logger.warning(f"⚠️ Iframe removal wait failed: {e}")

    async def wait_for_overlays(self):
        logger.info("⏳ Waiting for Loading Overlays to Disappear...")
        try:
            await self.page.wait_for_selector(".spinner, .loading, .loader", state="detached", timeout=30000)
            logger.info("✅ Overlays Cleared!")
        except Exception as e:
            logger.warning(f"⚠️ Overlay removal failed: {e}")

    async def find_inputs_via_labels(self):
        from config import EMAIL_INPUT_SELECTOR, PASSWORD_INPUT_SELECTOR, FORM_FILL_TIMEOUT
        logger.info("⏳ V49 Strategy: Searching for Inputs via Labels...")
        email_input = None
        password_input = None
        
        labels = await self.page.query_selector_all("label, span")
        input_candidates = await self.page.query_selector_all("input")
        
        for lbl in labels:
            try:
                text = await lbl.inner_text()
                if "E-posta" in text or "Şifre" in text:
                    sibling = await lbl.evaluate_handle("el => el.nextElementSibling")
                    if sibling and await sibling.evaluate("el => el.tagName === 'INPUT'"):
                        if "E-posta" in text:
                            email_input = sibling
                        else:
                            password_input = sibling
                        logger.info(f"✅ Found '{text}' input at sibling")
            except Exception:
                continue

        if not email_input and input_candidates:
            logger.info("⚠️ Label search failed. Manual fallback to input candidates...")
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
                logger.info("✅ Found 2 visible inputs via fallback.")
            elif len(visible_inputs) == 1:
                email_input = visible_inputs[0]
                logger.info("✅ Found 1 visible input via fallback.")

        return email_input, password_input

    async def fill_and_submit(self):
        from config import LOGIN_BUTTON_SELECTOR
        logger.info("📧 Filling credentials...")
        email_input, password_input = await self.find_inputs_via_labels()
        
        if email_input:
            await email_input.fill(self.email)
            logger.info("✅ Email filled.")
            
            if password_input:
                await password_input.fill(self.password)
                logger.info("✅ Password filled.")
            else:
                logger.info("⚠️ No password input found via labels, trying type='password'...")
                try:
                    pwd = await self.page.wait_for_selector('input[type="password"]', state="visible", timeout=5000)
                    await pwd.fill(self.password)
                    logger.info("✅ Password filled (via type selector).")
                except Exception:
                    pass

            logger.info("🖱️ Looking for Login button...")
            login_btn = await self.page.wait_for_selector(LOGIN_BUTTON_SELECTOR, state="visible", timeout=5000)
            await login_btn.click()
            logger.info("🔓 Login button clicked!")
            
            logger.info("⏳ Waiting for Dashboard/OTP redirect...")
            await asyncio.sleep(20)
            final_url = self.page.url
            logger.info(f"🔗 Final URL: {final_url}")
            
            return final_url
        else:
            logger.error("❌ No email input found.")
            await self.page.screenshot(path="screenshots/vfs_otp_debug.png")
            return None

    async def trigger_otp(self):
        logger.info("✅ OTP Page Loaded. Searching for OTP Trigger...")
        await asyncio.sleep(5)
        
        from config import OTP_TRIGGER_SELECTOR
        otp_btn_selector = "button:has-text('Gönder'), button:has-text('Send OTP'), button:has-text('Email OTP'), button:has-text('OTP')"
        otp_btn = await self.page.query_selector(otp_btn_selector)
        
        if otp_btn:
            logger.info("✅ OTP Trigger Button Found! Clicking...")
            await otp_btn.click()
            await asyncio.sleep(5)
            logger.info("✅ OTP Trigger Clicked. Waiting for API Call...")
            return True
        else:
            logger.warning("⚠️ OTP Trigger Button NOT Found. Saving HTML...")
            html = await self.page.content()
            with open("/tmp/vfs_otp_analysis.html", "w", encoding="utf-8") as f:
                f.write(html)
            await self.page.screenshot(path="screenshots/e2e_otp_analysis.png")
            return False

    async def run(self):
        await self.initialize_scraper()
        cookies, ua = self.extract_cookies()
        await self.initialize_browser(cookies, ua)
        await self.setup_network_monitoring()
        
        try:
            await self.page.goto("https://visa.vfsglobal.com/tur/tr/", wait_until="networkidle", timeout=30000)
            await self.page.goto("https://visa.vfsglobal.com/tur/tr/fra/login", wait_until="networkidle", timeout=30000)
            
            await self.wait_for_cf_bypass()
            await self.wait_for_overlays()
            
            final_url = await self.fill_and_submit()
            
            if final_url and 'otp' in final_url:
                success = await self.trigger_otp()
                if success:
                    logger.info("✅ OTP Flow Completed Successfully!")
                else:
                    logger.warning("⚠️ OTP Trigger failed.")
            else:
                logger.warning("⚠️ Unexpected redirect or form fill failed.")
                
        except Exception as e:
            logger.error(f"❌ OTP Flow interaction failed: {e}")
            await self.page.screenshot(path="screenshots/e2e_v49_debug.png")
        finally:
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()

if __name__ == "__main__":
    bot = VFSOTPManager()
    asyncio.run(bot.run())
