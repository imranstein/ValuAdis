"""
Scraper data-quality helpers.

Covers outlier filtering of scraped listings before they reach the
raw_market_listings table (S9) and the pure consecutive-failure
detection used for alerting (S3). All logic here is pure: no database,
no network, no Sentry.
"""

from scraper.quality import (
    CONSECUTIVE_FAILURE_THRESHOLD,
    count_consecutive_failures,
    filter_outliers,
    has_consecutive_failures,
)


def _listing(price, area, url):
    return {
        "title": f"Listing {url}",
        "asking_price_etb": price,
        "area_sqm": area,
        "listing_url": url,
    }


def _plausible_batch():
    # Eight consistent listings around ~500,000 ETB/sqm.
    prices_areas = [
        (50_000_000, 100.0),
        (52_000_000, 104.0),
        (48_000_000, 96.0),
        (100_000_000, 200.0),
        (75_000_000, 150.0),
        (60_000_000, 120.0),
        (90_000_000, 180.0),
        (55_000_000, 110.0),
    ]
    return [_listing(p, a, f"https://x.test/{i}") for i, (p, a) in enumerate(prices_areas)]


def test_filter_outliers_keeps_consistent_batch():
    kept, dropped = filter_outliers(_plausible_batch())

    assert dropped == []
    assert len(kept) == 8


def test_filter_outliers_drops_absurdly_cheap_price_per_sqm():
    batch = _plausible_batch()
    # 167,992 ETB for 134 sqm ~= 1,254 ETB/sqm, a clear misparse.
    outlier = _listing(167_992, 134.0, "https://x.test/cheap")
    batch.append(outlier)

    kept, dropped = filter_outliers(batch)

    assert outlier in dropped
    assert outlier not in kept


def test_filter_outliers_drops_absurdly_expensive_price_per_sqm():
    batch = _plausible_batch()
    outlier = _listing(9_000_000_000, 100.0, "https://x.test/pricey")
    batch.append(outlier)

    kept, dropped = filter_outliers(batch)

    assert outlier in dropped


def test_filter_outliers_drops_negative_price():
    batch = _plausible_batch()
    outlier = _listing(-5, 120.0, "https://x.test/neg-price")
    batch.append(outlier)

    kept, dropped = filter_outliers(batch)

    assert outlier in dropped


def test_filter_outliers_keeps_zero_price_as_unknown():
    # Extractors emit 0.0 when a price is not parseable; treat it as
    # unknown (kept) rather than an outlier.
    batch = _plausible_batch()
    unknown = _listing(0, 120.0, "https://x.test/zero-price")
    batch.append(unknown)

    kept, dropped = filter_outliers(batch)

    assert unknown in kept


def test_filter_outliers_drops_negative_area():
    batch = _plausible_batch()
    outlier = _listing(50_000_000, -50.0, "https://x.test/neg-area")
    batch.append(outlier)

    kept, dropped = filter_outliers(batch)

    assert outlier in dropped


def test_filter_outliers_keeps_records_with_unknown_price_or_area():
    # The market_listing model allows missing price/area; these must not
    # be dropped just because a price-per-sqm cannot be computed.
    batch = _plausible_batch()
    no_price = _listing(None, 120.0, "https://x.test/no-price")
    no_area = _listing(50_000_000, None, "https://x.test/no-area")
    no_area_zero = _listing(50_000_000, 0.0, "https://x.test/zero-area")
    batch.extend([no_price, no_area, no_area_zero])

    kept, dropped = filter_outliers(batch)

    assert no_price in kept
    assert no_area in kept
    assert no_area_zero in kept


def test_filter_outliers_on_empty_batch():
    kept, dropped = filter_outliers([])

    assert kept == []
    assert dropped == []


def test_count_consecutive_failures_counts_leading_failed_only():
    # Statuses are most-recent-first.
    assert count_consecutive_failures(["failed", "failed", "success"]) == 2


def test_count_consecutive_failures_stops_at_first_non_failed():
    assert count_consecutive_failures(["success", "failed", "failed"]) == 0


def test_count_consecutive_failures_all_failed():
    assert count_consecutive_failures(["failed", "failed", "failed"]) == 3


def test_count_consecutive_failures_empty():
    assert count_consecutive_failures([]) == 0


def test_has_consecutive_failures_at_threshold():
    assert has_consecutive_failures(["failed"] * CONSECUTIVE_FAILURE_THRESHOLD) is True


def test_has_consecutive_failures_below_threshold():
    statuses = ["failed"] * (CONSECUTIVE_FAILURE_THRESHOLD - 1) + ["success"]
    assert has_consecutive_failures(statuses) is False
