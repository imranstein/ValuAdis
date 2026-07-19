"""
robots.txt decision tests — pure, fixture-text based, no network.
"""

from scraper.robots import is_path_allowed, robots_url_for

UA = "ValuAdisBot"

DISALLOW_ALL = "User-agent: *\nDisallow: /"
ALLOW_ALL = "User-agent: *\nDisallow:"
DISALLOW_SECTION = "User-agent: *\nDisallow: /private/\nAllow: /"


def test_disallow_all_blocks_any_path():
    assert is_path_allowed(DISALLOW_ALL, UA, "https://x.example/for-sale?page=1") is False


def test_allow_all_permits_any_path():
    assert is_path_allowed(ALLOW_ALL, UA, "https://x.example/for-sale?page=1") is True


def test_empty_robots_defaults_to_allowed():
    assert is_path_allowed("", UA, "https://x.example/for-sale") is True


def test_section_disallows_only_matching_prefix():
    assert is_path_allowed(DISALLOW_SECTION, UA, "https://x.example/private/x") is False
    assert is_path_allowed(DISALLOW_SECTION, UA, "https://x.example/for-sale") is True


def test_robots_url_is_host_root():
    assert robots_url_for("https://x.example/for-sale?page=2") == "https://x.example/robots.txt"
