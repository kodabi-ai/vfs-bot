import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=['--disable-blink-features=AutomationControlled'])
        page = await browser.new_page()
        try:
            await page.goto('https://visa.vfsglobal.com/tur/tr/fra/login', wait_until='networkidle', timeout=60000)
            
            # Wait for Cloudflare 403201 to resolve
            print('Waiting for Cloudflare challenge to resolve...')
            while True:
                content = await page.content()
                if '403201' not in content:
                    break
                print('  ...Still waiting (403 active)...')
                await page.wait_for_timeout(1000)
            
            print('Cloudflare challenge resolved.')
            await page.wait_for_timeout(5000)  # Extra wait for dynamic JS
            
            # Close potential cookie/popups
            accept_btn = await page.query_selector('.cc-btn-accept, #onetrust-accept-btn-handler, .cf-turnstile-wrapper iframe')
            if accept_btn:
                print("Closing popup/cookie banner...")
                await accept_btn.click()
                await page.wait_for_timeout(3000)

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
            
            # Fallback: Dump body HTML structure if inputs are empty
            if len(await frames[0].query_selector_all('input')) == 0:
                print('\n--- Body Inner HTML Snippet ---')
                html = await page.inner_html('body')
                print(html[:2000])  # Print first 2000 chars to see form structure
            
            await page.screenshot(path='screenshots/vfs_diag_v2.png')
            print(f'\nFinal URL: {page.url}')
        except Exception as e:
            print(f'Error: {e}')
        finally:
            await browser.close()

asyncio.run(main())
