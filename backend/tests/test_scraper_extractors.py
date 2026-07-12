"""
Offline extractor tests for Ethiopian property portals.

Runs against the saved fixture HTML — no network, no Playwright.
"""

import os

import pytest

from scraper.extractors import EXTRACTORS, extract_epc, get_extractor, parse_price

FIXTURE_PATH = os.path.join(
    os.path.dirname(__file__), "fixtures", "scraper", "epc_listing_page.html"
)

EPC_DOMAIN = "ethiopiapropertycentre.com"
EPC_BASE_URL = "https://ethiopiapropertycentre.com"
EPC_FIXTURE_LISTING_COUNT = 20


@pytest.fixture(scope="module")
def epc_html() -> str:
    with open(FIXTURE_PATH, encoding="utf-8") as fixture_file:
        return fixture_file.read()


@pytest.fixture(scope="module")
def epc_listings(epc_html):
    return extract_epc(epc_html)


def test_extract_epc_parses_every_listing_card(epc_listings):
    assert len(epc_listings) == EPC_FIXTURE_LISTING_COUNT


def test_extract_epc_extracts_listing_title(epc_listings):
    assert epc_listings[0]["title"] == "B+g+9 Apartment Building @ Sarbet"


def test_extract_epc_normalizes_price_to_etb_float(epc_listings):
    assert epc_listings[0]["asking_price_etb"] == 300000000.0


def test_extract_epc_extracts_location_subcity(epc_listings):
    assert epc_listings[0]["location_subcity"] == "Sarbet, Kirkos, Addis Ababa"


def test_extract_epc_extracts_total_area_sqm(epc_listings):
    assert epc_listings[0]["area_sqm"] == 270.0


def test_extract_epc_extracts_property_type(epc_listings):
    assert epc_listings[0]["property_type"] == "Commercial property for sale"


def test_extract_epc_extracts_bedrooms(epc_listings):
    assert epc_listings[1]["bedrooms"] == 2


def test_extract_epc_extracts_bathrooms(epc_listings):
    assert epc_listings[1]["bathrooms"] == 2


def test_extract_epc_returns_absolute_listing_urls(epc_listings):
    assert all(
        listing["listing_url"].startswith(f"{EPC_BASE_URL}/")
        for listing in epc_listings
    )


def test_extract_epc_returns_unique_listing_urls(epc_listings):
    urls = [listing["listing_url"] for listing in epc_listings]
    assert len(set(urls)) == len(urls)


def test_extract_epc_every_listing_has_positive_price(epc_listings):
    assert all(listing["asking_price_etb"] > 0 for listing in epc_listings)


@pytest.mark.parametrize(
    ("raw_price", "expected"),
    [
        ("Br 300,000,000", 300000000.0),
        ("ETB 8,480,560", 8480560.0),
        ("3.5 million", 3500000.0),
        ("Birr 1.2 billion", 1200000000.0),
        ("500k", 500000.0),
        ("Negotiable", 0.0),
        ("", 0.0),
        (None, 0.0),
    ],
)
def test_parse_price_normalizes_common_formats(raw_price, expected):
    assert parse_price(raw_price) == expected


def test_get_extractor_matches_epc_domain():
    assert get_extractor(EPC_DOMAIN) is extract_epc


def test_get_extractor_matches_www_subdomain():
    assert get_extractor(f"www.{EPC_DOMAIN}") is extract_epc


def test_get_extractor_returns_none_for_unknown_domain():
    assert get_extractor("unknown-portal.example.com") is None


def test_extractor_registry_covers_all_five_portals():
    assert set(EXTRACTORS) == {
        "ethiopiapropertycentre.com",
        "jiji.com.et",
        "zegebeya.com",
        "ethiopianproperties.com",
        "livingethio.com",
    }


FIXTURE_2026_PATH = os.path.join(
    os.path.dirname(__file__), "fixtures", "scraper", "epc_listing_page_2026.html"
)


@pytest.fixture(scope="module")
def epc_2026_listings():
    with open(FIXTURE_2026_PATH, encoding="utf-8") as fixture_file:
        return extract_epc(fixture_file.read())


def test_extract_epc_2026_parses_every_listing_card(epc_2026_listings):
    assert len(epc_2026_listings) == 20


def test_extract_epc_2026_extracts_title(epc_2026_listings):
    assert epc_2026_listings[0]["title"].startswith("Megenagna Top View")


def test_extract_epc_2026_normalizes_br_price(epc_2026_listings):
    assert epc_2026_listings[0]["asking_price_etb"] == 28500000.0


def test_extract_epc_2026_extracts_location_chip(epc_2026_listings):
    assert epc_2026_listings[0]["location_subcity"] == (
        "Megenagna-Lamberet Top View, Yeka, Addis Ababa"
    )


def test_extract_epc_2026_extracts_beds_and_baths(epc_2026_listings):
    assert epc_2026_listings[0]["bedrooms"] == 3
    assert epc_2026_listings[0]["bathrooms"] == 3


def test_extract_epc_2026_extracts_area_from_text(epc_2026_listings):
    assert epc_2026_listings[0]["area_sqm"] == 188.0


def test_extract_epc_2026_extracts_property_type(epc_2026_listings):
    assert epc_2026_listings[0]["property_type"] == "Apartment for sale"


def test_extract_epc_2026_builds_absolute_unique_urls(epc_2026_listings):
    urls = [listing["listing_url"] for listing in epc_2026_listings]
    assert all(url.startswith(EPC_BASE_URL) for url in urls)
    assert len(set(urls)) == len(urls)
