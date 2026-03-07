"""
Property Service

Business logic for property operations including spatial calculations
"""

from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from geoalchemy2 import WKTElement
from app.core.exceptions import ValidationException, SpatialOperationException
from app.data.repositories.property_repository import PropertyRepository
from app.services.spatial_service import SpatialService
from app.data.models.property import Property


class PropertyService:
    def __init__(self, db: Session):
        self.property_repo = PropertyRepository(db)
        self.spatial_service = SpatialService()
    
    async def create_property(self, property_data: dict, user_id: int) -> Property:
        """Create new property with boundary validation and area calculation"""
        # Validate coordinates
        coordinates = property_data.get("coordinates")
        if not coordinates:
            raise ValidationException("Coordinates are required")
        
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
        
        # Remove coordinates as they're now stored in boundary
        property_data.pop("coordinates", None)
        
        return self.property_repo.create_property(property_data)
    
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

    async def bulk_import(
        self, rows: List[dict], user_id: int
    ) -> dict:
        """
        Bulk import properties from CSV/JSON rows.
        Each row must have: address, municipality, property_type, area_sqm.
        Optional: latitude, longitude, parcel_number, condition, etc.
        """
        created = []
        errors = []
        for i, row in enumerate(rows):
            try:
                area_sqm = float(row.get("area_sqm", row.get("area_sqm_sqm", 0)) or 0)
                if area_sqm <= 0:
                    errors.append({"row": i + 1, "error": "area_sqm must be positive"})
                    continue
                address = str(row.get("address", "") or "").strip()
                municipality = str(row.get("municipality", "") or "").strip()
                property_type = str(row.get("property_type", row.get("propertyType", "residential")) or "residential").strip()
                if not address or not municipality:
                    errors.append({"row": i + 1, "error": "address and municipality required"})
                    continue

                coords = row.get("coordinates")
                lat = row.get("latitude")
                lon = row.get("longitude")
                boundary_wkt = None
                if coords and isinstance(coords, (list, tuple)) and len(coords) >= 3:
                    if self.spatial_service.validate_polygon(coords):
                        boundary_wkt = self.spatial_service.create_wkt_polygon(coords)
                        area_sqm = self.spatial_service.calculate_area(coords)
                elif lat is not None and lon is not None:
                    try:
                        lat_f, lon_f = float(lat), float(lon)
                        boundary_wkt = self.spatial_service.create_wkt_polygon(
                            [[lon_f, lat_f], [lon_f + 0.0001, lat_f], [lon_f + 0.0001, lat_f + 0.0001], [lon_f, lat_f + 0.0001], [lon_f, lat_f]]
                        )
                    except (TypeError, ValueError):
                        pass

                boundary_geom = WKTElement(boundary_wkt, srid=4326) if boundary_wkt else None
                data = {
                    "user_id": user_id,
                    "address": address,
                    "municipality": municipality,
                    "property_type": property_type,
                    "area_sqm": area_sqm,
                    "latitude": float(lat) if lat is not None else None,
                    "longitude": float(lon) if lon is not None else None,
                    "boundary": boundary_geom,
                    "parcel_number": str(row.get("parcel_number", "") or "").strip() or None,
                    "condition": str(row.get("condition", "") or "").strip() or None,
                    "status": "active",
                }
                p = self.property_repo.create_property(data)
                created.append({"id": p.id, "address": p.address})
            except Exception as e:
                errors.append({"row": i + 1, "error": str(e)})
        return {"created": len(created), "errors": errors, "properties": created}
    
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
