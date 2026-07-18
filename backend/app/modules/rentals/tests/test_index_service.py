"""
Rent index aggregation — pure math (Phase D).

compute_group_stats() and is_suppressed() take no DB session; median math,
the contracts-vs-listings fallback, and the suppression threshold are all
testable with plain lists of floats.
"""

from app.modules.rentals.index_service import (
    MIN_SAMPLE_SIZE,
    compute_group_stats,
    current_period,
    is_suppressed,
)


class TestMedianMath:
    def test_odd_count_returns_middle_value(self):
        stats = compute_group_stats([20000.0, 25000.0, 30000.0], [])
        assert stats["median_rent"] == 25000.0
        assert stats["sample_size"] == 3
        assert stats["source"] == "contracts"

    def test_even_count_returns_average_of_middle_two(self):
        stats = compute_group_stats([10000.0, 20000.0], [30000.0, 40000.0])
        assert stats["median_rent"] == 25000.0
        assert stats["sample_size"] == 4


class TestFallback:
    def test_contract_sample_above_threshold_ignores_listings(self):
        stats = compute_group_stats([10000.0, 20000.0, 30000.0], [999999.0])
        assert stats["source"] == "contracts"
        assert stats["sample_size"] == 3

    def test_thin_contract_sample_blends_listings(self):
        stats = compute_group_stats([20000.0], [22000.0, 24000.0])
        assert stats["source"] == "blended"
        assert stats["sample_size"] == 3

    def test_no_contracts_falls_back_to_listings_only(self):
        stats = compute_group_stats([], [15000.0, 16000.0, 17000.0])
        assert stats["source"] == "listings"
        assert stats["median_rent"] == 16000.0

    def test_no_data_at_all_returns_none_median(self):
        stats = compute_group_stats([], [])
        assert stats["median_rent"] is None
        assert stats["sample_size"] == 0


class TestSuppression:
    def test_sample_below_threshold_is_suppressed(self):
        assert is_suppressed(MIN_SAMPLE_SIZE - 1) is True

    def test_sample_at_threshold_is_not_suppressed(self):
        assert is_suppressed(MIN_SAMPLE_SIZE) is False

    def test_sample_above_threshold_is_not_suppressed(self):
        assert is_suppressed(MIN_SAMPLE_SIZE + 5) is False


class TestPeriod:
    def test_current_period_is_year_month(self):
        from datetime import datetime, timezone

        moment = datetime(2026, 7, 22, tzinfo=timezone.utc)
        assert current_period(moment) == "2026-07"
