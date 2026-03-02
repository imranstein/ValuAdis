"""
Properties Endpoints

Property CRUD operations for ValuAdis
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.security import get_current_user_id
from app.schemas.property import (
    PropertyCreate,
    PropertyUpdate,
    PropertyResponse,
    PropertyListResponse
)
from app.services.property_service import PropertyService

router = APIRouter()


@router.post("", response_model=PropertyResponse, status_code=201)
async def create_property(
    property_data: PropertyCreate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """Create new property with GPS boundary"""
    property_service = PropertyService(db)
    
    try:
        property = await property_service.create_property(
            property_data.dict(),
            user_id=current_user_id
        )
        return PropertyResponse(success=True, data=property.to_dict())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=PropertyListResponse)
async def get_properties(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """Get user's properties with pagination"""
    property_service = PropertyService(db)
    
    properties, total = await property_service.get_user_properties(
        user_id=current_user_id,
        skip=skip,
        limit=limit
    )
    
    return PropertyListResponse(
        success=True,
        data=[p.to_dict() for p in properties],
        total=total,
        skip=skip,
        limit=limit
    )


@router.get("/{property_id}", response_model=PropertyResponse)
async def get_property(
    property_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """Get specific property by ID"""
    property_service = PropertyService(db)
    
    property = await property_service.get_property_by_id(
        property_id=property_id,
        user_id=current_user_id
    )
    
    if not property:
        raise HTTPException(
            status_code=404,
            detail="Property not found"
        )
    
    return PropertyResponse(success=True, data=property.to_dict())


@router.put("/{property_id}", response_model=PropertyResponse)
async def update_property(
    property_id: int,
    property_data: PropertyUpdate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """Update property information"""
    property_service = PropertyService(db)
    
    try:
        property = await property_service.update_property(
            property_id=property_id,
            user_id=current_user_id,
            update_data=property_data.dict(exclude_unset=True)
        )
        
        if not property:
            raise HTTPException(
                status_code=404,
                detail="Property not found"
            )
        
        return PropertyResponse(success=True, data=property.to_dict())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{property_id}")
async def delete_property(
    property_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """Delete property"""
    property_service = PropertyService(db)
    
    success = await property_service.delete_property(
        property_id=property_id,
        user_id=current_user_id
    )
    
    if not success:
        raise HTTPException(
            status_code=404,
            detail="Property not found"
        )
    
    return {"success": True, "message": "Property deleted successfully"}
