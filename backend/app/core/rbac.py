"""
Role-Based Access Helpers (Phase E)

Shared staff/citizen gating used across every mounted router. The rentals
module already had its own owner/officer/renter guards
(app/modules/rentals/routes.py); this module generalizes the same
is_admin-honors-role pattern so the rest of the app (properties, valuations,
vehicles, scrapers, audit, analytics, users, settings) can deny citizen
tokens without duplicating the check per router.

Persona precedence mirrors the frontend (frontend/app/utils/persona.ts):
admin > rental_officer > property_owner > renter > staff. A plain valuer
account (no roles rows, is_admin=False) is "staff" — the pre-rentals
default — so existing valuer accounts see no behavior change.
"""

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.data.models.user import User

OFFICER_ROLE = "rental_officer"
PROPERTY_OWNER_ROLE = "property_owner"
RENTER_ROLE = "renter"
CITIZEN_ROLES = frozenset({PROPERTY_OWNER_ROLE, RENTER_ROLE})


def load_current_user(
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> User:
    """Resolve the bearer token to a full User row (roles included)."""
    user = db.query(User).filter(User.id == current_user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


def user_role_names(user: User) -> frozenset:
    try:
        return frozenset(role.name for role in user.roles)
    except Exception:
        return frozenset()


def is_rental_officer(user: User) -> bool:
    """Officer gate: the rental_officer role, honoring is_admin (seeded
    admin accounts may have no role rows — session learning)."""
    return bool(user.is_admin or OFFICER_ROLE in user_role_names(user))


def is_property_owner(user: User) -> bool:
    return PROPERTY_OWNER_ROLE in user_role_names(user)


def is_renter(user: User) -> bool:
    return RENTER_ROLE in user_role_names(user)


def is_staff(user: User) -> bool:
    """Staff = admin, or a regular account with no citizen/officer role
    (the pre-rentals valuer account shape). A rental_officer- or
    citizen-only account is never staff, even though it can authenticate."""
    if user.is_admin:
        return True
    roles = user_role_names(user)
    if roles & CITIZEN_ROLES:
        return False
    if OFFICER_ROLE in roles:
        return False
    return True


def require_staff(user: User = Depends(load_current_user)) -> User:
    """Dependency for staff-shell-only endpoints (dashboard, valuations,
    properties CRUD-all, vehicles, scrapers, reports, audit, analytics,
    settings, users). Citizens and rental officers are denied with 403."""
    if not is_staff(user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Staff access required",
        )
    return user
