"""
Rentals Routes

/api/v1/rentals — government-mediated rental registry (Phase B).

Public (no auth): published-listing search, listing detail, citizen signup.
Owner (property_owner role): create listing, my-listings, withdraw.
Officer (rental_officer role): review queue, publish/adjust/reject, owner verify.
"""

import csv
import io
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import StreamingResponse
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
from app.modules.auth.routes import set_refresh_cookie
from app.modules.valuation.certificate_service import CertificateService
from app.services.auth_service import AuthService
from .application_service import RentalApplicationService
from .contract_service import TenancyContractService
from .exceptions import BandViolationError, RateLimitError, RenewalCapExceededError
from .index_service import RentIndexService
from .rate_limit import (
    SEARCH_RATE_LIMIT_MAX_REQUESTS,
    SEARCH_RATE_LIMIT_WINDOW_SECONDS,
    SIGNUP_RATE_LIMIT_MAX_REQUESTS,
    SIGNUP_RATE_LIMIT_WINDOW_SECONDS,
    client_ip,
    search_rate_limiter,
    signup_rate_limiter,
)
from .renewal_cap_service import RenewalCapService
from .schemas import (
    ApplicationCreate,
    ApplicationDecisionRequest,
    ContractCreate,
    ContractListResponse,
    ContractResponse,
    DepositRecordRequest,
    ListingCreate,
    ListingListResponse,
    ListingResponse,
    ListingReviewRequest,
    ListingWithdrawRequest,
    OwnerVerifyRequest,
    PublicListingListResponse,
    PublicListingResponse,
    RenewalCheckRequest,
    RentIndexResponse,
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


def require_renter(
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> User:
    user = _load_user(current_user_id, db)
    if user.is_admin or _has_role(user, ROLE_RENTER):
        return user
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Only renters can perform this action",
    )


def get_rentals_service(db: Session = Depends(get_db)) -> RentalListingService:
    return RentalListingService(db)


def get_application_service(db: Session = Depends(get_db)) -> RentalApplicationService:
    return RentalApplicationService(db)


def get_contract_service(db: Session = Depends(get_db)) -> TenancyContractService:
    return TenancyContractService(db)


def get_index_service(db: Session = Depends(get_db)) -> RentIndexService:
    return RentIndexService(db)


def get_renewal_cap_service(db: Session = Depends(get_db)) -> RenewalCapService:
    return RenewalCapService(db)


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
async def citizen_signup(signup: CitizenSignup, request: Request, response: Response, db: Session = Depends(get_db)):
    """Citizen signup with Fayda ID capture. Renter by default; property
    owners remain unverified until a rental officer verifies them."""
    try:
        signup_rate_limiter.check(
            client_ip(request), SIGNUP_RATE_LIMIT_WINDOW_SECONDS, SIGNUP_RATE_LIMIT_MAX_REQUESTS
        )
    except RateLimitError as exc:
        return _error(status.HTTP_429_TOO_MANY_REQUESTS, str(exc))

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
    # Refresh travels only in the httpOnly cookie (same flow as /auth/login);
    # a body copy would be JS-readable and would not survive a reload.
    set_refresh_cookie(response, create_refresh_token(data={"sub": str(user.id)}))
    return {
        "success": True,
        "message": "Registration successful",
        "data": {
            "access_token": access_token,
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
    request: Request,
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

    # Rate limit only the anonymous public-search path — an officer's
    # review-queue traffic above must never be throttled by this budget.
    try:
        search_rate_limiter.check(
            client_ip(request), SEARCH_RATE_LIMIT_WINDOW_SECONDS, SEARCH_RATE_LIMIT_MAX_REQUESTS
        )
    except RateLimitError as exc:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=str(exc))

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


# ---------------------------------------------------------------------------
# Rent index (Phase D) — public, aggregate-only
# ---------------------------------------------------------------------------

# Aggregation runs at most a few times a day (index_service.run_aggregation
# is a standalone/scheduled job, not per-request); a short public cache
# lets a shared cache or the browser avoid hammering the DB for a read that
# cannot change faster than that.
RENT_INDEX_CACHE_CONTROL = "public, max-age=300"


@router.get("/index", response_model=RentIndexResponse, tags=["Rentals"])
async def rent_index(
    response: Response,
    district: Optional[str] = None,
    property_subtype: Optional[str] = None,
    service: RentIndexService = Depends(get_index_service),
):
    """Public district rent index. Groups below the minimum-sample threshold
    are absent from the response, never zeroed or estimated — an empty
    result for a filter is the honest "insufficient data yet" state."""
    rows = service.get_public_index(district=district, property_subtype=property_subtype)
    response.headers["Cache-Control"] = RENT_INDEX_CACHE_CONTROL
    return RentIndexResponse(success=True, data=rows)


# ---------------------------------------------------------------------------
# Applications (Phase C)
# ---------------------------------------------------------------------------

@router.post(
    "/listings/{public_id}/applications",
    status_code=status.HTTP_201_CREATED,
    response_model=ContractResponse,
    tags=["Rentals"],
)
async def apply_to_listing(
    public_id: str,
    body: ApplicationCreate,
    renter: User = Depends(require_renter),
    service: RentalApplicationService = Depends(get_application_service),
):
    """Renter applies at an offered rent. The offer is validated server-side
    against the listing's frozen band; an out-of-band offer is a 422."""
    try:
        result = service.apply(public_id, renter, body.offered_rent, body.message)
        return ContractResponse(success=True, data=result, message="Application submitted")
    except BandViolationError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))
    except RateLimitError as exc:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=str(exc))
    except ValidationException as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except ValuAdisException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.get("/my-applications", response_model=ContractListResponse, tags=["Rentals"])
async def my_applications(
    skip: int = 0,
    limit: int = 20,
    current_user_id: int = Depends(get_current_user_id),
    service: RentalApplicationService = Depends(get_application_service),
):
    """The authenticated renter's applications (any status)."""
    applications, total = service.get_renter_applications(current_user_id, skip, max(1, min(limit, 100)))
    return ContractListResponse(success=True, data=applications, total=total, skip=skip, limit=limit)


@router.get("/listings/{public_id}/applications", response_model=ContractListResponse, tags=["Rentals"])
async def listing_applications(
    public_id: str,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
    service: RentalApplicationService = Depends(get_application_service),
):
    """Applications on a listing — the owner, or a rental officer preparing
    the contract from the accepted application."""
    actor = _load_user(current_user_id, db)
    try:
        applications = service.get_owner_listing_applications(public_id, actor)
        return ContractListResponse(success=True, data=applications, total=len(applications))
    except AuthorizationException as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    except ValuAdisException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.post("/applications/{application_id}/decision", response_model=ContractResponse, tags=["Rentals"])
async def decide_application(
    application_id: int,
    body: ApplicationDecisionRequest,
    owner: User = Depends(require_property_owner),
    service: RentalApplicationService = Depends(get_application_service),
):
    """Owner accepts or rejects an application. Accepting auto-rejects the
    pending siblings and moves the listing to `rented`."""
    try:
        result = service.decide(application_id, owner, body.action, body.reason)
        return ContractResponse(success=True, data=result, message=f"Application {body.action}ed")
    except AuthorizationException as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    except ValidationException as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except ValuAdisException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


# ---------------------------------------------------------------------------
# Contracts + deposits (Phase C, officer)
# ---------------------------------------------------------------------------

@router.post("/contracts", status_code=status.HTTP_201_CREATED, response_model=ContractResponse, tags=["Rentals"])
async def create_contract(
    body: ContractCreate,
    officer: User = Depends(require_rental_officer),
    service: TenancyContractService = Depends(get_contract_service),
):
    """Officer registers a tenancy contract from an accepted application.
    Generates the registry contract number; the contract stays `draft` until
    a matching deposit receipt is recorded."""
    try:
        result = service.create_contract(
            body.application_id,
            officer,
            body.start_date,
            body.end_date,
            body.deposit_amount,
            body.deposit_reason,
        )
        return ContractResponse(success=True, data=result, message="Contract registered (draft)")
    except ValidationException as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except ValuAdisException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.get("/contracts", response_model=ContractListResponse, tags=["Rentals"])
async def list_contracts(
    skip: int = 0,
    limit: int = 20,
    officer: User = Depends(require_rental_officer),
    service: TenancyContractService = Depends(get_contract_service),
):
    """Contracts registry (officer only)."""
    contracts, total = service.list_contracts(skip, max(1, min(limit, 100)))
    return ContractListResponse(success=True, data=contracts, total=total, skip=skip, limit=limit)


@router.get("/contracts/export", tags=["Rentals"])
async def export_contracts(
    officer: User = Depends(require_rental_officer),
    service: TenancyContractService = Depends(get_contract_service),
):
    """CSV export of the contracts registry — the tax-base deliverable for
    the administration (rental_officer only; party IDs are intentionally
    included, unlike every public serializer in this module)."""
    rows = service.list_contracts_for_export()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(
        [
            "contract_no", "property_address", "municipality", "subcity",
            "owner_name", "owner_fayda_id", "renter_name", "renter_fayda_id",
            "monthly_rent", "deposit_amount", "deposit_receipt_ref",
            "status", "start_date", "end_date", "created_at",
        ]
    )
    for row in rows:
        writer.writerow(
            [
                row["contract_no"], row["property_address"], row["municipality"], row["subcity"],
                row["owner_name"], row["owner_fayda_id"], row["renter_name"], row["renter_fayda_id"],
                row["monthly_rent"], row["deposit_amount"], row["deposit_receipt_ref"],
                row["status"], row["start_date"], row["end_date"], row["created_at"],
            ]
        )
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=rental_contracts_export.csv"},
    )


@router.get("/my-contracts", response_model=ContractListResponse, tags=["Rentals"])
async def my_contracts(
    skip: int = 0,
    limit: int = 100,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
    service: TenancyContractService = Depends(get_contract_service),
):
    """Contracts where the authenticated user is the owner or renter party."""
    user = _load_user(current_user_id, db)
    contracts, _ = service.list_contracts(0, 1000)
    contract_objs = {c["contract_no"]: c for c in contracts}
    visible = []
    for contract_no in contract_objs:
        contract = service.get_contract(contract_no)
        if contract and service.can_view_contract(contract, user):
            visible.append(contract_objs[contract_no])
    page = visible[skip: skip + max(1, min(limit, 100))]
    return ContractListResponse(success=True, data=page, total=len(visible), skip=skip, limit=limit)


@router.post("/contracts/{contract_no}/deposit", response_model=ContractResponse, tags=["Rentals"])
async def record_deposit(
    contract_no: str,
    body: DepositRecordRequest,
    officer: User = Depends(require_rental_officer),
    service: TenancyContractService = Depends(get_contract_service),
):
    """Officer records a deposit receipt. A matching amount activates the
    contract (draft → active); a mismatch is rejected."""
    try:
        result = service.record_deposit(
            contract_no, officer, body.deposit_receipt_ref, body.amount, body.paid_on
        )
        return ContractResponse(success=True, data=result, message="Deposit recorded; contract active")
    except ValidationException as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except ValuAdisException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.post("/contracts/{contract_no}/renewal", tags=["Rentals"])
async def check_contract_renewal(
    contract_no: str,
    body: RenewalCheckRequest,
    officer: User = Depends(require_rental_officer),
    contract_service: TenancyContractService = Depends(get_contract_service),
    cap_service: RenewalCapService = Depends(get_renewal_cap_service),
):
    """Contract-shape stub: validates a proposed renewal rent against the
    configured legal cap over the contract's current rent. Settles the API
    shape now; the full renewal workflow (a new contract record, signatures,
    PDF) is post-pilot (plan decision)."""
    contract = contract_service.get_contract(contract_no)
    if contract is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contract not found")

    try:
        result = cap_service.validate_renewal(contract.monthly_rent, body.proposed_rent)
    except RenewalCapExceededError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))
    except ValidationException as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    return {
        "success": True,
        "data": result,
        "message": "Renewal rent is within the legal cap. Full renewal registration is not yet available.",
    }


@router.get("/contracts/{contract_no}/pdf", tags=["Rentals"])
async def download_contract_pdf(
    contract_no: str,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
    service: TenancyContractService = Depends(get_contract_service),
):
    """Download the registered tenancy contract PDF. Visible to the owner or
    renter party, or a rental officer."""
    user = _load_user(current_user_id, db)
    contract = service.get_contract(contract_no)
    if contract is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contract not found")
    if not service.can_view_contract(contract, user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a party to this contract")

    context = service.build_pdf_context(contract)
    cert_service = CertificateService()
    pdf_bytes = await run_in_threadpool(
        cert_service.generate_tenancy_contract,
        context["contract"],
        context["owner"],
        context["renter"],
        context["property_data"],
        context["rent_context"],
    )
    filename = f"ValuAdis_Contract_{contract_no}.pdf"
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/listings/{public_id}/agreement", tags=["Rentals"])
async def download_listing_agreement(
    public_id: str,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
    service: RentalListingService = Depends(get_rentals_service),
):
    """Download the owner ↔ administration listing agreement PDF generated at
    publish time. Visible to the listing owner or a rental officer."""
    actor = _load_user(current_user_id, db)
    try:
        context = service.build_listing_agreement_context(public_id, actor)
    except AuthorizationException as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    except ValidationException as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except ValuAdisException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))

    cert_service = CertificateService()
    pdf_bytes = await run_in_threadpool(
        cert_service.generate_listing_agreement,
        context["listing"],
        context["owner"],
        context["property_data"],
    )
    filename = f"ValuAdis_ListingAgreement_{public_id}.pdf"
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


def _error(status_code: int, message: str):
    from fastapi.responses import JSONResponse

    return JSONResponse(status_code=status_code, content={"success": False, "message": message})
