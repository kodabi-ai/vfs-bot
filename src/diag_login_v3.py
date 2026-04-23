import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=['--disable-blink-features=AutomationControlled'])
        page = await browser.new_page()
        try:
            # 1. Navigate and wait for network idle initially
            await page.goto('https://visa.vfsglobal.com/tur/tr/fra/login', wait_until='networkidle', timeout=60000)
            
            # 2. Wait for inputs to appear (Cloudflare usually resolves within 10-20s)
            print('Waiting for login form inputs...')
            await page.wait_for_timeout(15000) 
            
            # 3. Check frames for inputs
            frames = page.frames
            print(f'Total frames found: {len(frames)}')
            
            found_inputs = False
            for i, frame in enumerate(frames):
                try:
                    inputs = await frame.query_selector_all('input')
                    print(f'\n--- Frame {i}: {frame.url} ---')
                    print(f'Inputs in frame: {len(inputs)}')
                    for j, el in enumerate(inputs):
                        name = await el.get_attribute('name')
                        type_ = await el.get_attribute('type')
                        placeholder = await el.get_attribute('placeholder')
                        print(f'  [{j}] name={name}, type={type_}, placeholder={placeholder}')
                    if len(inputs) > 0:
                        found_inputs = True
                except Exception as e:
                    print(f'Error accessing frame {i}: {e}')

            # 4. Fallback if no inputs found
            if not found_inputs:
                print('\n--- Fallback: Dumping Body HTML Snippet ---')
                body_html = await page.inner_html('body')
                print(body_html[:1000])
                await page.screenshot(path='screenshots/vfs_diag_v3.png')
                print('\nScreenshot saved: screenshots/vfs_diag_v3.png')
                
            print(f'\nFinal URL: {page.url}')
        except Exception as e:
            print(f'Error: {e}')
        finally:
            await browser.close()

asyncio.run(main())
