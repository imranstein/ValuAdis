"""
Vehicle Valuation Services

Business logic for vehicle valuation operations including AI-powered analysis.
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from uuid import UUID
import json
import logging

from sqlalchemy.orm import Session

from .models import Vehicle, VehicleValuation
from .repositories import VehicleRepository, VehicleValuationRepository
from .schemas import VehicleCreate, VehicleUpdate, VehicleValuationCreate
from .ai.vehicle_analyzer import VehicleAnalyzer
from .ai.market_comparator import MarketComparator
from .ai.valuation_calculator import ValuationCalculator

logger = logging.getLogger(__name__)


class VehicleValuationService:
    """Service for vehicle valuation business logic"""
    
    def __init__(self, db: Session):
        self.db = db
        self.vehicle_repo = VehicleRepository(db)
        self.valuation_repo = VehicleValuationRepository(db)
        self.analyzer = VehicleAnalyzer()
        self.comparator = MarketComparator()
        self.calculator = ValuationCalculator()
    
    # Vehicle Management
    def create_vehicle(self, vehicle_data: VehicleCreate, owner_id: UUID) -> Vehicle:
        """Create a new vehicle record"""
        # Check for duplicate VIN or plate number
        existing_vin = self.vehicle_repo.get_by_vin(vehicle_data.vin)
        if existing_vin:
            raise ValueError(f"Vehicle with VIN {vehicle_data.vin} already exists")
        
        existing_plate = self.vehicle_repo.get_by_plate(vehicle_data.plate_number)
        if existing_plate:
            raise ValueError(f"Vehicle with plate {vehicle_data.plate_number} already exists")
        
        # Create vehicle
        vehicle_dict = vehicle_data.model_dump()
        vehicle_dict["owner_id"] = owner_id
        
        vehicle = self.vehicle_repo.create(vehicle_dict)
        logger.info(f"Created vehicle: {vehicle.id}")
        
        return vehicle
    
    def get_vehicle(self, vehicle_id: UUID) -> Optional[Vehicle]:
        """Get vehicle by ID"""
        return self.vehicle_repo.get_by_id(vehicle_id)
    
    def update_vehicle(self, vehicle_id: UUID, update_data: VehicleUpdate) -> Optional[Vehicle]:
        """Update vehicle information"""
        update_values = update_data.model_dump(exclude_unset=True)

        # Check if VIN or plate is being changed to an existing one
        if "vin" in update_values:
            existing = self.vehicle_repo.get_by_vin(update_values["vin"])
            if existing and existing.id != vehicle_id:
                raise ValueError(f"Vehicle with VIN {update_values['vin']} already exists")
        
        if "plate_number" in update_values:
            existing = self.vehicle_repo.get_by_plate(update_values["plate_number"])
            if existing and existing.id != vehicle_id:
                raise ValueError(f"Vehicle with plate {update_values['plate_number']} already exists")
        
        return self.vehicle_repo.update(vehicle_id, update_values)
    
    def delete_vehicle(self, vehicle_id: UUID) -> bool:
        """Delete (soft delete) a vehicle"""
        return self.vehicle_repo.delete(vehicle_id)
    
    def search_vehicles(self, **filters) -> List[Vehicle]:
        """Search vehicles with filters"""
        return self.vehicle_repo.search_vehicles(**filters)
    
    def get_owner_vehicles(self, owner_id: UUID, skip: int = 0, limit: int = 100) -> List[Vehicle]:
        """Get all vehicles for an owner"""
        return self.vehicle_repo.get_owner_vehicles(owner_id, skip, limit)
    
    # Vehicle Valuation
    def create_valuation(
        self,
        valuation_data: VehicleValuationCreate,
        valuer_id: UUID
    ) -> VehicleValuation:
        """Create a new vehicle valuation"""
        # Verify vehicle exists
        vehicle = self.vehicle_repo.get_by_id(valuation_data.vehicle_id)
        if not vehicle:
            raise ValueError(f"Vehicle {valuation_data.vehicle_id} not found")
        
        # Create valuation
        valuation_dict = valuation_data.model_dump()
        valuation_dict["valuer_id"] = valuer_id
        valuation_dict["valuation_date"] = datetime.utcnow()
        
        # Calculate taxable value (25% of market value)
        valuation_dict["taxable_value"] = valuation_dict["market_value"] * 0.25
        
        valuation = self.valuation_repo.create(valuation_dict)
        logger.info(f"Created vehicle valuation: {valuation.id}")
        
        return valuation
    
    def analyze_and_value_vehicle(
        self,
        vehicle_id: UUID,
        valuer_id: UUID,
        include_ai_analysis: bool = True
    ) -> VehicleValuation:
        """Perform AI-powered analysis and create valuation"""
        vehicle = self.vehicle_repo.get_by_id(vehicle_id)
        if not vehicle:
            raise ValueError(f"Vehicle {vehicle_id} not found")
        
        # Get similar vehicles for market comparison
        similar_vehicles = self.vehicle_repo.get_similar_vehicles(
            vehicle.make,
            vehicle.model,
            vehicle.year,
            vehicle.region
        )
        
        # Get market data
        market_data = self.valuation_repo.get_market_data(
            vehicle.make,
            vehicle.model,
            (vehicle.year - 3, vehicle.year + 3),
            vehicle.region
        )
        
        # AI Analysis
        ai_results = {}
        if include_ai_analysis:
            try:
                # Analyze vehicle condition and market position
                ai_results = self.analyzer.analyze_vehicle(vehicle, similar_vehicles, market_data)
                
                # Get market comparison data
                comparison_data = self.comparator.compare_vehicle(vehicle, similar_vehicles)
                
                # Calculate valuation using AI insights
                valuation_calculation = self.calculator.calculate_value(
                    vehicle,
                    similar_vehicles,
                    market_data,
                    ai_results
                )
                
                # Merge AI results
                ai_results.update({
                    "comparison_data": comparison_data,
                    "calculation": valuation_calculation
                })
                
            except Exception as e:
                logger.error(f"AI analysis failed for vehicle {vehicle_id}: {e}")
                # Fallback to basic calculation
                ai_results = self._basic_valuation_calculation(vehicle, similar_vehicles)
            if "market_value" not in ai_results:
                ai_results = self._basic_valuation_calculation(vehicle, similar_vehicles)
        else:
            ai_results = self._basic_valuation_calculation(vehicle, similar_vehicles)
        
        # Create valuation with AI results
        valuation_data = VehicleValuationCreate(
            vehicle_id=vehicle_id,
            market_value=ai_results["market_value"],
            valuation_method=ai_results["method"],
            depreciation_rate=ai_results.get("depreciation_rate", 0.0),
            condition_factor=ai_results.get("condition_factor", 1.0),
            comparable_vehicles=json.dumps(ai_results.get("comparable_vehicles", [])),
            ai_confidence_score=ai_results.get("confidence_score", 0.0),
            ai_market_trends=json.dumps(ai_results.get("market_trends", {})),
            local_demand_factor=ai_results.get("local_demand_factor", 1.0),
            import_tax_adjustment=ai_results.get("import_tax_adjustment", 0.0),
            regional_price_adjustment=ai_results.get("regional_price_adjustment", 0.0)
        )
        
        return self.create_valuation(valuation_data, valuer_id)
    
    def _basic_valuation_calculation(
        self,
        vehicle: Vehicle,
        similar_vehicles: List[Vehicle]
    ) -> Dict[str, Any]:
        """Basic valuation calculation without AI"""
        # Simple average depreciation calculation
        current_year = datetime.now().year
        vehicle_age = current_year - vehicle.year
        depreciation_rate = min(vehicle_age * 0.1, 0.7)  # 10% per year, max 70%
        
        # Base value estimation (simplified)
        base_value = 500000  # ETB base value for average car
        
        # Adjust for make/model (simplified)
        make_adjustments = {
            "Toyota": 1.2,
            "Honda": 1.1,
            "BMW": 1.5,
            "Mercedes": 1.6,
            "Hyundai": 0.9,
            "Kia": 0.85
        }
        
        make_factor = make_adjustments.get(vehicle.make, 1.0)
        
        # Calculate market value
        market_value = base_value * make_factor * (1 - depreciation_rate)
        
        # Ethiopian market factors
        local_demand_factor = 1.0
        if vehicle.region and "addis" in vehicle.region.lower():
            local_demand_factor = 1.1  # Higher demand in Addis
        
        import_tax_adjustment = 0.0
        if not vehicle.custom_duty_paid:
            import_tax_adjustment = -0.2  # Penalty for unpaid customs
        
        market_value *= local_demand_factor * (1 + import_tax_adjustment)
        
        return {
            "market_value": round(market_value, 2),
            "method": "Market Comparison",
            "depreciation_rate": depreciation_rate,
            "condition_factor": 1.0,
            "confidence_score": 0.7,
            "local_demand_factor": local_demand_factor,
            "import_tax_adjustment": import_tax_adjustment,
            "regional_price_adjustment": 0.0,
            "comparable_vehicles": [],
            "market_trends": {}
        }
    
    def get_valuation(self, valuation_id: UUID) -> Optional[VehicleValuation]:
        """Get valuation by ID"""
        return self.valuation_repo.get_by_id(valuation_id)
    
    def update_valuation(
        self,
        valuation_id: UUID,
        update_data: Dict[str, Any]
    ) -> Optional[VehicleValuation]:
        """Update valuation"""
        # Recalculate taxable value if market value changed
        if "market_value" in update_data:
            update_data["taxable_value"] = update_data["market_value"] * 0.25
        
        return self.valuation_repo.update(valuation_id, update_data)
    
    def approve_valuation(
        self,
        valuation_id: UUID,
        approved_by: UUID
    ) -> Optional[VehicleValuation]:
        """Approve valuation and generate certificate number"""
        # Generate certificate number
        certificate_number = self._generate_certificate_number()
        
        return self.valuation_repo.approve_valuation(
            valuation_id,
            approved_by,
            certificate_number
        )
    
    def _generate_certificate_number(self) -> str:
        """Generate unique certificate number"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_suffix = str(hash(timestamp))[:6].upper()
        return f"VAL-{timestamp}-{random_suffix}"
    
    def get_vehicle_valuations(self, vehicle_id: UUID) -> List[VehicleValuation]:
        """Get all valuations for a vehicle"""
        return self.valuation_repo.get_vehicle_valuations(vehicle_id)
    
    def get_latest_valuation(self, vehicle_id: UUID) -> Optional[VehicleValuation]:
        """Get latest approved valuation for a vehicle"""
        return self.valuation_repo.get_latest_valuation(vehicle_id)
    
    def search_valuations(self, **filters) -> List[VehicleValuation]:
        """Search valuations with filters"""
        return self.valuation_repo.search_valuations(**filters)
    
    # Statistics and Analytics
    def get_valuation_statistics(
        self,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get valuation statistics"""
        valuations = self.valuation_repo.search_valuations(
            date_from=date_from,
            date_to=date_to,
            limit=10000  # Large limit for statistics
        )
        
        if not valuations:
            return {
                "total_valuations": 0,
                "total_market_value": 0,
                "average_value": 0,
                "by_make": {},
                "by_region": {},
                "by_status": {}
            }
        
        total_value = sum(v.market_value for v in valuations)
        avg_value = total_value / len(valuations)
        
        # Group by make
        by_make = {}
        by_region = {}
        by_status = {}
        
        for valuation in valuations:
            # Group by vehicle make
            if valuation.vehicle:
                make = valuation.vehicle.make
                by_make[make] = by_make.get(make, 0) + 1
                
                # Group by region
                region = valuation.vehicle.region or "Unknown"
                by_region[region] = by_region.get(region, 0) + 1
            
            # Group by status
            status = valuation.status
            by_status[status] = by_status.get(status, 0) + 1
        
        return {
            "total_valuations": len(valuations),
            "total_market_value": round(total_value, 2),
            "average_value": round(avg_value, 2),
            "by_make": by_make,
            "by_region": by_region,
            "by_status": by_status
        }
    
    def get_market_trends(self, make: Optional[str] = None) -> Dict[str, Any]:
        """Get market trends for analysis"""
        # This would integrate with the AI market trend analyzer
        # For now, return basic statistics
        return {
            "popular_makes": ["Toyota", "Hyundai", "Honda"],
            "average_prices": {
                "sedan": 450000,
                "suv": 650000,
                "truck": 800000
            },
            "market_growth": 0.05,  # 5% growth
            "regional_variations": {
                "Addis Ababa": 1.1,
                "Oromia": 0.95,
                "Amhara": 0.9
            }
        }
