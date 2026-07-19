"""
Property Repository

Data access layer for property operations with PostGIS spatial queries
"""

from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, text
from app.data.repositories.base import BaseRepository
from app.data.models.property import Property


class PropertyRepository(BaseRepository[Property]):
    def __init__(self, db: Session):
        super().__init__(Property, db)
    
    def get_user_properties(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 20,
        scope_all: bool = False,
    ) -> Tuple[List[Property], int]:
        """Get properties, scoped to the owner unless scope_all (staff/
        rental_officer read access — Phase E permission matrix)."""
        query = self.db.query(Property)
        if not scope_all:
            query = query.filter(Property.user_id == user_id)
        total = query.count()
        properties = query.offset(skip).limit(limit).all()
        return properties, total

    def get_by_user_and_id(
        self,
        property_id: int,
        user_id: int,
        scope_all: bool = False,
    ) -> Optional[Property]:
        """Get property by ID, scoped to the owner unless scope_all."""
        query = self.db.query(Property).filter(Property.id == property_id)
        if not scope_all:
            query = query.filter(Property.user_id == user_id)
        return query.first()

    def create_property(self, property_data: dict) -> Property:
        """Create new property with spatial data"""
        return self.create(property_data)

    def update_property(
        self,
        property_id: int,
        user_id: int,
        update_data: dict,
        scope_all: bool = False,
    ) -> Optional[Property]:
        """Update property. Owner-scoped unless scope_all (staff)."""
        property = self.get_by_user_and_id(property_id, user_id, scope_all=scope_all)
        if property:
            return self.update(property, update_data)
        return None

    def delete_property(self, property_id: int, user_id: int, scope_all: bool = False) -> bool:
        """Delete property. Owner-scoped unless scope_all (staff)."""
        property = self.get_by_user_and_id(property_id, user_id, scope_all=scope_all)
        if property:
            self.db.delete(property)
            self.db.commit()
            return True
        return False
    
    def find_properties_within_radius(
        self,
        lat: float,
        lon: float,
        radius_km: float,
        user_id: Optional[int] = None
    ) -> List[Property]:
        """Find properties within a given radius using PostGIS"""
        # Convert radius from km to meters
        radius_meters = radius_km * 1000

        # Build query with bound parameters (never interpolate into SQL)
        query = self.db.query(Property).filter(
            text(
                "ST_DWithin(boundary, ST_SetSRID(ST_MakePoint(:lon, :lat), 4326), :radius_meters)"
            ).bindparams(lon=lon, lat=lat, radius_meters=radius_meters)
        )
        
        if user_id:
            query = query.filter(Property.user_id == user_id)
        
        return query.all()
    
    def calculate_area(self, property_id: int) -> Optional[float]:
        """Calculate property area in square meters using PostGIS"""
        property = self.get(property_id)
        if property and property.boundary:
            result = self.db.execute(
                text("SELECT ST_Area(ST_Transform(boundary, 32637)) FROM properties WHERE id = :property_id"),
                {"property_id": property_id}
            ).scalar()
            return result
        return None
    
    def get_properties_by_municipality(
        self,
        municipality: str,
        skip: int = 0,
        limit: int = 20
    ) -> Tuple[List[Property], int]:
        """Get properties by municipality"""
        query = self.db.query(Property).filter(Property.municipality == municipality)
        total = query.count()
        properties = query.offset(skip).limit(limit).all()
        return properties, total
    
    def get_property_statistics(self, user_id: Optional[int] = None) -> dict:
        """Get property statistics"""
        # ⚡ Bolt Optimization: Combine count, sum, and avg into a single database query
        # to reduce roundtrips from 4 to 2 (one for aggregates, one for group_by).
        base_query = self.db.query(Property)
        if user_id:
            base_query = base_query.filter(Property.user_id == user_id)

        aggregates = base_query.with_entities(
            func.count(Property.id),
            func.sum(Property.area_sqm),
            func.avg(Property.area_sqm)
        ).first()

        total_properties = aggregates[0] or 0
        total_area = aggregates[1] or 0
        avg_area = aggregates[2] or 0
        
        properties_by_type = base_query.with_entities(
            Property.property_type,
            func.count(Property.id)
        ).group_by(Property.property_type).all()
        
        return {
            "total_properties": total_properties,
            "total_area_sqm": float(total_area),
            "average_area_sqm": float(avg_area),
            "properties_by_type": dict(properties_by_type)
        }
