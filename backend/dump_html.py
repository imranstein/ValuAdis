from playwright.sync_api import sync_playwright

def dump(url, filename):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto(url, timeout=30000)
            with open(filename, 'w') as f:
                f.write(page.content())
        except Exception as e:
            print(f"Failed {url}: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    urls = {
        "ethiopiapropertycentre": "https://ethiopiapropertycentre.com/for-sale",
        "livingethio": "https://livingethio.com/properties/for-sale/",
        "jiji": "https://jiji.com.et/real-estate",
        "zegebeya": "https://zegebeya.com/category/real-estate/",
        "ethiopianproperties": "https://ethiopianproperties.com/property-status/for-sale/"
    }
    for name, url in urls.items():
        print(f"Dumping {name}...")
        dump(url, f"tmp_{name}.html")
