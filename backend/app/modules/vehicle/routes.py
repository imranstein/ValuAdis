"""
Vehicles API Routes

Single owner of the /api/v1/vehicles contract after the v2 consolidation.

The vehicle stack previously existed twice:
- flat: app/api/v1/endpoints/vehicles.py + app/services/vehicle_valuation_service.py
  + app/schemas/vehicle*.py (the mounted, live contract)
- module: app/modules/vehicle/{routes,services,repositories,schemas,ai} (an
  unmounted UUID-based prototype whose fields did not match the real models)

The live flat implementation moved here verbatim; the prototype was deleted.
NOTE: /statistics/summary must stay declared before /{vehicle_id} (FastAPI
matches routes in declaration order).
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging

from app.core.database import get_db
from app.core.security import get_current_user_id
from .models import Vehicle, VehicleValuation, VehicleValuationStatus
from .services import vehicle_valuation_service
from .schemas import VehicleCreate, VehicleUpdate, VehicleResponse
from .valuation_schemas import VehicleValuationCreate, VehicleValuationResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/vehicles", tags=["vehicles"])


@router.post("/", response_model=VehicleResponse)
async def create_vehicle(
    vehicle_data: VehicleCreate,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Create a new vehicle record
    
    Args:
        vehicle_data: Vehicle creation data
        
    Returns the created vehicle record.
    """
    try:
        # Check if VIN already exists
        existing_vin = db.query(Vehicle).filter(Vehicle.vin == vehicle_data.vin).first()
        if existing_vin:
            raise HTTPException(
                status_code=400,
                detail="Vehicle with this VIN already exists"
            )
        
        # Check if plate number already exists
        existing_plate = db.query(Vehicle).filter(Vehicle.plate_number == vehicle_data.plate_number).first()
        if existing_plate:
            raise HTTPException(
                status_code=400,
                detail="Vehicle with this plate number already exists"
            )
        
        # Create vehicle object
        vehicle = Vehicle(
            user_id=current_user_id,
            **vehicle_data.model_dump()
        )

        db.add(vehicle)
        db.commit()
        db.refresh(vehicle)

        logger.info(f"User {current_user_id} created vehicle: {vehicle.vin}")
        return vehicle
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating vehicle: {e}")
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Internal server error while creating vehicle"
        )


@router.get("/", response_model=List[VehicleResponse])
async def get_user_vehicles(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    make: Optional[str] = Query(None, description="Filter by vehicle make"),
    model: Optional[str] = Query(None, description="Filter by vehicle model"),
    year: Optional[int] = Query(None, description="Filter by vehicle year"),
    region: Optional[str] = Query(None, description="Filter by region"),
    status: Optional[str] = Query(None, description="Filter by valuation status"),
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Get user's vehicles with optional filtering
    
    Returns a list of vehicles belonging to the current user with optional filters.
    """
    try:
        query = db.query(Vehicle).filter(Vehicle.user_id == current_user_id)

        # Apply filters
        if make:
            query = query.filter(Vehicle.make.ilike(f"%{make}%"))
        if model:
            query = query.filter(Vehicle.model.ilike(f"%{model}%"))
        if year:
            query = query.filter(Vehicle.year == year)
        if region:
            query = query.filter(Vehicle.region.ilike(f"%{region}%"))
        if status:
            # Join with valuations to filter by status
            query = query.join(VehicleValuation).filter(VehicleValuation.status == status)
        
        # Apply pagination
        vehicles = query.offset(skip).limit(limit).all()
        
        logger.info(f"User {current_user_id} retrieved {len(vehicles)} vehicles")
        return vehicles
        
    except Exception as e:
        logger.error(f"Error retrieving vehicles: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while retrieving vehicles"
        )


@router.get("/statistics/summary")
async def get_vehicle_statistics(
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Get vehicle statistics summary for the current user

    Returns statistics including total vehicles, total value, and breakdowns.
    """
    try:
        vehicles = db.query(Vehicle).filter(Vehicle.user_id == current_user_id).all()
        valuations = db.query(VehicleValuation).filter(
            VehicleValuation.user_id == current_user_id
        ).all()

        total_vehicles = len(vehicles)
        total_market_value = sum(v.market_value for v in valuations)
        total_taxable_value = sum(v.taxable_value for v in valuations)

        make_breakdown = {}
        for vehicle in vehicles:
            make = vehicle.make
            make_breakdown[make] = make_breakdown.get(make, 0) + 1

        year_breakdown = {}
        for vehicle in vehicles:
            year = vehicle.year
            year_breakdown[year] = year_breakdown.get(year, 0) + 1

        region_breakdown = {}
        for vehicle in vehicles:
            region = vehicle.region or "Unknown"
            region_breakdown[region] = region_breakdown.get(region, 0) + 1

        status_breakdown = {}
        for valuation in valuations:
            status = valuation.status.value
            status_breakdown[status] = status_breakdown.get(status, 0) + 1

        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_valuations = len([
            v for v in valuations if v.created_at > thirty_days_ago
        ])

        logger.info(f"User {current_user_id} retrieved vehicle statistics")
        return {
            "total_vehicles": total_vehicles,
            "total_valuations": len(valuations),
            "total_market_value": total_market_value,
            "total_taxable_value": total_taxable_value,
            "average_vehicle_value": total_market_value / len(valuations) if valuations else 0,
            "recent_valuations": recent_valuations,
            "make_breakdown": make_breakdown,
            "year_breakdown": year_breakdown,
            "region_breakdown": region_breakdown,
            "status_breakdown": status_breakdown
        }

    except Exception as e:
        logger.error(f"Error retrieving vehicle statistics: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while retrieving vehicle statistics"
        )


@router.get("/{vehicle_id}", response_model=VehicleResponse)
async def get_vehicle(
    vehicle_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Get a specific vehicle by ID
    
    Args:
        vehicle_id: Vehicle ID
        
    Returns the vehicle record if found and belongs to current user.
    """
    try:
        vehicle = db.query(Vehicle).filter(
            and_(Vehicle.id == vehicle_id, Vehicle.user_id == current_user_id)
        ).first()

        if not vehicle:
            raise HTTPException(
                status_code=404,
                detail="Vehicle not found"
            )

        logger.info(f"User {current_user_id} retrieved vehicle: {vehicle_id}")
        return vehicle
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving vehicle {vehicle_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error while retrieving vehicle {vehicle_id}"
        )


@router.put("/{vehicle_id}", response_model=VehicleResponse)
async def update_vehicle(
    vehicle_id: int,
    vehicle_data: VehicleUpdate,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Update a vehicle record
    
    Args:
        vehicle_id: Vehicle ID
        vehicle_data: Updated vehicle data
        
    Returns the updated vehicle record.
    """
    try:
        vehicle = db.query(Vehicle).filter(
            and_(Vehicle.id == vehicle_id, Vehicle.user_id == current_user_id)
        ).first()

        if not vehicle:
            raise HTTPException(
                status_code=404,
                detail="Vehicle not found"
            )

        # Check if VIN is being changed and if it already exists
        if vehicle_data.vin and vehicle_data.vin != vehicle.vin:
            existing_vin = db.query(Vehicle).filter(
                and_(Vehicle.vin == vehicle_data.vin, Vehicle.id != vehicle_id)
            ).first()
            if existing_vin:
                raise HTTPException(
                    status_code=400,
                    detail="Vehicle with this VIN already exists"
                )
        
        # Check if plate number is being changed and if it already exists
        if vehicle_data.plate_number and vehicle_data.plate_number != vehicle.plate_number:
            existing_plate = db.query(Vehicle).filter(
                and_(Vehicle.plate_number == vehicle_data.plate_number, Vehicle.id != vehicle_id)
            ).first()
            if existing_plate:
                raise HTTPException(
                    status_code=400,
                    detail="Vehicle with this plate number already exists"
                )
        
        # Update vehicle with provided data
        update_data = vehicle_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(vehicle, field, value)
        
        db.commit()
        db.refresh(vehicle)
        
        logger.info(f"User {current_user_id} updated vehicle: {vehicle_id}")
        return vehicle
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating vehicle {vehicle_id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error while updating vehicle {vehicle_id}"
        )


@router.delete("/{vehicle_id}")
async def delete_vehicle(
    vehicle_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Delete a vehicle record
    
    Args:
        vehicle_id: Vehicle ID
        
    Returns success message if vehicle is deleted.
    """
    try:
        vehicle = db.query(Vehicle).filter(
            and_(Vehicle.id == vehicle_id, Vehicle.user_id == current_user_id)
        ).first()

        if not vehicle:
            raise HTTPException(
                status_code=404,
                detail="Vehicle not found"
            )

        db.delete(vehicle)
        db.commit()

        logger.info(f"User {current_user_id} deleted vehicle: {vehicle_id}")
        return {"message": "Vehicle deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting vehicle {vehicle_id}: {e}")
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error while deleting vehicle {vehicle_id}"
        )


@router.post("/{vehicle_id}/valuation", response_model=VehicleValuationResponse)
async def create_vehicle_valuation(
    vehicle_id: int,
    valuation_data: Optional[VehicleValuationCreate] = None,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Create a vehicle valuation
    
    Args:
        vehicle_id: Vehicle ID
        valuation_data: Optional valuation data (will auto-calculate if not provided)
        
    Returns the created vehicle valuation.
    """
    try:
        vehicle = db.query(Vehicle).filter(
            and_(Vehicle.id == vehicle_id, Vehicle.user_id == current_user_id)
        ).first()

        if not vehicle:
            raise HTTPException(
                status_code=404,
                detail="Vehicle not found"
            )

        # Check if vehicle can be valued
        if not vehicle.can_be_valued():
            raise HTTPException(
                status_code=400,
                detail="Vehicle cannot be valued - missing required information"
            )
        
        # Calculate valuation using service
        valuation_result = vehicle_valuation_service.calculate_vehicle_valuation(vehicle)
        
        # Create valuation record
        valuation = VehicleValuation(
            vehicle_id=vehicle_id,
            user_id=current_user_id,
            vehicle_make=vehicle.make,
            vehicle_model=vehicle.model,
            vehicle_year=vehicle.year,
            vehicle_vin=vehicle.vin,
            vehicle_plate=vehicle.plate_number,
            vehicle_mileage=vehicle.mileage,
            vehicle_region=vehicle.region,
            base_value=valuation_result["base_value"],
            market_value=valuation_result["market_value"],
            taxable_value=valuation_result["taxable_value"],
            condition_factor=valuation_result["condition_factor"],
            regional_multiplier=valuation_result["ethiopian_factors"]["regional_multiplier"],
            import_year_adjustment=valuation_result["ethiopian_factors"]["import_year_adjustment"],
            customs_duty_factor=valuation_result["ethiopian_factors"]["customs_duty_factor"],
            make_reliability=valuation_result["ethiopian_factors"]["make_reliability"],
            fuel_type_adjustment=valuation_result["ethiopian_factors"]["fuel_type_adjustment"],
            body_type_demand=valuation_result["ethiopian_factors"]["body_type_demand"],
            ethiopian_factors=valuation_result["ethiopian_factors"],
            market_position=valuation_result["market_position"],
            confidence_score=valuation_result["confidence_score"],
            condition_rating=valuation_result["condition_analysis"]["condition_rating"],
            age_depreciation=valuation_result["condition_analysis"]["age_depreciation"],
            mileage_depreciation=valuation_result["condition_analysis"].get("mileage_depreciation", 0),
            recommendations=valuation_result.get("recommendations", []),
            data_sources=["NHTSA vPIC API", "Ethiopian Market Data"],
            valuation_method="automated"
        )
        
        # Set expiration date (1 year from now)
        valuation.set_expiration_date(365)
        
        db.add(valuation)
        db.commit()
        db.refresh(valuation)
        
        logger.info(f"User {current_user_id} created valuation for vehicle {vehicle_id}: ETB {valuation.market_value}")
        return valuation
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating vehicle valuation: {e}")
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Internal server error while creating vehicle valuation"
        )


@router.get("/{vehicle_id}/valuations", response_model=List[VehicleValuationResponse])
async def get_vehicle_valuations(
    vehicle_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Get all valuations for a specific vehicle
    
    Args:
        vehicle_id: Vehicle ID
        
    Returns a list of valuations for the specified vehicle.
    """
    try:
        # Verify vehicle belongs to user
        vehicle = db.query(Vehicle).filter(
            and_(Vehicle.id == vehicle_id, Vehicle.user_id == current_user_id)
        ).first()

        if not vehicle:
            raise HTTPException(
                status_code=404,
                detail="Vehicle not found"
            )

        valuations = db.query(VehicleValuation).filter(
            VehicleValuation.vehicle_id == vehicle_id
        ).order_by(VehicleValuation.created_at.desc()).all()
        
        logger.info(f"User {current_user_id} retrieved {len(valuations)} valuations for vehicle {vehicle_id}")
        return valuations
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving vehicle valuations: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while retrieving vehicle valuations"
        )


@router.get("/{vehicle_id}/latest-valuation", response_model=VehicleValuationResponse)
async def get_latest_vehicle_valuation(
    vehicle_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Get the latest valuation for a specific vehicle
    
    Args:
        vehicle_id: Vehicle ID
        
    Returns the most recent valuation for the specified vehicle.
    """
    try:
        # Verify vehicle belongs to user
        vehicle = db.query(Vehicle).filter(
            and_(Vehicle.id == vehicle_id, Vehicle.user_id == current_user_id)
        ).first()

        if not vehicle:
            raise HTTPException(
                status_code=404,
                detail="Vehicle not found"
            )

        valuation = db.query(VehicleValuation).filter(
            VehicleValuation.vehicle_id == vehicle_id
        ).order_by(VehicleValuation.created_at.desc()).first()
        
        if not valuation:
            raise HTTPException(
                status_code=404,
                detail="No valuation found for this vehicle"
            )
        
        logger.info(f"User {current_user_id} retrieved latest valuation for vehicle {vehicle_id}")
        return valuation
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving latest vehicle valuation: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while retrieving latest vehicle valuation"
        )

