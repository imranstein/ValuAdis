"""
Vehicle Valuation Service

Calculates vehicle valuations with Ethiopian market-specific factors
including regional demand, import adjustments, and customs duties.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import statistics
from ..models.vehicle import Vehicle
from ..models.vehicle_valuation import VehicleValuation

logger = logging.getLogger(__name__)

class VehicleValuationService:
    """Service for calculating vehicle valuations with Ethiopian market factors"""
    
    def __init__(self):
        # Ethiopian regional demand multipliers
        self.regional_multipliers = {
            "addis ababa": 1.15,  # Highest demand
            "oromia": 1.0,
            "amhara": 0.95,
            "tigray": 0.9,
            "southern": 0.85,
            "somali": 0.8,
            "afar": 0.75,
            "benishangul": 0.8,
            "gambela": 0.8,
            "harari": 0.9,
            "dire dawa": 0.95
        }
        
        # Make reliability scores for Ethiopian market
        self.make_reliability_scores = {
            "toyota": 0.95,
            "honda": 0.90,
            "mazda": 0.85,
            "nissan": 0.80,
            "hyundai": 0.75,
            "kia": 0.75,
            "bmw": 0.85,
            "mercedes": 0.85,
            "audi": 0.80,
            "volkswagen": 0.80,
            "byd": 0.70,  # New to Ethiopian market
            "tesla": 0.65,  # Limited infrastructure
            "ford": 0.75,
            "chevrolet": 0.70,
            "isuzu": 0.85,  # Popular for commercial vehicles
            "hino": 0.85,  # Popular for trucks
        }
        
        # Fuel type adjustments for Ethiopian market
        self.fuel_type_adjustments = {
            "gasoline": 1.0,
            "diesel": 1.1,  # Higher demand in Ethiopia
            "hybrid": 1.2,  # Growing demand
            "electric": 0.8,  # Lower demand due to infrastructure
            "lpg": 0.9,
            "cng": 0.85
        }
        
        # Body type demand factors
        self.body_type_demand = {
            "sedan": 1.0,
            "suv": 1.2,  # High demand for SUVs
            "hatchback": 0.9,
            "pickup": 1.1,  # Popular in Ethiopia
            "truck": 1.05,
            "van": 0.95,
            "coupe": 0.8,
            "convertible": 0.7,
            "station wagon": 0.9
        }
        
        # Base market values by category (in ETB)
        self.base_market_values = {
            "sedan": {
                "compact": 400000,  # ~$7,000
                "midsize": 600000,   # ~$10,500
                "fullsize": 800000,  # ~$14,000
                "luxury": 1500000    # ~$26,000
            },
            "suv": {
                "compact": 500000,   # ~$8,750
                "midsize": 700000,   # ~$12,250
                "fullsize": 900000,  # ~$15,750
                "luxury": 1800000    # ~$31,500
            },
            "pickup": {
                "compact": 450000,   # ~$7,875
                "midsize": 650000,   # ~$11,375
                "fullsize": 850000,  # ~$14,875
                "heavy": 1200000     # ~$21,000
            },
            "truck": {
                "light": 600000,     # ~$10,500
                "medium": 900000,    # ~$15,750
                "heavy": 1500000     # ~$26,250
            }
        }
    
    def calculate_vehicle_valuation(self, vehicle: Vehicle) -> Dict[str, Any]:
        """
        Calculate comprehensive vehicle valuation with Ethiopian market factors
        
        Args:
            vehicle: Vehicle object with all specifications
            
        Returns:
            Dictionary with valuation details and factors
        """
        try:
            # Step 1: Calculate base market value
            base_value = self._calculate_base_value(vehicle)
            
            # Step 2: Apply condition depreciation
            condition_factor = self._calculate_condition_factor(vehicle)
            
            # Step 3: Apply Ethiopian market factors
            ethiopian_factors = self._calculate_ethiopian_factors(vehicle)
            
            # Step 4: Calculate final market value
            market_value = base_value * condition_factor * ethiopian_factors["total_multiplier"]
            
            # Step 5: Calculate taxable value (25% per Ethiopian regulations)
            taxable_value = market_value * 0.25
            
            # Step 6: Calculate confidence score
            confidence_score = self._calculate_confidence_score(vehicle, ethiopian_factors)
            
            valuation_result = {
                "vehicle_id": vehicle.id,
                "valuation_date": datetime.utcnow().isoformat(),
                "base_value": round(base_value, 2),
                "condition_factor": round(condition_factor, 3),
                "market_value": round(market_value, 2),
                "taxable_value": round(taxable_value, 2),
                "confidence_score": round(confidence_score, 3),
                "ethiopian_factors": ethiopian_factors,
                "condition_analysis": self._get_condition_analysis(vehicle),
                "market_position": self._determine_market_position(market_value, vehicle),
                "recommendations": self._generate_recommendations(vehicle, market_value)
            }
            
            logger.info(f"Calculated vehicle valuation for {vehicle.make} {vehicle.model}: ETB {market_value:,.2f}")
            return valuation_result
            
        except Exception as e:
            logger.error(f"Vehicle valuation calculation failed: {e}")
            return self._fallback_valuation(vehicle)
    
    def _calculate_base_value(self, vehicle: Vehicle) -> float:
        """Calculate base market value based on vehicle specifications"""
        # Determine vehicle category and size
        category = self._determine_vehicle_category(vehicle)
        size = self._determine_vehicle_size(vehicle)
        
        # Get base value from lookup table
        if category in self.base_market_values and size in self.base_market_values[category]:
            base_value = self.base_market_values[category][size]
        else:
            # Default to midsize sedan if category not found
            base_value = self.base_market_values["sedan"]["midsize"]
        
        # Adjust for engine capacity
        if vehicle.engine_capacity:
            if vehicle.engine_capacity < 1000:  # Small engines
                base_value *= 0.9
            elif vehicle.engine_capacity > 3000:  # Large engines
                base_value *= 1.1
        
        # Adjust for year (depreciation)
        current_year = datetime.now().year
        vehicle_age = current_year - vehicle.year
        
        # Standard depreciation: 10% per year for first 5 years, then 8%
        if vehicle_age <= 5:
            depreciation = vehicle_age * 0.10
        else:
            depreciation = 0.5 + (vehicle_age - 5) * 0.08
        
        depreciation = min(depreciation, 0.8)  # Maximum 80% depreciation
        base_value *= (1 - depreciation)
        
        # Ensure minimum value
        base_value = max(base_value, 50000)  # Minimum ETB 50,000
        
        return base_value
    
    def _calculate_condition_factor(self, vehicle: Vehicle) -> float:
        """Calculate condition factor based on mileage and ownership"""
        current_year = datetime.now().year
        vehicle_age = current_year - vehicle.year
        
        # Mileage-based depreciation
        mileage_depreciation = 0.0
        if vehicle.mileage:
            # Ethiopian average: 15,000 km/year
            expected_mileage = vehicle_age * 15000
            if vehicle.mileage > expected_mileage:
                excess_mileage = vehicle.mileage - expected_mileage
                mileage_depreciation = min(excess_mileage / 100000, 0.3)  # Max 30% penalty
        
        # Previous owners impact
        owners_penalty = max(0, (vehicle.previous_owners - 1) * 0.05)  # 5% per additional owner
        
        # Overall condition factor
        condition_factor = 1.0 - (mileage_depreciation + owners_penalty)
        return max(0.3, condition_factor)  # Minimum 30% of base value
    
    def _calculate_ethiopian_factors(self, vehicle: Vehicle) -> Dict[str, Any]:
        """Calculate Ethiopian market-specific factors"""
        factors = {
            "regional_multiplier": 1.0,
            "import_year_adjustment": 1.0,
            "customs_duty_factor": 1.0,
            "make_reliability": 1.0,
            "fuel_type_adjustment": 1.0,
            "body_type_demand": 1.0,
            "total_multiplier": 1.0
        }
        
        # Regional demand adjustment
        if vehicle.region:
            region_lower = vehicle.region.lower()
            for region, multiplier in self.regional_multipliers.items():
                if region in region_lower:
                    factors["regional_multiplier"] = multiplier
                    break
        
        # Import year adjustments
        if vehicle.import_year:
            current_year = datetime.now().year
            import_age = current_year - vehicle.import_year
            
            if import_age <= 1:
                factors["import_year_adjustment"] = 1.1  # Recent imports preferred
            elif import_age <= 3:
                factors["import_year_adjustment"] = 1.0
            elif import_age <= 5:
                factors["import_year_adjustment"] = 0.95
            else:
                factors["import_year_adjustment"] = 0.85  # Older imports less preferred
        
        # Customs duty impact
        if vehicle.custom_duty_paid:
            factors["customs_duty_factor"] = 1.05  # Small premium for legal vehicles
        else:
            factors["customs_duty_factor"] = 0.8  # Penalty for unpaid duties
        
        # Make reliability
        make_lower = vehicle.make.lower()
        factors["make_reliability"] = self.make_reliability_scores.get(make_lower, 0.7)
        
        # Fuel type adjustment
        fuel_lower = vehicle.fuel_type.lower() if vehicle.fuel_type else ""
        factors["fuel_type_adjustment"] = self.fuel_type_adjustments.get(fuel_lower, 1.0)
        
        # Body type demand
        body_lower = vehicle.body_type.lower() if vehicle.body_type else ""
        factors["body_type_demand"] = self.body_type_demand.get(body_lower, 1.0)
        
        # Calculate total multiplier
        factors["total_multiplier"] = (
            factors["regional_multiplier"] *
            factors["import_year_adjustment"] *
            factors["customs_duty_factor"] *
            factors["make_reliability"] *
            factors["fuel_type_adjustment"] *
            factors["body_type_demand"]
        )
        
        return factors
    
    def _determine_vehicle_category(self, vehicle: Vehicle) -> str:
        """Determine vehicle category based on body type"""
        if not vehicle.body_type:
            return "sedan"  # Default
        
        body_lower = vehicle.body_type.lower()
        
        if "truck" in body_lower:
            return "truck"
        elif "pickup" in body_lower:
            return "pickup"
        elif "suv" in body_lower:
            return "suv"
        elif "van" in body_lower:
            return "truck"  # Group vans with trucks
        else:
            return "sedan"  # Default for cars
    
    def _determine_vehicle_size(self, vehicle: Vehicle) -> str:
        """Determine vehicle size based on engine capacity and other factors"""
        if not vehicle.engine_capacity:
            return "midsize"  # Default
        
        if vehicle.engine_capacity < 1500:
            return "compact"
        elif vehicle.engine_capacity < 2500:
            return "midsize"
        elif vehicle.engine_capacity < 3500:
            return "fullsize"
        else:
            return "luxury"  # Large engines typically luxury
    
    def _calculate_confidence_score(self, vehicle: Vehicle, factors: Dict[str, Any]) -> float:
        """Calculate confidence score for the valuation"""
        score = 0.5  # Base score
        
        # Data completeness bonus
        if vehicle.mileage:
            score += 0.1
        if vehicle.vin:
            score += 0.1
        if vehicle.engine_capacity:
            score += 0.05
        if vehicle.import_year:
            score += 0.05
        
        # Market factor reliability
        if factors["regional_multiplier"] != 1.0:
            score += 0.05
        if factors["make_reliability"] > 0.8:
            score += 0.05
        
        # Vehicle age (newer vehicles have more reliable data)
        current_year = datetime.now().year
        vehicle_age = current_year - vehicle.year
        if vehicle_age <= 5:
            score += 0.1
        elif vehicle_age <= 10:
            score += 0.05
        
        return min(1.0, score)
    
    def _get_condition_analysis(self, vehicle: Vehicle) -> Dict[str, Any]:
        """Get detailed condition analysis"""
        current_year = datetime.now().year
        vehicle_age = current_year - vehicle.year
        
        return {
            "age_years": vehicle_age,
            "mileage": vehicle.mileage,
            "previous_owners": vehicle.previous_owners,
            "age_depreciation": min(vehicle_age * 0.10, 0.5) if vehicle_age <= 5 else 0.5 + (vehicle_age - 5) * 0.08,
            "condition_rating": self._get_condition_rating(vehicle)
        }
    
    def _get_condition_rating(self, vehicle: Vehicle) -> str:
        """Get condition rating from condition factor"""
        condition_factor = self._calculate_condition_factor(vehicle)
        
        if condition_factor >= 0.9:
            return "excellent"
        elif condition_factor >= 0.75:
            return "good"
        elif condition_factor >= 0.6:
            return "fair"
        else:
            return "poor"
    
    def _determine_market_position(self, market_value: float, vehicle: Vehicle) -> str:
        """Determine market position based on value"""
        # This is a simplified version - in production, you'd compare with market data
        if market_value > 2000000:  # > ~$35,000
            return "premium"
        elif market_value > 800000:  # > ~$14,000
            return "above_average"
        elif market_value > 400000:  # > ~$7,000
            return "average"
        else:
            return "budget"
    
    def _generate_recommendations(self, vehicle: Vehicle, market_value: float) -> List[str]:
        """Generate recommendations based on vehicle and valuation"""
        recommendations = []
        
        # Customs duty recommendation
        if not vehicle.custom_duty_paid:
            recommendations.append("Consider paying customs duties to increase market value by 20%")
        
        # Regional recommendation
        if vehicle.region and vehicle.region.lower() != "addis ababa":
            recommendations.append("Consider selling in Addis Ababa for 15% higher market value")
        
        # Maintenance recommendation
        current_year = datetime.now().year
        vehicle_age = current_year - vehicle.year
        if vehicle_age > 10:
            recommendations.append("Vehicle is over 10 years old - consider maintenance records for better valuation")
        
        # Fuel type recommendation
        if vehicle.fuel_type and vehicle.fuel_type.lower() == "electric":
            recommendations.append("Electric vehicles have limited market demand due to infrastructure")
        
        return recommendations
    
    def _fallback_valuation(self, vehicle: Vehicle) -> Dict[str, Any]:
        """Fallback valuation when main calculation fails"""
        return {
            "vehicle_id": vehicle.id,
            "valuation_date": datetime.utcnow().isoformat(),
            "base_value": 500000,  # Default base value
            "condition_factor": 0.8,
            "market_value": 400000,
            "taxable_value": 100000,
            "confidence_score": 0.3,
            "ethiopian_factors": {
                "regional_multiplier": 1.0,
                "import_year_adjustment": 1.0,
                "customs_duty_factor": 1.0,
                "make_reliability": 0.7,
                "fuel_type_adjustment": 1.0,
                "body_type_demand": 1.0,
                "total_multiplier": 1.0
            },
            "error": "Valuation calculation failed, using fallback values"
        }

# Singleton instance
vehicle_valuation_service = VehicleValuationService()
