import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        async def intercept_response(response):
            if "api" in response.url or "graphql" in response.url or "property" in response.url:
                if response.ok and "image" not in response.headers.get("content-type", ""):
                    try:
                        print(f"Network URL: {response.url}")
                    except Exception:
                        pass
                        
        page.on("response", intercept_response)
        
        print("Navigating to livingethio.com/site/property/for-sale")
        await page.goto("https://livingethio.com/site/property", wait_until="networkidle")
        
        # See what pagination elements are present
        content = await page.content()
        with open("tmp_livingethio_props.html", "w") as f:
            f.write(content)
            
        print("Done. Saved to tmp_livingethio_props.html")
        await browser.close()

asyncio.run(main())
