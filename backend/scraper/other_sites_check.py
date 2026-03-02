import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        
        # Jiji test
        page1 = await browser.new_page()
        await page1.goto("https://jiji.com.et/real-estate", wait_until="domcontentloaded")
        await asyncio.sleep(2)
        content1 = await page1.content()
        with open("tmp_jiji.html", "w") as f:
            f.write(content1)
            
        # Zegebeya test
        page2 = await browser.new_page()
        await page2.goto("https://zegebeya.com/?s=&post_type=ad_listing&scat=13", wait_until="domcontentloaded")
        await asyncio.sleep(2)
        content2 = await page2.content()
        with open("tmp_zegebeya.html", "w") as f:
            f.write(content2)

        # Ethiopianproperties test
        page3 = await browser.new_page()
        await page3.goto("https://ethiopianproperties.com/rent/", wait_until="domcontentloaded")
        await asyncio.sleep(2)
        content3 = await page3.content()
        with open("tmp_ethiopianproperties.html", "w") as f:
            f.write(content3)

        await browser.close()

asyncio.run(main())
