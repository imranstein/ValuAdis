import re
from typing import Dict, Any, List

def parse_price(val: str) -> float:
    if not val:
        return 0.0
    val = val.lower().replace('etb', '').replace('br', '').replace('birr', '').replace(',', '').replace(' ', '')
    try:
        # handle "million" / "k" / "billion" ? Usually it's digits.
        return float(re.sub(r'[^\d.]', '', val))
    except ValueError:
        return 0.0

def parse_int(val: str) -> int:
    if not val:
        return 0
    try:
        return int(re.sub(r'[^\d]', '', val))
    except ValueError:
        return 0

def parse_float(val: str) -> float:
    if not val:
        return 0.0
    try:
        return float(re.sub(r'[^\d.]', '', val))
    except ValueError:
        return 0.0


async def extract_epc(page) -> List[Dict[str, Any]]:
    # ethiopiapropertycentre.com
    results = []
    # Actual elements from analysis: classes like "property" inside a "property-list"
    items = await page.locator('.property, .wp-block-property').all()
    for item in items:
        try:
            link_loc = item.locator('a[itemprop="url"], h4.content-title a, .property-title a, a[href*="/for-sale/property/"], a[href*="/for-rent/property/"]').first
            if await link_loc.count() == 0:
                # Some sites use itemprop, or just h4 a
                link_loc = item.locator('a').first
                if await link_loc.count() == 0:
                    continue
            title = await link_loc.inner_text()
            listing_url = await link_loc.get_attribute('href')
            
            price_loc = item.locator('.price, span[itemprop="price"], h3.price').first
            price_str = await price_loc.inner_text() if await price_loc.count() > 0 else ""
            
            address_loc = item.locator('.address, address').first
            location_subcity = await address_loc.inner_text() if await address_loc.count() > 0 else ""
            
            beds_loc = item.locator('.beds strong, ul.amenities li:has(i.fa-bed) span').first
            bedrooms = parse_int(await beds_loc.inner_text()) if await beds_loc.count() > 0 else 0
            
            baths_loc = item.locator('.baths strong, ul.amenities li:has(i.fa-bath) span').first
            bathrooms = parse_int(await baths_loc.inner_text()) if await baths_loc.count() > 0 else 0
            
            area_loc = item.locator('.area strong, ul.amenities li:has(i.fa-arrows-alt) span').first
            area_sqm = parse_float(await area_loc.inner_text()) if await area_loc.count() > 0 else 0.0
            
            type_loc = item.locator('.property-type, span:has-text("Type:") + span').first
            property_type = await type_loc.inner_text() if await type_loc.count() > 0 else "Unknown"

            results.append({
                "title": title.strip(),
                "asking_price_etb": parse_price(price_str),
                "location_subcity": location_subcity.strip(),
                "area_sqm": area_sqm,
                "property_type": property_type.strip(),
                "bedrooms": bedrooms,
                "bathrooms": bathrooms,
                "listing_url": ("https://ethiopiapropertycentre.com" + listing_url) if listing_url.startswith('/') else listing_url,
            })
        except Exception as e:
            print(f"Error extracting EPC item: {e}")
            continue
    return results


async def extract_jiji(page) -> List[Dict[str, Any]]:
    # jiji.com.et/real-estate
    # item class: .b-list-advert-base
    results = []
    items = await page.locator('.b-list-advert-base').all()
    for item in items:
        try:
            title_loc = item.locator('.qa-advert-title').first
            if await title_loc.count() == 0:
                continue
            title = await title_loc.inner_text()
            
            # The item itself is an <a> tag sometimes:
            # Let's check if the item is <a> or has <a>
            if await item.evaluate('el => el.tagName') == 'A':
                listing_url = await item.get_attribute('href')
            else:
                a_loc = item.locator('a').first
                listing_url = await a_loc.get_attribute('href') if await a_loc.count() > 0 else None
                
            if not listing_url:
                continue
            
            price_loc = item.locator('.qa-advert-price').first
            price_str = await price_loc.inner_text() if await price_loc.count() > 0 else ""
            
            # Jiji has attributes in `.b-list-advert-base__item-attr`
            attrs_locs = await item.locator('.b-list-advert-base__item-attr').all()
            attrs = [await x.inner_text() for x in attrs_locs]
            
            area_sqm = 0.0
            bedrooms = 0
            for a in attrs:
                if 'sqm' in a.lower():
                    area_sqm = parse_float(a)
                if 'bed' in a.lower():
                    bedrooms = parse_int(a)
            
            results.append({
                "title": title.strip(),
                "asking_price_etb": parse_price(price_str),
                "location_subcity": "", 
                "area_sqm": area_sqm,
                "property_type": "Unknown", 
                "bedrooms": bedrooms,
                "bathrooms": 0, 
                "listing_url": ("https://jiji.com.et" + listing_url) if listing_url.startswith('/') else listing_url,
            })
        except Exception as e:
            print(f"Error extracting Jiji item: {e}")
            continue
    return results


async def extract_zegebeya(page) -> List[Dict[str, Any]]:
    # zegebeya.com items
    results = []
    # RealHomes theme uses article.property-item or .rh_list_card__wrap or .rhea_property_card
    items = await page.locator('article.property-item, .rh_list_card__wrap, .rhea_property_card').all()
    for item in items:
        try:
            link_loc = item.locator('h3 a, h2.entry-title a, h4 a, .rhea_property_title a').first
            if await link_loc.count() == 0:
                continue
            title = await link_loc.inner_text()
            listing_url = await link_loc.get_attribute('href')
            
            price_loc = item.locator('.price, .rh_prop_card__price').first
            price_str = await price_loc.inner_text() if await price_loc.count() > 0 else ""
            
            bed_loc = item.locator('.rh_prop_card__meta figure[data-tooltip="Bedrooms"] + div, .rhea_meta_bed .figure, span:has-text("Bedrooms")').first
            bedrooms = parse_int(await bed_loc.inner_text()) if await bed_loc.count() > 0 else 0
            
            bath_loc = item.locator('.rh_prop_card__meta figure[data-tooltip="Bathrooms"] + div, .rhea_meta_bath .figure, span:has-text("Bathrooms")').first
            bathrooms = parse_int(await bath_loc.inner_text()) if await bath_loc.count() > 0 else 0
            
            area_loc = item.locator('.rh_prop_card__meta figure[data-tooltip="Area"] + div, .rhea_meta_area .figure, span:has-text("Sq Ft")').first
            area_sqm = parse_float(await area_loc.inner_text()) if await area_loc.count() > 0 else 0.0
            
            results.append({
                "title": title.strip(),
                "asking_price_etb": parse_price(price_str),
                "location_subcity": "", 
                "area_sqm": area_sqm,
                "property_type": "Unknown",
                "bedrooms": bedrooms,
                "bathrooms": bathrooms,
                "listing_url": listing_url,
            })
        except Exception as e:
            print(f"Error extracting Zegebeya item: {e}")
            continue
    return results

async def extract_ethiopianproperties(page) -> List[Dict[str, Any]]:
    results = []
    # Theme element
    items = await page.locator('article.property, .property-item, .rh_list_card__wrap').all()
    for item in items:
        try:
            link_loc = item.locator('h3 a, h2.entry-title a, h4 a, .property-title a').first
            if await link_loc.count() == 0:
                continue
            title = await link_loc.inner_text()
            listing_url = await link_loc.get_attribute('href')
            
            price_loc = item.locator('.price, .property-price').first
            price_str = await price_loc.inner_text() if await price_loc.count() > 0 else ""
            
            results.append({
                "title": title.strip(),
                "asking_price_etb": parse_price(price_str),
                "location_subcity": "",
                "area_sqm": 0.0,
                "property_type": "Unknown",
                "bedrooms": 0,
                "bathrooms": 0,
                "listing_url": listing_url,
            })
        except Exception as e:
            print(f"Error extracting ethiopianproperties item: {e}")
            continue
    return results

async def extract_livingethio(page) -> List[Dict[str, Any]]:
    # livingethio loads via Angular/PrimeNG.
    # Property cards
    results = []
    items = await page.locator('.b-list-advert-base, .property-card, .p-card').all()
    for item in items:
        # We need a robust general approach if standard selectors fail.
        # livingethio json API is at /api/properties/search. Let's do basic scraping if they render them with .p-card
        try:
            title_loc = item.locator('.p-card-title').first
            if await title_loc.count() == 0:
                continue
            title = await title_loc.inner_text()
            
            price_loc = item.locator('.price, .text-primary-500').first
            price_str = await price_loc.inner_text() if await price_loc.count() > 0 else ""
            
            # URL: might be inside an a tag under card
            a_loc = item.locator('a').first
            if await a_loc.count() == 0:
                continue
            listing_url = await a_loc.get_attribute('href')
            
            results.append({
                "title": title.strip(),
                "asking_price_etb": parse_price(price_str),
                "location_subcity": "", 
                "area_sqm": 0.0,
                "property_type": "Unknown",
                "bedrooms": 0,
                "bathrooms": 0,
                "listing_url": ("https://livingethio.com" + listing_url) if listing_url.startswith('/') else listing_url,
            })
        except Exception as e:
            print(f"Error extracting livingethio item: {e}")
            continue
    return results

EXTRACTORS = {
    'ethiopiapropertycentre.com': extract_epc,
    'jiji.com.et': extract_jiji,
    'zegebeya.com': extract_zegebeya,
    'ethiopianproperties.com': extract_ethiopianproperties,
    'livingethio.com': extract_livingethio
}
