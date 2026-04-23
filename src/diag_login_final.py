import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=['--disable-blink-features=AutomationControlled'])
        page = await browser.new_page()
        try:
            await page.goto('https://visa.vfsglobal.com/tur/tr/fra/login', wait_until='domcontentloaded', timeout=45000)
            
            # Bounded wait for Cloudflare to resolve (max 20s)
            print('Waiting for Cloudflare challenge to resolve...')
            for _ in range(40):  # 40 * 0.5s = 20s
                await page.wait_for_timeout(500)
                content = await page.content()
                if '403201' not in content:
                    print('Cloudflare challenge resolved.')
                    break
            else:
                print('Cloudflare challenge still active after 20s.')

            await page.wait_for_timeout(3000)  # Extra time for DOM to settle
            
            frames = page.frames
            print(f'\nTotal frames found: {len(frames)}')
            
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

            if not found_inputs:
                print('\n--- No inputs found. Dumping body HTML snippet ---')
                body_html = await page.inner_html('body')
                print(body_html[:1500])
                await page.screenshot(path='screenshots/vfs_diag_final.png')
                print('\nScreenshot saved: screenshots/vfs_diag_final.png')
                
            print(f'\nFinal URL: {page.url}')
        except Exception as e:
            print(f'Error: {e}')
        finally:
            await browser.close()

asyncio.run(main())
