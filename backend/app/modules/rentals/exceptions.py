"""
Rentals module exceptions

Distinct exception types so the routes can map band violations to 422 (the
plan's documented contract for an out-of-band offer) and rate-limit hits to
429, separately from ordinary 400 validation errors.
"""

from app.core.exceptions import ValidationException


class BandViolationError(ValidationException):
    """Offered rent falls outside the listing's published band → HTTP 422."""


class RateLimitError(ValidationException):
    """Too many applications from one account in the window → HTTP 429."""
