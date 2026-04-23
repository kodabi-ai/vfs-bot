import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=['--disable-blink-features=AutomationControlled'])
        page = await browser.new_page()
        try:
            await page.goto('https://visa.vfsglobal.com/tur/tr/fra/login', wait_until='networkidle', timeout=60000)
            await page.wait_for_timeout(5000)
            await page.screenshot(path='screenshots/vfs_diag.png')
            
            frames = page.frames
            print(f'Total frames found: {len(frames)}')
            for i, frame in enumerate(frames):
                print(f'\n--- Frame {i}: {frame.url} ---')
                inputs = await frame.query_selector_all('input')
                print(f'Inputs in frame: {len(inputs)}')
                for j, el in enumerate(inputs):
                    name = await el.get_attribute('name')
                    type_ = await el.get_attribute('type')
                    placeholder = await el.get_attribute('placeholder')
                    print(f'  [{j}] name={name}, type={type_}, placeholder={placeholder}')
            print(f'\nFinal URL: {page.url}')
        except Exception as e:
            print(f'Error: {e}')
        finally:
            await browser.close()

asyncio.run(main())
