"""
Pure HTML extractors for Ethiopian property portals.

Each extractor takes raw page HTML and returns normalized listing dicts.
No network access and no Playwright — the browser driver fetches HTML,
extraction stays pure so it can be tested offline against fixtures.
"""

import re
from typing import Any, Callable, Dict, List, Optional

from bs4 import BeautifulSoup

Listing = Dict[str, Any]
Extractor = Callable[[str], List[Listing]]

EPC_BASE_URL = "https://ethiopiapropertycentre.com"
JIJI_BASE_URL = "https://jiji.com.et"
LIVINGETHIO_BASE_URL = "https://livingethio.com"

CURRENCY_TOKENS = ("etb", "birr", "br")
BILLION = 1_000_000_000.0
MILLION = 1_000_000.0
THOUSAND = 1_000.0


def parse_price(val: Optional[str]) -> float:
    """Normalize a price string (Br/ETB/birr, commas, million/k suffixes) to ETB."""
    if not val:
        return 0.0
    text = str(val).lower().replace(",", "")
    for token in CURRENCY_TOKENS:
        text = text.replace(token, " ")
    match = re.search(r"\d+(?:\.\d+)?", text)
    if not match:
        return 0.0
    amount = float(match.group())
    suffix = text[match.end():]
    if "billion" in suffix:
        amount *= BILLION
    elif "million" in suffix or re.match(r"\s*m\b", suffix):
        amount *= MILLION
    elif re.match(r"\s*k\b", suffix):
        amount *= THOUSAND
    return amount


def parse_int(val: Optional[str]) -> int:
    if not val:
        return 0
    match = re.search(r"\d+", str(val))
    return int(match.group()) if match else 0


def parse_float(val: Optional[str]) -> float:
    if not val:
        return 0.0
    match = re.search(r"\d+(?:\.\d+)?", str(val))
    return float(match.group()) if match else 0.0


def _absolute_url(href: str, base_url: str) -> str:
    return f"{base_url}{href}" if href.startswith("/") else href


def _text(node) -> str:
    return node.get_text(" ", strip=True) if node else ""


def extract_epc(html: str) -> List[Listing]:
    """ethiopiapropertycentre.com listing/search result pages."""
    soup = BeautifulSoup(html, "html.parser")
    listings = []
    for item in soup.select("div.wp-block.property.list"):
        link = item.select_one('.wp-block-title a[itemprop="url"]') or item.select_one(
            ".wp-block-title a, h4.content-title a"
        )
        href = link.get("href") if link else None
        if not href:
            continue
        title = _text(item.select_one('h3[itemprop="name"]')) or _text(link)
        if not title:
            continue
        bedrooms, bathrooms, area_sqm = _epc_aux_info(item)
        listings.append(
            {
                "title": title,
                "asking_price_etb": _epc_price(item),
                "location_subcity": _text(item.select_one("address")),
                "area_sqm": area_sqm,
                "property_type": _text(item.select_one("h4.content-title")) or "Unknown",
                "bedrooms": bedrooms,
                "bathrooms": bathrooms,
                "listing_url": _absolute_url(href, EPC_BASE_URL),
            }
        )
    return listings


def _epc_price(item) -> float:
    # EPC embeds the numeric amount in a content attribute next to the
    # currency span; prefer it over display text.
    for span in item.select("span.price[content]"):
        try:
            value = float(span.get("content", ""))
        except ValueError:
            continue
        if value > 0:
            return value
    return parse_price(" ".join(_text(span) for span in item.select("span.price")))


def _epc_aux_info(item):
    bedrooms = 0
    bathrooms = 0
    area_sqm = 0.0
    for entry in item.select("ul.aux-info li"):
        icon = entry.select_one("i")
        icon_classes = set(icon.get("class", [])) if icon else set()
        text = _text(entry)
        if "fa-bed" in icon_classes:
            bedrooms = parse_int(text)
        elif "fa-bath" in icon_classes:
            bathrooms = parse_int(text)
        elif "fa-square" in icon_classes:
            area_sqm = parse_float(text)
    return bedrooms, bathrooms, area_sqm


def extract_jiji(html: str) -> List[Listing]:
    """jiji.com.et real-estate listing pages."""
    soup = BeautifulSoup(html, "html.parser")
    listings = []
    for item in soup.select(".b-list-advert-base"):
        title = _text(item.select_one(".qa-advert-title"))
        if not title:
            continue
        if item.name == "a":
            href = item.get("href")
        else:
            anchor = item.select_one("a")
            href = anchor.get("href") if anchor else None
        if not href:
            continue
        area_sqm = 0.0
        bedrooms = 0
        for attr in item.select(".b-list-advert-base__item-attr"):
            attr_text = _text(attr)
            if "sqm" in attr_text.lower():
                area_sqm = parse_float(attr_text)
            if "bed" in attr_text.lower():
                bedrooms = parse_int(attr_text)
        listings.append(
            {
                "title": title,
                "asking_price_etb": parse_price(_text(item.select_one(".qa-advert-price"))),
                "location_subcity": "",
                "area_sqm": area_sqm,
                "property_type": "Unknown",
                "bedrooms": bedrooms,
                "bathrooms": 0,
                "listing_url": _absolute_url(href, JIJI_BASE_URL),
            }
        )
    return listings


def extract_zegebeya(html: str) -> List[Listing]:
    """zegebeya.com (RealHomes theme) listing pages."""
    soup = BeautifulSoup(html, "html.parser")
    listings = []
    for item in soup.select("article.property-item, .rh_list_card__wrap, .rhea_property_card"):
        link = item.select_one("h3 a, h2.entry-title a, h4 a, .rhea_property_title a")
        href = link.get("href") if link else None
        if not href:
            continue
        listings.append(
            {
                "title": _text(link),
                "asking_price_etb": parse_price(
                    _text(item.select_one(".price, .rh_prop_card__price"))
                ),
                "location_subcity": "",
                "area_sqm": parse_float(
                    _text(item.select_one('figure[data-tooltip="Area"] + div'))
                ),
                "property_type": "Unknown",
                "bedrooms": parse_int(
                    _text(item.select_one('figure[data-tooltip="Bedrooms"] + div'))
                ),
                "bathrooms": parse_int(
                    _text(item.select_one('figure[data-tooltip="Bathrooms"] + div'))
                ),
                "listing_url": href,
            }
        )
    return listings


def extract_ethiopianproperties(html: str) -> List[Listing]:
    """ethiopianproperties.com listing pages."""
    soup = BeautifulSoup(html, "html.parser")
    listings = []
    for item in soup.select("article.property, .property-item, .rh_list_card__wrap"):
        link = item.select_one("h3 a, h2.entry-title a, h4 a, .property-title a")
        href = link.get("href") if link else None
        if not href:
            continue
        listings.append(
            {
                "title": _text(link),
                "asking_price_etb": parse_price(
                    _text(item.select_one(".price, .property-price"))
                ),
                "location_subcity": "",
                "area_sqm": 0.0,
                "property_type": "Unknown",
                "bedrooms": 0,
                "bathrooms": 0,
                "listing_url": href,
            }
        )
    return listings


def extract_livingethio(html: str) -> List[Listing]:
    """livingethio.com (PrimeNG card layout) listing pages."""
    soup = BeautifulSoup(html, "html.parser")
    listings = []
    for item in soup.select(".property-card, .p-card"):
        title = _text(item.select_one(".p-card-title"))
        if not title:
            continue
        anchor = item.select_one("a")
        href = anchor.get("href") if anchor else None
        if not href:
            continue
        listings.append(
            {
                "title": title,
                "asking_price_etb": parse_price(
                    _text(item.select_one(".price, .text-primary-500"))
                ),
                "location_subcity": "",
                "area_sqm": 0.0,
                "property_type": "Unknown",
                "bedrooms": 0,
                "bathrooms": 0,
                "listing_url": _absolute_url(href, LIVINGETHIO_BASE_URL),
            }
        )
    return listings


EXTRACTORS: Dict[str, Extractor] = {
    "ethiopiapropertycentre.com": extract_epc,
    "jiji.com.et": extract_jiji,
    "zegebeya.com": extract_zegebeya,
    "ethiopianproperties.com": extract_ethiopianproperties,
    "livingethio.com": extract_livingethio,
}


def get_extractor(domain: Optional[str]) -> Optional[Extractor]:
    """Resolve the site-specific extractor for a scraper target domain."""
    if not domain:
        return None
    normalized = domain.lower().strip()
    if normalized.startswith("www."):
        normalized = normalized[len("www."):]
    if normalized in EXTRACTORS:
        return EXTRACTORS[normalized]
    for key, extractor in EXTRACTORS.items():
        if normalized.endswith(f".{key}"):
            return extractor
    return None
