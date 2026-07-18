"""
Rentals Schemas

Pydantic models for rental listing request/response validation.

The public serializer is deliberately a separate, closed model
(PublicListing) rather than a redaction pass over the full listing dict:
owner PII (name/email/phone/user id, Fayda ID) can never leak through a
field that was never declared. Enforced by tests/test_rental_public_serializer.py.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ListingCreate(BaseModel):
    """Owner registers an existing property for rent."""

    property_id: int = Field(..., description="Existing property to list for rent")
    notes: Optional[str] = Field(None, max_length=1000, description="Optional note to the review officer")


class ListingReviewRequest(BaseModel):
    """Officer review action on a pending listing."""

    action: str = Field(..., description="'publish', 'adjust_band', or 'reject'")
    band_min: Optional[float] = Field(None, gt=0, description="Adjusted band lower bound (adjust_band)")
    band_max: Optional[float] = Field(None, gt=0, description="Adjusted band upper bound (adjust_band)")
    reason: Optional[str] = Field(None, max_length=1000, description="Mandatory for adjust_band and reject")

    @field_validator("action")
    @classmethod
    def validate_action(cls, v):
        allowed = ["publish", "adjust_band", "reject"]
        if v not in allowed:
            raise ValueError(f"action must be one of: {', '.join(allowed)}")
        return v


class ListingWithdrawRequest(BaseModel):
    reason: Optional[str] = Field(None, max_length=1000)


class OwnerVerifyRequest(BaseModel):
    """Officer verifies a citizen account as a property owner."""

    user_id: int = Field(..., description="User to verify as property owner")


# ---------------------------------------------------------------------------
# Public serializer — PII-redacted by construction
# ---------------------------------------------------------------------------

class PublicListingProperty(BaseModel):
    """Property facts safe for the public listing surface. No ownership data."""

    address: str
    municipality: str
    subcity: Optional[str] = None
    property_type: str
    property_subtype: Optional[str] = None
    area_sqm: float
    building_area_sqm: Optional[float] = None
    number_of_bedrooms: Optional[int] = None
    number_of_bathrooms: Optional[int] = None
    number_of_floors: Optional[int] = None
    year_built: Optional[int] = None
    condition: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    model_config = ConfigDict(extra="forbid")


class PublicListing(BaseModel):
    """A published listing as seen by anonymous renters. Closed model —
    owner identity, user ids, and internal integer PKs are not fields."""

    public_id: str
    suggested_rent: float
    band_min: float
    band_max: float
    published_at: Optional[datetime] = None
    has_valuation_certificate: bool = True
    property: PublicListingProperty

    model_config = ConfigDict(extra="forbid")


class PublicListingListResponse(BaseModel):
    success: bool
    data: List[PublicListing]
    total: int
    skip: int
    limit: int


class PublicListingResponse(BaseModel):
    success: bool
    data: PublicListing


# ---------------------------------------------------------------------------
# Authenticated (owner/officer) responses — envelope style matches the
# property/valuation modules
# ---------------------------------------------------------------------------

class ListingResponse(BaseModel):
    success: bool
    data: Optional[dict] = None
    message: Optional[str] = None


class ListingListResponse(BaseModel):
    success: bool
    data: Optional[List[dict]] = None
    total: Optional[int] = None
    skip: Optional[int] = None
    limit: Optional[int] = None
    message: Optional[str] = None
