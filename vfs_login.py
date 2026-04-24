import asyncio
import logging
import httpx
from playwright.async_api import async_playwright

import config

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class VFSLoginBot:
    def __init__(self, email: str = None, password: str = None):
        self.email = email or config.EMAIL
        self.password = password or config.PASSWORD
        self.USER_AGENT = getattr(config, 'USER_AGENT', "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        self.VIEWPORT = getattr(config, 'VIEWPORT', {'width': 1920, 'height': 1080})
        self.browser = None
        self.context = None
        self.page = None

    async def fetch_api_cookies(self):
        logger.info("🌐 Step 1: Fetching API cookies with httpx...")
        api_base = config.config.get('vfs_global.urls.api_base', 'https://lift-api.vfsglobal.com')
        main_base = config.config.get('vfs_global.urls.base', 'https://visa.vfsglobal.com/tur/tr/')
        
        main_domain = main_base.replace('https://', '').split('/')[0]
        api_domain = api_base.replace('https://', '').split('/')[0]
        
        async with httpx.AsyncClient(http2=True, follow_redirects=True, timeout=20) as client:
            try:
                await client.get(f"https://{main_domain}", headers={"User-Agent": self.USER_AGENT})
                await client.get(f"https://{api_domain}", headers={"User-Agent": self.USER_AGENT})
                
                all_cookies = []
                for name, cookie in client.cookies.items():
                    val = cookie.value if hasattr(cookie, 'value') else cookie
                    if api_domain in name or name == '__cf_bm' or name == '__cfuvid' or name == 'cf_clearance':
                        domain = f".{api_domain}"
                    else:
                        domain = f".{main_domain}"
                    all_cookies.append({"name": name, "value": val, "domain": domain, "path": "/"})
                
                logger.info(f"✅ Fetched {len(all_cookies)} cookies via httpx.")
                return all_cookies
            except Exception as e:
                logger.warning(f"⚠️ httpx cookie fetch failed: {e}. Proceeding with empty cookies.")
                return []

    async def run(self):
        logger.info("🚀 Starting V105 Optimization (HTML Debug & Generic Input)...")
        try:
            api_cookies = await self.fetch_api_cookies()
            
            self.browser = await async_playwright().start()
            self.context = await self.browser.chromium.launch_persistent_context(
                user_data_dir="/tmp/vfs-v105",
                headless=True,
                user_agent=self.USER_AGENT,
                viewport=self.VIEWPORT
            )
            self.page = self.context.pages[0] if self.context.pages else await self.context.new_page()
            
            if api_cookies:
                await self.context.add_cookies(api_cookies)
                logger.info("✅ API cookies injected successfully.")
            
            LOGIN_URL = "https://visa.vfsglobal.com/tur/tr/fra/login"
            logger.info(f"🚀 Navigating to {LOGIN_URL}...")
            await self.page.goto(LOGIN_URL, wait_until="domcontentloaded", timeout=15000)
            
            # Check URL after navigation
            logger.info(f"🔗 Current URL: {self.page.url}")
            
            logger.info("⏳ Waiting for Cloudflare bypass...")
            try:
                await self.page.wait_for_selector("iframe[src*='challenges/']", state="detached", timeout=30000)
                logger.info("✅ Cloudflare challenge cleared.")
            except Exception as e:
                logger.warning(f"⚠️ Cloudflare wait timeout: {e}")

            # V105 Strategy: Wait for ANY input to appear, then debug
            logger.info("⏳ Waiting for ANY input element...")
            try:
                await self.page.wait_for_selector("input, select, textarea", state="attached", timeout=15000)
                logger.info("✅ Any input element detected in DOM.")
            except Exception as e:
                logger.warning(f"⚠️ No input elements detected. Dumping HTML debug...")
                html_content = await self.page.evaluate('document.body.innerHTML')
                logger.info(f"📄 HTML Length: {len(html_content)}")
                logger.info(f"📄 HTML Preview: {html_content[:1000]}")
                await self.page.reload(wait_until="domcontentloaded")
                await self.page.wait_for_selector("input, select, textarea", state="attached", timeout=10000)

            # V111 Strategy: Visible Transition Wait (d-none removal) & Robust Fallback
            logger.info("🔍 Waiting for visible Username/Password inputs (V111)...")
            try:
                # Strategy: VFS loads hidden 'd-none' inputs first. We wait for them to become visible.
                logger.info("⏳ Waiting for visible Username/Email field (removing d-none)...")
                # Wait for the specific attribute name to lose its hidden state
                user_input = await self.page.wait_for_selector("input[name='username'], input[name='email']", state="visible", timeout=20000)
                await user_input.fill(self.email)
                logger.info("✅ User field filled.")

                logger.info("⏳ Waiting for visible Password field...")
                pass_input = await self.page.wait_for_selector("input[name='password']", state="visible", timeout=15000)
                await pass_input.fill(self.password)
                logger.info("✅ Password field filled.")

                # Click Sign In
                logger.info("🖱️ Clicking Sign In button...")
                sign_in_btn = self.page.get_by_role("button", name="Sign In")
                await sign_in_btn.click(timeout=5000)
                logger.info("✅ Sign In clicked.")
                await asyncio.sleep(5)

            except Exception as e:
                logger.warning(f"⚠️ V111 Standard Strategy failed: {e}")
                # Fallback: Try any visible button and fill first available inputs
                logger.info("🔄 Fallback: Trying first visible button and inputs...")
                try:
                    btns = await self.page.query_selector_all("button")
                    for b in btns:
                        if await b.is_visible():
                            await b.click()
                            break
                except Exception as sub_e:
                    logger.error(f"❌ Fallback failed: {sub_e}")

            logger.info("🖱️ Clicking Login Button...")
            try:
                login_btn = await self.page.wait_for_selector(LOGIN_BUTTON, state="visible", timeout=5000)
                await login_btn.click()
                logger.info("🔓 Login button clicked.")
            except Exception as e:
                logger.warning(f"⚠️ Login button not found. Trying any button with 'Giriş' text or first button...")
                btn = await self.page.wait_for_selector('button:has-text("Giriş")', state="visible", timeout=5000)
                await btn.click()
                logger.info("🔓 Button clicked.")
            
            logger.info("⏳ Waiting for redirect/OTP...")
            await asyncio.sleep(10)
            
            final_url = self.page.url
            logger.info(f"🔗 Final URL: {final_url}")
            
            if 'otp' in final_url or 'dashboard' in final_url:
                logger.info("✅ Login Completed Successfully!")
                return True
            else:
                logger.warning("⚠️ Unexpected redirect.")
                await self.page.screenshot(path="screenshots/v105_result.png")
                return False

        except Exception as e:
            logger.error(f"❌ Execution failed: {e}")
            if self.page:
                await self.page.screenshot(path="screenshots/v105_error.png")
            return False
        finally:
            if self.context:
                await self.context.close()
            if self.browser:
                try:
                    await self.browser.close()
                except:
                    pass

if __name__ == "__main__":
    bot = VFSLoginBot()
    asyncio.run(bot.run())
