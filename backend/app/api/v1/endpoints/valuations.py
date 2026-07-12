"""
Valuation Endpoints

RESTful API endpoints for property valuation operations
Following ValuAdis clean architecture and 7 pillars
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from starlette.concurrency import run_in_threadpool
from typing import List, Optional
import io
import csv
from app.services.valuation_service import ValuationService
from app.services.spatial_service import SpatialService
from app.services.certificate_service import CertificateService
from app.services.auth_service import AuthService
from app.schemas.valuation import (
    ValuationCreate, ValuationUpdate, ValuationResponse,
    ValuationListResponse, ValuationDetail, ValuationCalculation,
    ValuationOverrideRequest, ValuationStatusTransitionRequest,
)
from app.core.exceptions import ValuAdisException, PropertyValidationError
from app.core.security import get_current_user_id
from app.core.database import get_db
from app.data.models.user import User
from sqlalchemy.orm import Session
import structlog

logger = structlog.get_logger()

router = APIRouter()

ALLOWED_OVERRIDE_ROLES = ["system_admin", "firm_admin", "municipal_admin", "senior_valuer"]


def require_valuation_override_permission(
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> User:
    """Dependency: only admins or senior valuers can override valuations."""
    user = db.query(User).filter(User.id == current_user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if user.is_admin:
        return user
    if any(role.name in ALLOWED_OVERRIDE_ROLES for role in user.roles):
        return user
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Only admins or senior valuers can override valuations",
    )


def get_valuation_service(db: Session = Depends(get_db)) -> ValuationService:
    """Dependency injection for valuation service"""
    spatial_service = SpatialService()
    return ValuationService(spatial_service, db)


@router.post("/", response_model=ValuationResponse, status_code=status.HTTP_201_CREATED, tags=["Valuations"])
async def create_valuation(
    valuation_data: ValuationCreate,
    user_id: int = Depends(get_current_user_id),
    valuation_service: ValuationService = Depends(get_valuation_service)
):
    """
    Create a new property valuation
    
    Calculates market value and taxable value per Ethiopian standards
    """
    try:
        logger.info(
            "Creating valuation",
            property_id=valuation_data.property_id,
            user_id=user_id,
            municipality=valuation_data.municipality
        )
        
        # Convert Pydantic model to dict for service
        property_data = valuation_data.model_dump()
        
        # Calculate market value
        market_value = valuation_service.calculate_market_value(property_data)
        
        # Calculate taxable value (25% per Proclamation 1365/2025)
        taxable_value = valuation_service.calculate_taxable_value(market_value)
        
        # Create valuation record
        valuation_result = valuation_service.create_valuation(valuation_data, user_id)
        
        logger.info(
            "Valuation created successfully",
            valuation_id=valuation_result.get("id"),
            market_value=float(market_value),
            taxable_value=float(taxable_value)
        )
        
        return ValuationResponse(
            success=True,
            data={
                **valuation_result,
                "market_value": float(market_value),
                "taxable_value": float(taxable_value)
            },
            message="Valuation created successfully"
        )
        
    except PropertyValidationError as e:
        logger.warning("Property validation failed", error=str(e), user_id=user_id)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except ValuAdisException as e:
        logger.error("Valuation creation failed", error=str(e), user_id=user_id)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error("Unexpected error in valuation creation", error=str(e), user_id=user_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/export", tags=["Valuations"])
async def export_valuations(
    format: str = "csv",
    user_id: int = Depends(get_current_user_id),
    valuation_service: ValuationService = Depends(get_valuation_service),
):
    """Export valuations as CSV"""
    if format.lower() != "csv":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only CSV format is supported")
    valuations, _ = valuation_service.get_user_valuations(user_id=user_id, skip=0, limit=10000)
    output = io.StringIO()
    writer = csv.writer(output)
    headers = ["id", "property_id", "property_type", "municipality", "area_sqm", "market_value", "taxable_value", "status", "valuation_date", "created_at"]
    writer.writerow(headers)
    for v in valuations:
        writer.writerow([
            v.get("id"),
            v.get("property_id"),
            v.get("property_type", ""),
            v.get("municipality", ""),
            v.get("area_sqm"),
            v.get("market_value"),
            v.get("taxable_value"),
            v.get("status", ""),
            v.get("valuation_date", ""),
            v.get("created_at", ""),
        ])
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=valuations_export.csv"},
    )


@router.get("/{valuation_id}", response_model=ValuationResponse, tags=["Valuations"])
async def get_valuation(
    valuation_id: int,
    user_id: int = Depends(get_current_user_id),
    valuation_service: ValuationService = Depends(get_valuation_service)
):
    """
    Get a specific valuation by ID
    """
    try:
        logger.info("Fetching valuation", valuation_id=valuation_id, user_id=user_id)
        
        valuation = valuation_service.get_valuation_by_id(valuation_id, user_id)
        
        if not valuation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Valuation not found"
            )
        
        logger.info("Valuation retrieved successfully", valuation_id=valuation_id)
        
        return ValuationResponse(
            success=True,
            data=valuation,
            message="Valuation retrieved successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error fetching valuation", error=str(e), valuation_id=valuation_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/", response_model=ValuationListResponse, tags=["Valuations"])
async def get_user_valuations(
    skip: int = 0,
    limit: int = 100,
    user_id: int = Depends(get_current_user_id),
    valuation_service: ValuationService = Depends(get_valuation_service)
):
    """
    Get all valuations for the current user
    """
    try:
        logger.info("Fetching user valuations", user_id=user_id, skip=skip, limit=limit)
        
        valuations, total = valuation_service.get_user_valuations(user_id, skip, limit)
        
        logger.info(
            "User valuations retrieved successfully",
            user_id=user_id,
            count=len(valuations),
            total=total
        )
        
        return ValuationListResponse(
            success=True,
            data=valuations,
            total=total,
            skip=skip,
            limit=limit,
            message="Valuations retrieved successfully"
        )
        
    except Exception as e:
        logger.error("Error fetching user valuations", error=str(e), user_id=user_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.put("/{valuation_id}", response_model=ValuationResponse, tags=["Valuations"])
async def update_valuation(
    valuation_id: int,
    valuation_update: ValuationUpdate,
    user_id: int = Depends(get_current_user_id),
    valuation_service: ValuationService = Depends(get_valuation_service)
):
    """
    Update a valuation (status changes only)
    """
    try:
        logger.info(
            "Updating valuation",
            valuation_id=valuation_id,
            user_id=user_id,
            updates=valuation_update.model_dump(exclude_unset=True)
        )
        
        # Check if valuation exists and belongs to user
        existing_valuation = valuation_service.get_valuation_by_id(valuation_id, user_id)
        if not existing_valuation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Valuation not found"
            )
        
        # Update valuation
        updated_valuation = valuation_service.update_valuation(
            valuation_id, valuation_update.model_dump(exclude_unset=True), user_id
        )
        
        logger.info("Valuation updated successfully", valuation_id=valuation_id)
        
        return ValuationResponse(
            success=True,
            data=updated_valuation,
            message="Valuation updated successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error updating valuation", error=str(e), valuation_id=valuation_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.delete("/{valuation_id}", response_model=ValuationResponse, tags=["Valuations"])
async def delete_valuation(
    valuation_id: int,
    user_id: int = Depends(get_current_user_id),
    valuation_service: ValuationService = Depends(get_valuation_service)
):
    """
    Delete a valuation
    """
    try:
        logger.info("Deleting valuation", valuation_id=valuation_id, user_id=user_id)
        
        # Check if valuation exists and belongs to user
        existing_valuation = valuation_service.get_valuation_by_id(valuation_id, user_id)
        if not existing_valuation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Valuation not found"
            )
        
        # Delete valuation
        success = valuation_service.delete_valuation(valuation_id, user_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to delete valuation"
            )
        
        logger.info("Valuation deleted successfully", valuation_id=valuation_id)
        
        return ValuationResponse(
            success=True,
            data={"id": valuation_id},
            message="Valuation deleted successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error deleting valuation", error=str(e), valuation_id=valuation_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/{valuation_id}/certificate", tags=["Valuations"])
async def download_certificate(
    valuation_id: int,
    user_id: int = Depends(get_current_user_id),
    valuation_service: ValuationService = Depends(get_valuation_service),
    db: Session = Depends(get_db),
):
    """
    Generate and download a Proclamation 1365/2025-compliant PDF certificate
    for an approved valuation.
    """
    try:
        valuation = valuation_service.get_valuation_by_id(valuation_id, user_id)
        if not valuation:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Valuation not found")

        # Only issue certificates for approved valuations
        if valuation.get("status") != "approved":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Certificate can only be generated for approved valuations",
            )

        # Fetch owner name via auth service
        auth_svc = AuthService(db)
        owner = await auth_svc.get_user_by_id(user_id)
        owner_name = owner.full_name if owner else "Unknown Owner"

        # Property data may be embedded in valuation or fetched separately
        property_data = {
            "address":             valuation.get("address", "—"),
            "municipality":        valuation.get("municipality", "—"),
            "property_type":       valuation.get("property_type", "residential"),
            "area_sqm":            valuation.get("area_sqm", 0),
            "condition":           valuation.get("condition", "good"),
            "neighborhood_quality": valuation.get("neighborhood_quality", "average"),
        }

        cert_service = CertificateService()
        # ReportLab is CPU-bound; run in a threadpool to avoid blocking the
        # async event loop under concurrent load.
        pdf_bytes = await run_in_threadpool(
            cert_service.generate_certificate,
            valuation,
            property_data,
            owner_name,
        )

        filename = f"ValuAdis_Certificate_{valuation_id}.pdf"
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error generating certificate", error=str(e), valuation_id=valuation_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Certificate generation failed",
        ) from e


@router.patch("/{valuation_id}/override", response_model=ValuationResponse, tags=["Valuations"])
async def override_valuation(
    valuation_id: int,
    override_data: ValuationOverrideRequest,
    _: User = Depends(require_valuation_override_permission),
    valuation_service: ValuationService = Depends(get_valuation_service),
):
    """
    Override market_value and taxable_value (admin/senior valuer only).

    Used when senior valuers need to adjust algorithm-calculated values
    based on professional judgment.
    """
    try:
        result = valuation_service.override_valuation(
            valuation_id=valuation_id,
            market_value=override_data.market_value,
            taxable_value=override_data.taxable_value,
            override_reason=override_data.override_reason,
        )
        return ValuationResponse(
            success=True,
            data=result,
            message="Valuation override applied successfully",
        )
    except ValuAdisException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error("Valuation override failed", error=str(e), valuation_id=valuation_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Valuation override failed",
        )


@router.patch("/{valuation_id}/status", response_model=ValuationResponse, tags=["Valuations"])
async def transition_valuation_status(
    valuation_id: int,
    transition_data: ValuationStatusTransitionRequest,
    user_id: int = Depends(get_current_user_id),
    valuation_service: ValuationService = Depends(get_valuation_service),
):
    """
    Transition a valuation to a new status.

    Valid transitions:
    - draft → pending
    - pending → approved | rejected
    - approved → archived

    Invalid transitions are rejected with HTTP 400.
    """
    try:
        logger.info(
            "Transitioning valuation status",
            valuation_id=valuation_id,
            new_status=transition_data.status,
            actor_user_id=user_id,
        )

        result = valuation_service.transition_status(
            valuation_id=valuation_id,
            new_status=transition_data.status,
            actor_user_id=user_id,
            reason=transition_data.reason,
        )

        logger.info(
            "Valuation status transitioned successfully",
            valuation_id=valuation_id,
            new_status=transition_data.status,
        )

        return ValuationResponse(
            success=True,
            data=result,
            message=f"Valuation status updated to '{transition_data.status}'",
        )

    except ValuAdisException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error transitioning valuation status", error=str(e), valuation_id=valuation_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.post("/quick", response_model=ValuationCalculation, tags=["Valuations"])
async def quick_valuation(
    valuation_data: dict,
    _: int = Depends(get_current_user_id),
    valuation_service: ValuationService = Depends(get_valuation_service)
):
    """
    Quick valuation without requiring existing property
    
    Useful for standalone valuation calculations
    """
    try:
        logger.info(
            "Quick valuation calculation",
            property_type=valuation_data.get("property_type"),
            municipality=valuation_data.get("municipality"),
            area_sqm=valuation_data.get("area_sqm")
        )
        
        # Add default coordinates if not provided
        if "coordinates" not in valuation_data:
            # Default to Addis Ababa coordinates as closed polygon [longitude, latitude]
            valuation_data["coordinates"] = [
                [38.7000, 9.0000],
                [38.7500, 9.0500],
                [38.7500, 9.0000],
                [38.7000, 9.0000]
            ]
        
        # Add default property_id if not provided
        if "property_id" not in valuation_data:
            valuation_data["property_id"] = 0  # Use 0 for quick valuations
        
        # Calculate market value
        market_value = valuation_service.calculate_market_value(valuation_data)
        
        # Calculate taxable value (25% per Proclamation 1365/2025)
        taxable_value = valuation_service.calculate_taxable_value(market_value)
        
        calculation_result = ValuationCalculation(
            market_value=float(market_value),
            taxable_value=float(taxable_value),
            base_rate=float(valuation_service._base_rates.get(valuation_data.get("municipality"), 0)),
            multiplier=float(valuation_service._property_type_multipliers.get(valuation_data.get("property_type"), 1.0))
        )
        
        logger.info(
            "Quick valuation calculation completed",
            market_value=float(market_value),
            taxable_value=float(taxable_value)
        )
        
        return calculation_result
        
    except (PropertyValidationError, ValuAdisException) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error("Error in quick valuation", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.post("/calculate", response_model=ValuationResponse, tags=["Valuations"])
async def calculate_valuation_only(
    valuation_data: ValuationCreate,
    _: int = Depends(get_current_user_id),
    valuation_service: ValuationService = Depends(get_valuation_service)
):
    """
    Calculate valuation without saving to database
    
    Useful for preview calculations
    """
    try:
        logger.info(
            "Calculating valuation preview",
            property_id=valuation_data.property_id,
            municipality=valuation_data.municipality
        )
        
        # Convert Pydantic model to dict for service
        property_data = valuation_data.model_dump()
        
        # Calculate market value
        market_value = valuation_service.calculate_market_value(property_data)
        
        # Calculate taxable value (25% per Proclamation 1365/2025)
        taxable_value = valuation_service.calculate_taxable_value(market_value)
        
        calculation_result = ValuationCalculation(
            market_value=float(market_value),
            taxable_value=float(taxable_value),
            base_rate=float(valuation_service._base_rates.get(valuation_data.municipality, 0)),
            multiplier=float(valuation_service._property_type_multipliers.get(valuation_data.property_type, 1.0))
        )
        
        logger.info(
            "Valuation calculation completed",
            market_value=float(market_value),
            taxable_value=float(taxable_value)
        )
        
        return ValuationResponse(
            success=True,
            data=calculation_result.model_dump(),
            message="Valuation calculated successfully",
        )
        
    except (PropertyValidationError, ValuAdisException) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error("Error calculating valuation", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
