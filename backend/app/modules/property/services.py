"""
Property Service

Business logic for property operations including spatial calculations
"""

from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from app.core.exceptions import ValidationException, SpatialOperationException
from app.services.spatial_service import SpatialService
from .models import Property
from .repositories import PropertyRepository
import random
import datetime


class PropertyService:
    def __init__(self, db: Session):
        self.property_repo = PropertyRepository(db)
        self.spatial_service = SpatialService()
    
    async def create_property(self, property_data: dict, user_id: int) -> Property:
        """Create new property with boundary validation and area calculation"""
        # Generate property reference if not provided
        if not property_data.get("property_ref"):
            property_data["property_ref"] = self._generate_property_ref(property_data.get("municipality", "ADD"))
        
        # Handle coordinates - either from boundaries/coordinates field or generate from lat/lng
        coordinates = property_data.get("coordinates") or property_data.get("boundaries")
        
        # If no coordinates but lat/lng are provided, generate a small polygon
        if not coordinates and property_data.get("latitude") and property_data.get("longitude"):
            lat = property_data["latitude"]
            lng = property_data["longitude"]
            DELTA = 0.0002  # ~22 m bounding box at equator
            coordinates = [
                [lng - DELTA, lat - DELTA],
                [lng + DELTA, lat - DELTA],
                [lng + DELTA, lat + DELTA],
                [lng - DELTA, lat + DELTA],
                [lng - DELTA, lat - DELTA],  # closed ring
            ]
        
        if not coordinates:
            raise ValidationException("Coordinates are required (either polygon boundaries or latitude/longitude)")
        
        if not self.spatial_service.validate_polygon(coordinates):
            raise ValidationException("Invalid polygon: must have minimum 3 vertices and be closed")
        
        # Calculate area
        area_sqm = self.spatial_service.calculate_area(coordinates)
        if area_sqm <= 0:
            raise SpatialOperationException("Calculated area is invalid")
        
        # Create boundary geometry for PostGIS
        boundary_wkt = self.spatial_service.create_wkt_polygon(coordinates)
        
        # Prepare property data
        property_data = {
            **property_data,
            "user_id": user_id,
            "area_sqm": area_sqm,
            "boundary": boundary_wkt
        }
        
        # Remove coordinates and boundaries as they're now stored in boundary
        property_data.pop("coordinates", None)
        property_data.pop("boundaries", None)
        
        return self.property_repo.create_property(property_data)
    
    def _generate_property_ref(self, municipality: str) -> str:
        """Generate unique property reference number"""
        # Get municipality code (first 3 letters, uppercase)
        muni_code = (municipality[:3] or "ADD").upper()
        
        # Get current year
        year = datetime.datetime.now().year
        
        # Generate random 4-digit number
        random_num = random.randint(1000, 9999)
        
        return f"{muni_code}-{year}-{random_num}"
    
    async def get_property_by_id(self, property_id: int, user_id: int) -> Optional[Property]:
        """Get property by ID (user must be owner)"""
        return self.property_repo.get_by_user_and_id(property_id, user_id)
    
    async def get_user_properties(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 20
    ) -> Tuple[List[Property], int]:
        """Get user's properties with pagination"""
        return self.property_repo.get_user_properties(user_id, skip, limit)
    
    async def update_property(
        self,
        property_id: int,
        user_id: int,
        update_data: dict
    ) -> Optional[Property]:
        """Update property information"""
        # If coordinates are provided, recalculate area and boundary
        if "coordinates" in update_data:
            coordinates = update_data["coordinates"]
            
            if not self.spatial_service.validate_polygon(coordinates):
                raise ValidationException("Invalid polygon: must have minimum 3 vertices and be closed")
            
            # Recalculate area
            area_sqm = self.spatial_service.calculate_area(coordinates)
            if area_sqm <= 0:
                raise SpatialOperationException("Calculated area is invalid")
            
            # Update boundary geometry
            update_data["area_sqm"] = area_sqm
            update_data["boundary"] = self.spatial_service.create_wkt_polygon(coordinates)
            
            # Remove coordinates as they're now stored in boundary
            del update_data["coordinates"]
        
        return self.property_repo.update_property(property_id, user_id, update_data)
    
    async def delete_property(self, property_id: int, user_id: int) -> bool:
        """Delete property (user must be owner)"""
        return self.property_repo.delete_property(property_id, user_id)
    
    async def find_nearby_properties(
        self,
        lat: float,
        lon: float,
        radius_km: float,
        user_id: Optional[int] = None
    ) -> List[Property]:
        """Find properties within radius"""
        return self.property_repo.find_properties_within_radius(lat, lon, radius_km, user_id)
    
    async def get_property_statistics(self, user_id: Optional[int] = None) -> dict:
        """Get property statistics"""
        return self.property_repo.get_property_statistics(user_id)
