"""
Scraper data-quality helpers.

Pure functions used to (1) drop obvious price/area outliers from a batch
of scraped listings before they are written to raw_market_listings, and
(2) detect runs of consecutive failed scraper runs for alerting. Nothing
here touches the database, the network, or Sentry.
"""

import statistics
from typing import Any, Dict, List, Optional, Sequence, Tuple

Record = Dict[str, Any]

# A listing whose price-per-sqm sits outside median / RATIO .. median * RATIO
# is treated as a robust outlier relative to the rest of its batch.
OUTLIER_PPSQM_RATIO = 4.0

# Absolute plausibility band for Addis Ababa property (ETB per sqm). Values
# outside this range are misparses regardless of the rest of the batch.
MIN_PLAUSIBLE_PPSQM = 1_000.0
MAX_PLAUSIBLE_PPSQM = 10_000_000.0

# Robust bounds are only meaningful with enough computable samples.
MIN_ROBUST_SAMPLE = 4

# Number of consecutive failed runs that should trigger an alert.
CONSECUTIVE_FAILURE_THRESHOLD = 3


def _price_per_sqm(record: Record) -> Optional[float]:
    """Return ETB/sqm for a record, or None when it cannot be computed."""
    price = record.get("asking_price_etb")
    area = record.get("area_sqm")
    if price is None or area is None:
        return None
    try:
        price = float(price)
        area = float(area)
    except (TypeError, ValueError):
        return None
    if price <= 0 or area <= 0:
        return None
    return price / area


def _is_implausible(record: Record) -> bool:
    """A record is implausible if a present price/area is negative.

    Missing price or area is allowed (the listing model permits it), and
    the extractors emit 0.0 as the "unknown" sentinel for an unparsed
    price or area, so zero is treated as missing and kept. Only a negative
    value is a corrupt parse worth dropping outright.
    """
    for key in ("asking_price_etb", "area_sqm"):
        value = record.get(key)
        if value is None:
            continue
        try:
            if float(value) < 0:
                return True
        except (TypeError, ValueError):
            return True
    return False


def filter_outliers(records: Sequence[Record]) -> Tuple[List[Record], List[Record]]:
    """Split a batch into (kept, dropped).

    Records are dropped when a present price or area is non-positive, when
    their price-per-sqm falls outside the absolute plausibility band, or
    when it falls outside robust median-based bounds for the batch. Records
    whose price-per-sqm cannot be computed (missing price or area) are kept.
    """
    computable = [pp for pp in (_price_per_sqm(r) for r in records) if pp is not None]

    lower = upper = None
    if len(computable) >= MIN_ROBUST_SAMPLE:
        median = statistics.median(computable)
        if median > 0:
            lower = median / OUTLIER_PPSQM_RATIO
            upper = median * OUTLIER_PPSQM_RATIO

    kept: List[Record] = []
    dropped: List[Record] = []
    for record in records:
        if _is_implausible(record):
            dropped.append(record)
            continue
        ppsqm = _price_per_sqm(record)
        if ppsqm is None:
            kept.append(record)
            continue
        if ppsqm < MIN_PLAUSIBLE_PPSQM or ppsqm > MAX_PLAUSIBLE_PPSQM:
            dropped.append(record)
            continue
        if lower is not None and (ppsqm < lower or ppsqm > upper):
            dropped.append(record)
            continue
        kept.append(record)

    return kept, dropped


def count_consecutive_failures(statuses: Sequence[Optional[str]]) -> int:
    """Count leading 'failed' statuses given most-recent-first order."""
    count = 0
    for status in statuses:
        if status == "failed":
            count += 1
        else:
            break
    return count


def has_consecutive_failures(
    statuses: Sequence[Optional[str]],
    threshold: int = CONSECUTIVE_FAILURE_THRESHOLD,
) -> bool:
    """True when the most recent runs are `threshold` consecutive failures."""
    return count_consecutive_failures(statuses) >= threshold
