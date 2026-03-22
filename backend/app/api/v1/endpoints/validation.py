"""
License Validation Endpoints

API endpoints for validating Ethiopian business licenses
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from pydantic import BaseModel
from typing import Optional
from app.core.security import validate_ethiopian_license

router = APIRouter()
security = HTTPBearer()


class LicenseValidationRequest(BaseModel):
    """Request model for license validation"""
    license: str


class LicenseValidationResponse(BaseModel):
    """Response model for license validation"""
    valid: bool
    error: Optional[str] = None
    region: Optional[str] = None
    prefix: Optional[str] = None


@router.post("/license", response_model=LicenseValidationResponse, tags=["Validation"])
async def validate_license(request: LicenseValidationRequest):
    """
    Validate an Ethiopian business license number

    Accepts a license string and validates it against Ethiopian business license format.
    Returns validation result with optional error message and region information.

    Expected format: XXX-NNNNNNNNNN (e.g., AA-1234567890)
    - 2-4 uppercase letters (prefix indicating region/authority)
    - Hyphen separator
    - 6-10 digits
    """
    try:
        result = validate_ethiopian_license(request.license)

        if result["valid"]:
            # Extract prefix for region lookup
            parts = request.license.strip().upper().split('-')
            prefix = parts[0] if len(parts) > 0 else None
            region = get_license_region(prefix) if prefix else None

            return LicenseValidationResponse(
                valid=True,
                region=region,
                prefix=prefix
            )
        else:
            return LicenseValidationResponse(
                valid=False,
                error=result.get("error", "Invalid license format")
            )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"License validation failed: {str(e)}"
        )


# Ethiopian license prefix to region mapping
ETHIOPIAN_LICENSE_PREFIXES = {
    "AA": "Addis Ababa City Administration",
    "AD": "Adama City Administration",
    "BA": "Bahir Dar City Administration",
    "DD": "Dire Dawa City Administration",
    "HA": "Hawassa City Administration",
    "ME": "Mekelle City Administration",
    "GO": "Gondar City Administration",
    "JI": "Jimma City Administration",
    "DE": "Dessie City Administration",
    "TR": "Tigray Regional State",
    "AM": "Amhara Regional State",
    "OR": "Oromia Regional State",
    "SN": "Southern Nations, Nationalities, and Peoples Regional State",
    "AF": "Afar Regional State",
    "SO": "Somali Regional State",
    "BE": "Benishangul-Gumuz Regional State",
    "GA": "Gambela Regional State",
    "SI": "Sidama Regional State",
    "SW": "South West Ethiopia Peoples Regional State"
}


def get_license_region(prefix: str) -> Optional[str]:
    """
    Get the region/authority name for a license prefix

    Args:
        prefix: The 2-4 letter license prefix

    Returns:
        Region name or None if not recognized
    """
    if not prefix:
        return None
    return ETHIOPIAN_LICENSE_PREFIXES.get(prefix.upper())


@router.get("/license/prefixes", tags=["Validation"])
async def get_license_prefixes():
    """
    Get all recognized Ethiopian license prefixes and their regions

    Returns a dictionary mapping license prefixes to their corresponding
    regions/authorities.
    """
    return {
        "prefixes": ETHIOPIAN_LICENSE_PREFIXES,
        "count": len(ETHIOPIAN_LICENSE_PREFIXES)
    }
