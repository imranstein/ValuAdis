"""
Vehicle Valuation API Routes

FastAPI endpoints for vehicle management and valuation operations.
"""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.data.models.user import User
from .services import VehicleValuationService
from .schemas import (
    VehicleCreate, VehicleUpdate, VehicleResponse, VehicleListResponse,
    VehicleValuationCreate, VehicleValuationUpdate, VehicleValuationResponse, VehicleValuationListResponse,
    VehicleAnalysisRequest, VehicleAnalysisResponse,
    VehicleCertificateRequest, VehicleCertificateResponse
)

router = APIRouter(prefix="/vehicles", tags=["vehicles"])


def get_vehicle_service(db: Session = Depends(get_db)) -> VehicleValuationService:
    """Dependency injection for vehicle service"""
    return VehicleValuationService(db)


# Vehicle Management Routes
@router.post("/", response_model=VehicleResponse, status_code=status.HTTP_201_CREATED)
def create_vehicle(
    vehicle_data: VehicleCreate,
    current_user: User = Depends(get_current_user),
    vehicle_service: VehicleValuationService = Depends(get_vehicle_service)
):
    """Create a new vehicle record"""
    try:
        vehicle = vehicle_service.create_vehicle(vehicle_data, current_user.id)
        return vehicle
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/", response_model=VehicleListResponse)
def list_vehicles(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    query: Optional[str] = Query(None),
    make: Optional[str] = Query(None),
    model: Optional[str] = Query(None),
    year_min: Optional[int] = Query(None),
    year_max: Optional[int] = Query(None),
    region: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    vehicle_service: VehicleValuationService = Depends(get_vehicle_service)
):
    """List vehicles with search and filters"""
    vehicles = vehicle_service.search_vehicles(
        query=query,
        make=make,
        model=model,
        year_min=year_min,
        year_max=year_max,
        region=region,
        skip=skip,
        limit=limit
    )
    
    # Get total count (simplified - in production, use separate count query)
    total = len(vehicles)
    
    return VehicleListResponse(
        vehicles=vehicles,
        total=total,
        page=skip // limit + 1,
        per_page=limit,
        pages=(total + limit - 1) // limit
    )


@router.get("/my-vehicles", response_model=VehicleListResponse)
def get_my_vehicles(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
    vehicle_service: VehicleValuationService = Depends(get_vehicle_service)
):
    """Get current user's vehicles"""
    vehicles = vehicle_service.get_owner_vehicles(current_user.id, skip, limit)
    total = vehicle_service.vehicle_repo.count_owner_vehicles(current_user.id)
    
    return VehicleListResponse(
        vehicles=vehicles,
        total=total,
        page=skip // limit + 1,
        per_page=limit,
        pages=(total + limit - 1) // limit
    )


@router.get("/{vehicle_id}", response_model=VehicleResponse)
def get_vehicle(
    vehicle_id: UUID,
    current_user: User = Depends(get_current_user),
    vehicle_service: VehicleValuationService = Depends(get_vehicle_service)
):
    """Get vehicle by ID"""
    vehicle = vehicle_service.get_vehicle(vehicle_id)
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found"
        )
    
    # Check ownership or admin access
    if vehicle.owner_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return vehicle


@router.put("/{vehicle_id}", response_model=VehicleResponse)
def update_vehicle(
    vehicle_id: UUID,
    update_data: VehicleUpdate,
    current_user: User = Depends(get_current_user),
    vehicle_service: VehicleValuationService = Depends(get_vehicle_service)
):
    """Update vehicle information"""
    vehicle = vehicle_service.get_vehicle(vehicle_id)
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found"
        )
    
    # Check ownership or admin access
    if vehicle.owner_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    try:
        updated_vehicle = vehicle_service.update_vehicle(vehicle_id, update_data)
        return updated_vehicle
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{vehicle_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_vehicle(
    vehicle_id: UUID,
    current_user: User = Depends(get_current_user),
    vehicle_service: VehicleValuationService = Depends(get_vehicle_service)
):
    """Delete a vehicle"""
    vehicle = vehicle_service.get_vehicle(vehicle_id)
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found"
        )
    
    # Check ownership or admin access
    if vehicle.owner_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    vehicle_service.delete_vehicle(vehicle_id)


# Vehicle Valuation Routes
@router.post("/{vehicle_id}/valuations", response_model=VehicleValuationResponse)
def create_valuation(
    vehicle_id: UUID,
    valuation_data: VehicleValuationCreate,
    current_user: User = Depends(get_current_user),
    vehicle_service: VehicleValuationService = Depends(get_vehicle_service)
):
    """Create a vehicle valuation"""
    # Verify vehicle exists and user has access
    vehicle = vehicle_service.get_vehicle(vehicle_id)
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found"
        )
    
    # Only valuers or admins can create valuations
    if not (current_user.is_valuer or current_user.is_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only valuers can create valuations"
        )
    
    try:
        valuation = vehicle_service.create_valuation(valuation_data, current_user.id)
        return valuation
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{vehicle_id}/analyze-and-value", response_model=VehicleValuationResponse)
def analyze_and_value_vehicle(
    vehicle_id: UUID,
    include_ai_analysis: bool = Query(True),
    current_user: User = Depends(get_current_user),
    vehicle_service: VehicleValuationService = Depends(get_vehicle_service)
):
    """Perform AI-powered analysis and create valuation"""
    # Verify vehicle exists
    vehicle = vehicle_service.get_vehicle(vehicle_id)
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found"
        )
    
    # Only valuers or admins can create valuations
    if not (current_user.is_valuer or current_user.is_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only valuers can create valuations"
        )
    
    try:
        valuation = vehicle_service.analyze_and_value_vehicle(
            vehicle_id,
            current_user.id,
            include_ai_analysis
        )
        return valuation
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{vehicle_id}/valuations", response_model=VehicleValuationListResponse)
def get_vehicle_valuations(
    vehicle_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
    vehicle_service: VehicleValuationService = Depends(get_vehicle_service)
):
    """Get all valuations for a vehicle"""
    # Verify vehicle exists and user has access
    vehicle = vehicle_service.get_vehicle(vehicle_id)
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found"
        )
    
    # Check ownership or admin access
    if vehicle.owner_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    valuations = vehicle_service.get_vehicle_valuations(vehicle_id, skip, limit)
    total = len(valuations)  # Simplified count
    
    return VehicleValuationListResponse(
        valuations=valuations,
        total=total,
        page=skip // limit + 1,
        per_page=limit,
        pages=(total + limit - 1) // limit
    )


@router.get("/{vehicle_id}/latest-valuation", response_model=VehicleValuationResponse)
def get_latest_valuation(
    vehicle_id: UUID,
    current_user: User = Depends(get_current_user),
    vehicle_service: VehicleValuationService = Depends(get_vehicle_service)
):
    """Get the latest approved valuation for a vehicle"""
    # Verify vehicle exists and user has access
    vehicle = vehicle_service.get_vehicle(vehicle_id)
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found"
        )
    
    # Check ownership or admin access
    if vehicle.owner_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    valuation = vehicle_service.get_latest_valuation(vehicle_id)
    if not valuation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No approved valuation found"
        )
    
    return valuation


@router.put("/valuations/{valuation_id}", response_model=VehicleValuationResponse)
def update_valuation(
    valuation_id: UUID,
    update_data: VehicleValuationUpdate,
    current_user: User = Depends(get_current_user),
    vehicle_service: VehicleValuationService = Depends(get_vehicle_service)
):
    """Update a valuation"""
    valuation = vehicle_service.get_valuation(valuation_id)
    if not valuation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Valuation not found"
        )
    
    # Only valuer who created it or admin can update
    if valuation.valuer_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    updated_valuation = vehicle_service.update_valuation(valuation_id, update_data.dict(exclude_unset=True))
    return updated_valuation


@router.post("/valuations/{valuation_id}/approve", response_model=VehicleValuationResponse)
def approve_valuation(
    valuation_id: UUID,
    current_user: User = Depends(get_current_user),
    vehicle_service: VehicleValuationService = Depends(get_vehicle_service)
):
    """Approve a valuation and issue certificate"""
    # Only admins can approve valuations
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can approve valuations"
        )
    
    valuation = vehicle_service.get_valuation(valuation_id)
    if not valuation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Valuation not found"
        )
    
    if valuation.status != "submitted":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only submitted valuations can be approved"
        )
    
    approved_valuation = vehicle_service.approve_valuation(valuation_id, current_user.id)
    return approved_valuation


# Analytics Routes
@router.get("/valuations/statistics")
def get_valuation_statistics(
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    vehicle_service: VehicleValuationService = Depends(get_vehicle_service)
):
    """Get valuation statistics"""
    # Only admins can access statistics
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Parse dates (simplified)
    from datetime import datetime
    date_from_obj = None
    date_to_obj = None
    
    if date_from:
        try:
            date_from_obj = datetime.fromisoformat(date_from)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date_from format"
            )
    
    if date_to:
        try:
            date_to_obj = datetime.fromisoformat(date_to)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date_to format"
            )
    
    stats = vehicle_service.get_valuation_statistics(date_from_obj, date_to_obj)
    return stats


@router.get("/market-trends")
def get_market_trends(
    make: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    vehicle_service: VehicleValuationService = Depends(get_vehicle_service)
):
    """Get market trends"""
    # Only valuers and admins can access market trends
    if not (current_user.is_valuer or current_user.is_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    trends = vehicle_service.get_market_trends(make)
    return trends
