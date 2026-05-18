"""
Vehicle Data API Endpoints

API endpoints for fetching vehicle data from NHTSA vPIC API
including makes, models, years, and VIN decoding.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import logging

from app.core.database import get_db
from app.core.security import get_current_user_id
from app.services.vehicle_data_service import vehicle_data_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/vehicle-data", tags=["vehicle-data"])


@router.get("/brands", response_model=List[str])
async def get_vehicle_brands(
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Get all available vehicle brands from NHTSA API
    
    Returns a list of all vehicle makes available in the NHTSA database.
    """
    try:
        brands = await vehicle_data_service.get_all_makes()
        
        if not brands:
            raise HTTPException(
                status_code=503,
                detail="Unable to fetch vehicle brands from external API"
            )
        
        # Sort brands alphabetically
        brands.sort()
        
        logger.info(f"User {current_user_id} fetched {len(brands)} vehicle brands")
        return brands

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching vehicle brands: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while fetching vehicle brands"
        )


@router.get("/models/{brand}", response_model=List[str])
async def get_vehicle_models(
    brand: str,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Get all models for a specific vehicle brand
    
    Args:
        brand: Vehicle brand name (e.g., "toyota", "honda")
    
    Returns a list of all models available for the specified brand.
    """
    try:
        models = await vehicle_data_service.get_models_for_make(brand)
        
        if not models:
            raise HTTPException(
                status_code=404,
                detail=f"No models found for brand: {brand}"
            )
        
        logger.info(f"User {current_user_id} fetched {len(models)} models for {brand}")
        return models
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching models for {brand}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error while fetching models for {brand}"
        )


@router.get("/decode-vin/{vin}", response_model=Dict[str, Any])
async def decode_vehicle_vin(
    vin: str,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Decode a VIN to get vehicle specifications
    
    Args:
        vin: 17-character Vehicle Identification Number
    
    Returns decoded vehicle information including make, model, year, and specifications.
    """
    try:
        # Validate VIN format
        if len(vin) != 17:
            raise HTTPException(
                status_code=400,
                detail="VIN must be exactly 17 characters"
            )
        
        # Check for invalid characters
        invalid_chars = ['I', 'O', 'Q']
        if any(char in vin.upper() for char in invalid_chars):
            raise HTTPException(
                status_code=400,
                detail="VIN contains invalid characters (I, O, Q not allowed)"
            )
        
        decoded_data = await vehicle_data_service.decode_vin(vin)
        
        if not decoded_data:
            raise HTTPException(
                status_code=404,
                detail=f"Unable to decode VIN: {vin}"
            )
        
        # Extract key information for easier consumption
        key_data = {
            "vin": vin,
            "make": decoded_data.get("Make"),
            "model": decoded_data.get("Model"),
            "year": decoded_data.get("ModelYear"),
            "trim": decoded_data.get("Trim"),
            "body_type": decoded_data.get("BodyClass"),
            "engine": decoded_data.get("EngineDisplacementL"),
            "fuel_type": decoded_data.get("FuelTypePrimary"),
            "transmission": decoded_data.get("TransmissionStyle"),
            "drive_type": decoded_data.get("DriveType"),
            "manufacturer": decoded_data.get("Manufacturer"),
            "plant_country": decoded_data.get("PlantCountry"),
            "vehicle_type": decoded_data.get("VehicleType"),
            "displacement_cc": decoded_data.get("DisplacementCC"),
            "number_of_cylinders": decoded_data.get("EngineCylinders"),
            "valve_train_design": decoded_data.get("ValveTrainDesign"),
            "fuel_delivery": decoded_data.get("FuelDeliveryPrimary"),
            "abs": decoded_data.get("ABS"),
            "airbags": decoded_data.get("AirBagLocFront"),
            "daytime_running_lights": decoded_data.get("DaytimeRunningLights"),
            "traction_control": decoded_data.get("TractionControl"),
            "stability_control": decoded_data.get("StabilityControl"),
            "gps": decoded_data.get("GPS"),
            "theft_indicator": decoded_data.get("TheftIndicator"),
            "blind_spot_monitor": decoded_data.get("BlindSpotMon"),
            "lane_departure_warning": decoded_data.get("LaneDepartureWarning"),
            "forward_collision_warning": decoded_data.get("ForwardCollisionWarning"),
            "adaptive_cruise_control": decoded_data.get("AdaptiveCruiseControl"),
            "backup_camera": decoded_data.get("BackupCamera"),
            "parking_assist": decoded_data.get("ParkingAssist"),
            "keyless_start": decoded_data.get("KeylessStart"),
            "bluetooth": decoded_data.get("Bluetooth"),
            "interchange": decoded_data.get("Interchange"),
            "notes": decoded_data.get("Notes"),
            "error_code": decoded_data.get("ErrorCode"),
            "additional_error_text": decoded_data.get("AdditionalErrorText")
        }
        
        # Remove None values for cleaner response
        key_data = {k: v for k, v in key_data.items() if v is not None}
        
        logger.info(f"User {current_user_id} decoded VIN: {vin}")
        return key_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error decoding VIN {vin}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error while decoding VIN: {vin}"
        )


@router.get("/types/{brand}", response_model=List[str])
async def get_vehicle_types_for_make(
    brand: str,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Get all vehicle types for a specific brand
    
    Args:
        brand: Vehicle brand name (e.g., "toyota", "honda")
    
    Returns a list of vehicle types available for the specified brand.
    """
    try:
        types = await vehicle_data_service.get_vehicle_types_for_make(brand)
        
        if not types:
            raise HTTPException(
                status_code=404,
                detail=f"No vehicle types found for brand: {brand}"
            )
        
        logger.info(f"User {current_user_id} fetched {len(types)} vehicle types for {brand}")
        return types
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching vehicle types for {brand}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error while fetching vehicle types for {brand}"
        )


@router.get("/cache-info", response_model=Dict[str, Any])
async def get_cache_info(
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Get vehicle data cache information for monitoring
    
    Returns cache statistics and performance information.
    """
    try:
        cache_info = vehicle_data_service.get_cache_info()
        
        logger.info(f"User {current_user_id} accessed vehicle data cache info")
        return cache_info
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting cache info: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while getting cache info"
        )


@router.post("/clear-cache", response_model=Dict[str, str])
async def clear_cache(
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Clear vehicle data cache
    
    Clears all cached vehicle data to force fresh API calls.
    """
    try:
        vehicle_data_service.clear_cache()
        
        logger.info(f"User {current_user_id} cleared vehicle data cache")
        return {"message": "Vehicle data cache cleared successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while clearing cache"
        )


@router.get("/search", response_model=List[Dict[str, str]])
async def search_vehicles(
    query: str = Query(..., min_length=2, description="Search query for vehicle make or model"),
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Search for vehicles by make or model
    
    Args:
        query: Search term (minimum 2 characters)
    
    Returns a list of matching vehicles with make and model information.
    """
    try:
        query_lower = query.lower()
        
        # Get all makes and search
        all_makes = await vehicle_data_service.get_all_makes()
        matching_makes = [make for make in all_makes if query_lower in make.lower()]
        
        results = []
        
        # For each matching make, get its models
        for make in matching_makes[:10]:  # Limit to prevent too many API calls
            try:
                models = await vehicle_data_service.get_models_for_make(make)
                matching_models = [model for model in models if query_lower in model.lower()]
                
                for model in matching_models[:5]:  # Limit models per make
                    results.append({
                        "make": make,
                        "model": model,
                        "display_name": f"{make} {model}"
                    })
            except Exception as e:
                logger.warning(f"Failed to get models for {make}: {e}")
                continue
        
        # Sort by display name
        results.sort(key=lambda x: x["display_name"])
        
        logger.info(f"User {current_user_id} searched for vehicles with query: {query}")
        return results[:50]  # Limit total results
        
    except Exception as e:
        logger.error(f"Error searching vehicles: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while searching vehicles"
        )


@router.get("/validate-vin/{vin}", response_model=Dict[str, Any])
async def validate_vin(
    vin: str,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Validate VIN format and check if it exists in database
    
    Args:
        vin: 17-character Vehicle Identification Number
    
    Returns validation results and basic information if VIN is valid.
    """
    try:
        validation_result = {
            "vin": vin,
            "is_valid": False,
            "errors": [],
            "warnings": [],
            "basic_info": {}
        }
        
        # Check length
        if len(vin) != 17:
            validation_result["errors"].append("VIN must be exactly 17 characters")
        else:
            validation_result["is_valid"] = True
        
        # Check for invalid characters
        invalid_chars = ['I', 'O', 'Q']
        found_invalid = [char for char in vin.upper() if char in invalid_chars]
        if found_invalid:
            validation_result["errors"].append(f"VIN contains invalid characters: {', '.join(found_invalid)}")
            validation_result["is_valid"] = False
        
        # If valid, try to decode for basic info
        if validation_result["is_valid"]:
            try:
                decoded_data = await vehicle_data_service.decode_vin(vin)
                if decoded_data:
                    validation_result["basic_info"] = {
                        "make": decoded_data.get("Make"),
                        "model": decoded_data.get("Model"),
                        "year": decoded_data.get("ModelYear"),
                        "manufacturer": decoded_data.get("Manufacturer")
                    }
                else:
                    validation_result["warnings"].append("VIN format is valid but not found in database")
            except Exception as e:
                validation_result["warnings"].append("Unable to verify VIN with external database")
        
        logger.info(f"User {current_user_id} validated VIN: {vin}")
        return validation_result
        
    except Exception as e:
        logger.error(f"Error validating VIN {vin}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error while validating VIN: {vin}"
        )
