"""
Rentals Routes

/api/v1/rentals — government-mediated rental registry (Phase B).

Public (no auth): published-listing search, listing detail, citizen signup.
Owner (property_owner role): create listing, my-listings, withdraw.
Officer (rental_officer role): review queue, publish/adjust/reject, owner verify.
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, EmailStr, Field, field_validator
from sqlalchemy.orm import Session
import structlog

from app.core.config import settings
from app.core.database import get_db
from app.core.exceptions import (
    AuthorizationException,
    ValidationException,
    ValuAdisException,
)
from app.core.security import (
    create_access_token,
    create_refresh_token,
    get_current_user_id,
    validate_ethiopian_phone_number,
)
from app.data.models.role import Role
from app.data.models.user import User
from app.services.auth_service import AuthService
from .schemas import (
    ListingCreate,
    ListingListResponse,
    ListingResponse,
    ListingReviewRequest,
    ListingWithdrawRequest,
    OwnerVerifyRequest,
    PublicListingListResponse,
    PublicListingResponse,
)
from .services import RentalListingService, _is_rental_officer

logger = structlog.get_logger()

router = APIRouter()
optional_bearer = HTTPBearer(auto_error=False)

ROLE_RENTER = "renter"
ROLE_PROPERTY_OWNER = "property_owner"
ROLE_RENTAL_OFFICER = "rental_officer"

CITIZEN_ACCOUNT_TYPES = (ROLE_RENTER, ROLE_PROPERTY_OWNER)

ROLE_DISPLAY_NAMES = {
    ROLE_RENTER: "Renter",
    ROLE_PROPERTY_OWNER: "Property Owner",
    ROLE_RENTAL_OFFICER: "Rental Officer",
}


# ---------------------------------------------------------------------------
# Role guards
# ---------------------------------------------------------------------------

def _load_user(user_id: int, db: Session) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


def _has_role(user: User, role_name: str) -> bool:
    try:
        return any(role.name == role_name for role in user.roles)
    except Exception:
        return False


def require_property_owner(
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> User:
    user = _load_user(current_user_id, db)
    if user.is_admin or _has_role(user, ROLE_PROPERTY_OWNER):
        return user
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Only property owners can perform this action",
    )


def require_rental_officer(
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> User:
    user = _load_user(current_user_id, db)
    if _is_rental_officer(user):
        return user
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Only rental officers can perform this action",
    )


def get_rentals_service(db: Session = Depends(get_db)) -> RentalListingService:
    return RentalListingService(db)


# ---------------------------------------------------------------------------
# Citizen signup (public)
# ---------------------------------------------------------------------------

class CitizenSignup(BaseModel):
    """Citizen self-registration for the rental registry.

    Kept separate from /auth/register (the valuer registration contract is
    frozen). Captures the Fayda national ID; new accounts default to the
    renter role, and property_owner accounts stay unverified until a
    rental officer verifies them.
    """

    email: EmailStr
    full_name: str = Field(..., min_length=3)
    phone: str
    password: str
    municipality: str = Field(..., min_length=2)
    fayda_id_number: str = Field(..., min_length=6, max_length=50)
    account_type: str = Field(ROLE_RENTER, description="'renter' (default) or 'property_owner'")

    @field_validator("account_type")
    @classmethod
    def validate_account_type(cls, v):
        if v not in CITIZEN_ACCOUNT_TYPES:
            raise ValueError(f"account_type must be one of: {', '.join(CITIZEN_ACCOUNT_TYPES)}")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        # Same policy as auth UserRegister
        import re

        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[0-9]", v):
            raise ValueError("Password must contain at least one digit")
        if not re.search(r"[^A-Za-z0-9]", v):
            raise ValueError("Password must contain at least one special character")
        return v


def _get_or_create_role(db: Session, name: str) -> Role:
    role = db.query(Role).filter(Role.name == name).first()
    if role is None:
        role = Role(
            name=name,
            display_name=ROLE_DISPLAY_NAMES.get(name, name.replace("_", " ").title()),
            description=f"Rentals module role: {name}",
            is_active=True,
        )
        db.add(role)
        db.commit()
        db.refresh(role)
    return role


@router.post("/signup", status_code=status.HTTP_201_CREATED, tags=["Rentals"])
async def citizen_signup(signup: CitizenSignup, db: Session = Depends(get_db)):
    """Citizen signup with Fayda ID capture. Renter by default; property
    owners remain unverified until a rental officer verifies them."""
    if not validate_ethiopian_phone_number(signup.phone):
        return _error(status.HTTP_422_UNPROCESSABLE_ENTITY, "Invalid Ethiopian phone number format")

    existing_fayda = db.query(User).filter(User.fayda_id_number == signup.fayda_id_number).first()
    if existing_fayda:
        return _error(status.HTTP_400_BAD_REQUEST, "Fayda ID already registered")

    auth_service = AuthService(db)
    try:
        user = await auth_service.create_user(
            {
                "email": signup.email,
                "full_name": signup.full_name,
                "phone": signup.phone,
                "password": signup.password,
                "municipality": signup.municipality,
                # Citizens have no valuer license; the registry reference is
                # derived from their (unique) Fayda ID — not a fabricated value.
                "license_number": f"FAYDA-{signup.fayda_id_number}",
                "fayda_id_number": signup.fayda_id_number,
            }
        )
    except ValidationException as exc:
        return _error(status.HTTP_400_BAD_REQUEST, str(exc))

    role = _get_or_create_role(db, signup.account_type)
    user.roles.append(role)
    db.add(user)
    db.commit()

    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    return {
        "success": True,
        "message": "Registration successful",
        "data": {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "account_type": signup.account_type,
            "owner_verified": bool(user.owner_verified),
        },
    }


# ---------------------------------------------------------------------------
# Listings — create (owner), browse (public), review queue (officer)
# ---------------------------------------------------------------------------

@router.post("/listings", status_code=status.HTTP_201_CREATED, response_model=ListingResponse, tags=["Rentals"])
async def create_listing(
    listing_data: ListingCreate,
    owner: User = Depends(require_property_owner),
    service: RentalListingService = Depends(get_rentals_service),
):
    """Owner registers an existing property for rent (auto rent valuation,
    listing enters pending_review with the suggested band)."""
    try:
        result = service.create_listing(listing_data.property_id, owner, listing_data.notes)
        return ListingResponse(success=True, data=result, message="Listing submitted for review")
    except ValidationException as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.get("/listings", tags=["Rentals"])
async def browse_listings(
    status_filter: Optional[str] = Query(None, alias="status"),
    district: Optional[str] = None,
    property_subtype: Optional[str] = None,
    bedrooms: Optional[int] = None,
    band_min: Optional[float] = None,
    band_max: Optional[float] = None,
    skip: int = 0,
    limit: int = 20,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(optional_bearer),
    db: Session = Depends(get_db),
    service: RentalListingService = Depends(get_rentals_service),
):
    """Published-listing search (public, PII-redacted).

    With an explicit ?status=… (any value, including published) this
    becomes the officer review queue — full listing detail including owner
    verification state — and requires a rental_officer bearer token.
    Public browsing never needs the status param; it always sees published
    listings only, through the redacted serializer.
    """
    limit = max(1, min(limit, 100))
    skip = max(0, skip)

    if status_filter:
        if credentials is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
        user = _load_user(get_current_user_id(credentials.credentials), db)
        if not _is_rental_officer(user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only rental officers can view non-published listings",
            )
        listings, total = service.get_review_queue(status_filter, skip, limit)
        return ListingListResponse(success=True, data=listings, total=total, skip=skip, limit=limit)

    listings, total = service.search_published(
        district=district,
        property_subtype=property_subtype,
        bedrooms=bedrooms,
        band_min=band_min,
        band_max=band_max,
        skip=skip,
        limit=limit,
    )
    return PublicListingListResponse(success=True, data=listings, total=total, skip=skip, limit=limit)


@router.get("/my-listings", response_model=ListingListResponse, tags=["Rentals"])
async def my_listings(
    skip: int = 0,
    limit: int = 20,
    current_user_id: int = Depends(get_current_user_id),
    service: RentalListingService = Depends(get_rentals_service),
):
    """Authenticated owner's listings (any status)."""
    listings, total = service.get_owner_listings(current_user_id, skip, max(1, min(limit, 100)))
    return ListingListResponse(success=True, data=listings, total=total, skip=skip, limit=limit)


@router.get("/listings/{public_id}", response_model=PublicListingResponse, tags=["Rentals"])
async def get_listing(
    public_id: str,
    service: RentalListingService = Depends(get_rentals_service),
):
    """Public listing detail. Unpublished listings are a public 404."""
    listing = service.get_public_listing(public_id)
    if listing is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found")
    return PublicListingResponse(success=True, data=listing)


@router.patch("/listings/{public_id}/review", response_model=ListingResponse, tags=["Rentals"])
async def review_listing(
    public_id: str,
    review: ListingReviewRequest,
    officer: User = Depends(require_rental_officer),
    service: RentalListingService = Depends(get_rentals_service),
):
    """Officer review action: publish, adjust_band (mandatory reason), or
    reject (mandatory reason). All actions are audit-logged; band values
    freeze on publish."""
    try:
        result = service.review_listing(
            public_id,
            officer,
            action=review.action,
            band_min=review.band_min,
            band_max=review.band_max,
            reason=review.reason,
        )
        return ListingResponse(success=True, data=result, message=f"Listing {review.action} applied")
    except ValidationException as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except ValuAdisException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.post("/listings/{public_id}/withdraw", response_model=ListingResponse, tags=["Rentals"])
async def withdraw_listing(
    public_id: str,
    body: ListingWithdrawRequest,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
    service: RentalListingService = Depends(get_rentals_service),
):
    """Withdraw a listing (owner or officer). A published listing must be
    withdrawn before its band can be reviewed again."""
    actor = _load_user(current_user_id, db)
    try:
        result = service.withdraw_listing(public_id, actor, body.reason)
        return ListingResponse(success=True, data=result, message="Listing withdrawn")
    except AuthorizationException as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    except ValidationException as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except ValuAdisException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.post("/owners/verify", tags=["Rentals"])
async def verify_owner(
    body: OwnerVerifyRequest,
    officer: User = Depends(require_rental_officer),
    service: RentalListingService = Depends(get_rentals_service),
):
    """Officer verifies a citizen account as a property owner (audited).
    Unverified owners can draft listings but cannot be published."""
    try:
        result = service.verify_owner(body.user_id, officer)
        return {"success": True, "data": result, "message": "Owner verified"}
    except ValidationException as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except ValuAdisException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


def _error(status_code: int, message: str):
    from fastapi.responses import JSONResponse

    return JSONResponse(status_code=status_code, content={"success": False, "message": message})
