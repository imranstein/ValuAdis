"""
Vehicle Valuation Repositories

Data access layer for vehicles and vehicle valuations.
"""

from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc

from app.core.database import get_db
from .models import Vehicle, VehicleValuation


class VehicleRepository:
    """Repository for vehicle data operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, vehicle_data: Dict[str, Any]) -> Vehicle:
        """Create a new vehicle record"""
        vehicle = Vehicle(**vehicle_data)
        self.db.add(vehicle)
        self.db.commit()
        self.db.refresh(vehicle)
        return vehicle
    
    def get_by_id(self, vehicle_id: UUID) -> Optional[Vehicle]:
        """Get vehicle by ID"""
        return self.db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    
    def get_by_vin(self, vin: str) -> Optional[Vehicle]:
        """Get vehicle by VIN"""
        return self.db.query(Vehicle).filter(Vehicle.vin == vin).first()
    
    def get_by_plate(self, plate_number: str) -> Optional[Vehicle]:
        """Get vehicle by plate number"""
        return self.db.query(Vehicle).filter(Vehicle.plate_number == plate_number).first()
    
    def get_owner_vehicles(self, owner_id: UUID, skip: int = 0, limit: int = 100) -> List[Vehicle]:
        """Get all vehicles for a specific owner"""
        return (
            self.db.query(Vehicle)
            .filter(Vehicle.owner_id == owner_id)
            .filter(Vehicle.is_active == True)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def search_vehicles(
        self,
        query: Optional[str] = None,
        make: Optional[str] = None,
        model: Optional[str] = None,
        year_min: Optional[int] = None,
        year_max: Optional[int] = None,
        region: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Vehicle]:
        """Search vehicles with filters"""
        q = self.db.query(Vehicle).filter(Vehicle.is_active == True)
        
        if query:
            search_filter = or_(
                Vehicle.make.ilike(f"%{query}%"),
                Vehicle.model.ilike(f"%{query}%"),
                Vehicle.plate_number.ilike(f"%{query}%"),
                Vehicle.vin.ilike(f"%{query}%")
            )
            q = q.filter(search_filter)
        
        if make:
            q = q.filter(Vehicle.make.ilike(f"%{make}%"))
        
        if model:
            q = q.filter(Vehicle.model.ilike(f"%{model}%"))
        
        if year_min:
            q = q.filter(Vehicle.year >= year_min)
        
        if year_max:
            q = q.filter(Vehicle.year <= year_max)
        
        if region:
            q = q.filter(Vehicle.region.ilike(f"%{region}%"))
        
        return q.offset(skip).limit(limit).all()
    
    def update(self, vehicle_id: UUID, update_data: Dict[str, Any]) -> Optional[Vehicle]:
        """Update vehicle information"""
        vehicle = self.get_by_id(vehicle_id)
        if vehicle:
            for key, value in update_data.items():
                setattr(vehicle, key, value)
            self.db.commit()
            self.db.refresh(vehicle)
        return vehicle
    
    def delete(self, vehicle_id: UUID) -> bool:
        """Soft delete vehicle (set is_active=False)"""
        vehicle = self.get_by_id(vehicle_id)
        if vehicle:
            vehicle.is_active = False
            self.db.commit()
            return True
        return False
    
    def count_owner_vehicles(self, owner_id: UUID) -> int:
        """Count vehicles for a specific owner"""
        return (
            self.db.query(Vehicle)
            .filter(Vehicle.owner_id == owner_id)
            .filter(Vehicle.is_active == True)
            .count()
        )
    
    def get_similar_vehicles(
        self,
        make: str,
        model: str,
        year: int,
        region: Optional[str] = None,
        limit: int = 10
    ) -> List[Vehicle]:
        """Get similar vehicles for market comparison"""
        q = self.db.query(Vehicle).filter(
            and_(
                Vehicle.make.ilike(f"%{make}%"),
                Vehicle.model.ilike(f"%{model}%"),
                Vehicle.year.between(year - 3, year + 3),
                Vehicle.is_active == True
            )
        )
        
        if region:
            q = q.filter(Vehicle.region.ilike(f"%{region}%"))
        
        return q.limit(limit).all()


class VehicleValuationRepository:
    """Repository for vehicle valuation data operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, valuation_data: Dict[str, Any]) -> VehicleValuation:
        """Create a new vehicle valuation"""
        valuation = VehicleValuation(**valuation_data)
        self.db.add(valuation)
        self.db.commit()
        self.db.refresh(valuation)
        return valuation
    
    def get_by_id(self, valuation_id: UUID) -> Optional[VehicleValuation]:
        """Get valuation by ID"""
        return (
            self.db.query(VehicleValuation)
            .filter(VehicleValuation.id == valuation_id)
            .first()
        )
    
    def get_vehicle_valuations(
        self,
        vehicle_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[VehicleValuation]:
        """Get all valuations for a specific vehicle"""
        return (
            self.db.query(VehicleValuation)
            .filter(VehicleValuation.vehicle_id == vehicle_id)
            .order_by(desc(VehicleValuation.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_valuer_valuations(
        self,
        valuer_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[VehicleValuation]:
        """Get all valuations by a specific valuer"""
        return (
            self.db.query(VehicleValuation)
            .filter(VehicleValuation.valuer_id == valuer_id)
            .order_by(desc(VehicleValuation.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def search_valuations(
        self,
        status: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        value_min: Optional[float] = None,
        value_max: Optional[float] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[VehicleValuation]:
        """Search valuations with filters"""
        q = self.db.query(VehicleValuation)
        
        if status:
            q = q.filter(VehicleValuation.status == status)
        
        if date_from:
            q = q.filter(VehicleValuation.valuation_date >= date_from)
        
        if date_to:
            q = q.filter(VehicleValuation.valuation_date <= date_to)
        
        if value_min:
            q = q.filter(VehicleValuation.market_value >= value_min)
        
        if value_max:
            q = q.filter(VehicleValuation.market_value <= value_max)
        
        return q.order_by(desc(VehicleValuation.created_at)).offset(skip).limit(limit).all()
    
    def update(self, valuation_id: UUID, update_data: Dict[str, Any]) -> Optional[VehicleValuation]:
        """Update valuation information"""
        valuation = self.get_by_id(valuation_id)
        if valuation:
            for key, value in update_data.items():
                setattr(valuation, key, value)
            self.db.commit()
            self.db.refresh(valuation)
        return valuation
    
    def approve_valuation(
        self,
        valuation_id: UUID,
        approved_by: UUID,
        certificate_number: str
    ) -> Optional[VehicleValuation]:
        """Approve a valuation and issue certificate"""
        valuation = self.get_by_id(valuation_id)
        if valuation:
            valuation.status = "approved"
            valuation.approved_by = approved_by
            valuation.approved_at = datetime.utcnow()
            valuation.certificate_number = certificate_number
            valuation.certificate_issued_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(valuation)
        return valuation
    
    def get_latest_valuation(self, vehicle_id: UUID) -> Optional[VehicleValuation]:
        """Get the latest valuation for a vehicle"""
        return (
            self.db.query(VehicleValuation)
            .filter(VehicleValuation.vehicle_id == vehicle_id)
            .filter(VehicleValuation.status == "approved")
            .order_by(desc(VehicleValuation.created_at))
            .first()
        )
    
    def get_market_data(
        self,
        make: str,
        model: str,
        year_range: tuple = (None, None),
        region: Optional[str] = None,
        limit: int = 50
    ) -> List[VehicleValuation]:
        """Get market data for similar vehicles"""
        q = (
            self.db.query(VehicleValuation)
            .join(Vehicle)
            .filter(
                and_(
                    Vehicle.make.ilike(f"%{make}%"),
                    Vehicle.model.ilike(f"%{model}%"),
                    VehicleValuation.status == "approved"
                )
            )
        )
        
        if year_range[0]:
            q = q.filter(Vehicle.year >= year_range[0])
        
        if year_range[1]:
            q = q.filter(Vehicle.year <= year_range[1])
        
        if region:
            q = q.filter(Vehicle.region.ilike(f"%{region}%"))
        
        return q.limit(limit).all()
