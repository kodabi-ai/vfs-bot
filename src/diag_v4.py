import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            await page.goto('https://visa.vfsglobal.com/tur/tr/fra/login', wait_until='domcontentloaded')
            print('🌐 Navigated to VFS Login Page...')
            
            print('⏳ Waiting for Cloudflare challenge...')
            try:
                await page.wait_for_selector('input[name]', timeout=30000)
                print('✅ Cloudflare challenge resolved. Input found!')
            except Exception as e:
                print(f'⚠️ Timeout waiting for inputs: {e}')
                return

            inputs = await page.query_selector_all('input')
            print(f'\n🔍 Found {len(inputs)} inputs:')
            for inp in inputs:
                name = await inp.get_attribute('name')
                type_ = await inp.get_attribute('type')
                placeholder = await inp.get_attribute('placeholder')
                print(f'  - name: "{name}", type: "{type_}", placeholder: "{placeholder}"')

        except Exception as e:
            print(f'❌ Error: {e}')
        finally:
            await browser.close()

asyncio.run(main())
