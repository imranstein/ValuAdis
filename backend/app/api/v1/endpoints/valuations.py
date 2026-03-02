"""
Valuation Endpoints

RESTful API endpoints for property valuation operations
Following ValuAdis clean architecture and 7 pillars
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from app.services.valuation_service import ValuationService
from app.services.spatial_service import SpatialService
from app.schemas.valuation import (
    ValuationCreate, ValuationUpdate, ValuationResponse, 
    ValuationListResponse, ValuationDetail, ValuationCalculation
)
from app.core.exceptions import ValuAdisException, PropertyValidationError
from app.core.security import get_current_user_id
from app.core.database import get_db
from sqlalchemy.orm import Session
import structlog

logger = structlog.get_logger()

router = APIRouter()


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
        property_data = valuation_data.dict()
        
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


@router.get("/{valuation_id}", response_model=ValuationDetail, tags=["Valuations"])
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
            updates=valuation_update.dict(exclude_unset=True)
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
            valuation_id, valuation_update.dict(exclude_unset=True), user_id
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


@router.post("/calculate", response_model=ValuationCalculation, tags=["Valuations"])
async def calculate_valuation_only(
    valuation_data: ValuationCreate,
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
        property_data = valuation_data.dict()
        
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
        
        return calculation_result
        
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
