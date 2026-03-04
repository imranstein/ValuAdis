"""
Vehicle Analyzer AI Component

Analyzes vehicle condition, specifications, and market position
using machine learning and rule-based systems.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import statistics

from ...models import Vehicle, VehicleValuation

logger = logging.getLogger(__name__)


class VehicleAnalyzer:
    """AI-powered vehicle analysis engine"""
    
    def __init__(self):
        self.condition_factors = {
            "excellent": 1.0,
            "good": 0.9,
            "fair": 0.75,
            "poor": 0.6
        }
        
        self.make_reliability_scores = {
            "Toyota": 0.95,
            "Honda": 0.90,
            "Mazda": 0.85,
            "Nissan": 0.80,
            "Hyundai": 0.75,
            "Kia": 0.75,
            "BMW": 0.85,
            "Mercedes": 0.85,
            "Audi": 0.80,
            "Volkswagen": 0.80
        }
        
        self.fuel_type_adjustments = {
            "gasoline": 1.0,
            "diesel": 1.1,  # Higher demand in Ethiopia
            "hybrid": 1.2,
            "electric": 0.8,  # Lower demand due to infrastructure
            "lpg": 0.9
        }
    
    def analyze_vehicle(
        self,
        vehicle: Vehicle,
        similar_vehicles: List[Vehicle],
        market_data: List[VehicleValuation]
    ) -> Dict[str, Any]:
        """Comprehensive vehicle analysis"""
        try:
            analysis = {
                "vehicle_id": str(vehicle.id),
                "analysis_timestamp": datetime.utcnow().isoformat(),
                "condition_analysis": self._analyze_condition(vehicle),
                "specification_analysis": self._analyze_specifications(vehicle),
                "market_analysis": self._analyze_market_position(vehicle, similar_vehicles, market_data),
                "ethiopian_factors": self._analyze_ethiopian_factors(vehicle),
                "confidence_score": 0.0
            }
            
            # Calculate overall confidence score
            analysis["confidence_score"] = self._calculate_confidence_score(analysis)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Vehicle analysis failed: {e}")
            return self._fallback_analysis(vehicle)
    
    def _analyze_condition(self, vehicle: Vehicle) -> Dict[str, Any]:
        """Analyze vehicle condition based on available data"""
        current_year = datetime.now().year
        vehicle_age = current_year - vehicle.year
        
        # Calculate depreciation based on age
        age_depreciation = min(vehicle_age * 0.1, 0.7)  # 10% per year, max 70%
        
        # Mileage-based depreciation
        mileage_depreciation = 0.0
        if vehicle.mileage:
            # Ethiopian average: 20,000 km/year
            expected_mileage = vehicle_age * 20000
            if vehicle.mileage > expected_mileage:
                excess_mileage = vehicle.mileage - expected_mileage
                mileage_depreciation = min(excess_mileage / 100000, 0.3)  # Max 30% penalty
        
        # Previous owners impact
        owners_penalty = max(0, (vehicle.previous_owners - 1) * 0.05)  # 5% per additional owner
        
        # Overall condition factor
        condition_factor = 1.0 - (age_depreciation + mileage_depreciation + owners_penalty)
        condition_factor = max(0.3, condition_factor)  # Minimum 30% of original value
        
        return {
            "age_years": vehicle_age,
            "age_depreciation": age_depreciation,
            "mileage": vehicle.mileage,
            "mileage_depreciation": mileage_depreciation,
            "previous_owners": vehicle.previous_owners,
            "owners_penalty": owners_penalty,
            "condition_factor": round(condition_factor, 3),
            "condition_rating": self._get_condition_rating(condition_factor)
        }
    
    def _analyze_specifications(self, vehicle: Vehicle) -> Dict[str, Any]:
        """Analyze vehicle specifications and their market impact"""
        analysis = {
            "make_reliability": self.make_reliability_scores.get(vehicle.make, 0.7),
            "engine_capacity_factor": 1.0,
            "fuel_type_adjustment": self.fuel_type_adjustments.get(vehicle.fuel_type, 1.0),
            "transmission_preference": 1.0,
            "body_type_demand": 1.0
        }
        
        # Engine capacity impact (Ethiopian market preferences)
        if vehicle.engine_capacity:
            if vehicle.engine_capacity < 1000:  # Small cars
                analysis["engine_capacity_factor"] = 0.9
            elif vehicle.engine_capacity > 3000:  # Large engines
                analysis["engine_capacity_factor"] = 0.85
            else:  # Standard range
                analysis["engine_capacity_factor"] = 1.0
        
        # Transmission preference (Ethiopian market prefers automatic)
        if vehicle.transmission:
            if vehicle.transmission.lower() == "automatic":
                analysis["transmission_preference"] = 1.1
            elif vehicle.transmission.lower() == "manual":
                analysis["transmission_preference"] = 0.95
        
        # Body type demand
        if vehicle.body_type:
            body_demand = {
                "sedan": 1.0,
                "suv": 1.2,  # High demand for SUVs
                "hatchback": 0.9,
                "pickup": 1.1,
                "truck": 1.05,
                "van": 0.95
            }
            analysis["body_type_demand"] = body_demand.get(vehicle.body_type.lower(), 1.0)
        
        return analysis
    
    def _analyze_market_position(
        self,
        vehicle: Vehicle,
        similar_vehicles: List[Vehicle],
        market_data: List[VehicleValuation]
    ) -> Dict[str, Any]:
        """Analyze vehicle's position in the market"""
        if not market_data:
            return {
                "market_position": "insufficient_data",
                "price_percentile": 0.5,
                "competitor_count": 0,
                "market_saturation": "low"
            }
        
        # Extract market values
        market_values = [v.market_value for v in market_data]
        
        # Calculate market statistics
        avg_market_value = statistics.mean(market_values)
        median_market_value = statistics.median(market_values)
        market_std = statistics.stdev(market_values) if len(market_values) > 1 else 0
        
        # Determine market position
        position = "average"
        percentile = 0.5
        
        if market_std > 0:
            # Simplified percentile calculation
            z_score = (avg_market_value - median_market_value) / market_std
            if z_score > 1:
                position = "premium"
                percentile = 0.8
            elif z_score < -1:
                position = "budget"
                percentile = 0.2
            else:
                position = "average"
                percentile = 0.5
        
        # Market saturation
        saturation = "low"
        if len(similar_vehicles) > 50:
            saturation = "high"
        elif len(similar_vehicles) > 20:
            saturation = "medium"
        
        return {
            "market_position": position,
            "price_percentile": percentile,
            "avg_market_value": round(avg_market_value, 2),
            "median_market_value": round(median_market_value, 2),
            "market_volatility": round(market_std / avg_market_value, 3) if avg_market_value > 0 else 0,
            "competitor_count": len(similar_vehicles),
            "market_saturation": saturation
        }
    
    def _analyze_ethiopian_factors(self, vehicle: Vehicle) -> Dict[str, Any]:
        """Analyze Ethiopian market-specific factors"""
        factors = {
            "customs_duty_impact": 0.0,
            "regional_demand": 1.0,
            "import_year_adjustment": 1.0,
            "local_availability": 1.0
        }
        
        # Customs duty impact
        if not vehicle.custom_duty_paid:
            factors["customs_duty_impact"] = -0.2  # 20% penalty for unpaid duties
        else:
            factors["customs_duty_impact"] = 0.05  # Small premium for legal vehicles
        
        # Regional demand adjustments
        if vehicle.region:
            regional_multipliers = {
                "addis ababa": 1.15,  # Highest demand
                "oromia": 1.0,
                "amhara": 0.95,
                "tigray": 0.9,
                "southern": 0.85,
                "somali": 0.8,
                "afar": 0.75
            }
            region_lower = vehicle.region.lower()
            for region, multiplier in regional_multipliers.items():
                if region in region_lower:
                    factors["regional_demand"] = multiplier
                    break
        
        # Import year adjustments (newer imports preferred)
        if vehicle.import_year:
            current_year = datetime.now().year
            import_age = current_year - vehicle.import_year
            
            if import_age <= 1:
                factors["import_year_adjustment"] = 1.1
            elif import_age <= 3:
                factors["import_year_adjustment"] = 1.0
            elif import_age <= 5:
                factors["import_year_adjustment"] = 0.95
            else:
                factors["import_year_adjustment"] = 0.85
        
        # Local availability (common vs rare models)
        make_model = f"{vehicle.make} {vehicle.model}".lower()
        common_models = [
            "toyota corolla", "toyota yaris", "hyundai accent", "kia rio",
            "honda civic", "nissan sunny", "mazda 3"
        ]
        
        if any(common in make_model for common in common_models):
            factors["local_availability"] = 1.0  # Common parts and service
        else:
            factors["local_availability"] = 0.9  # Slightly less preferred
        
        return factors
    
    def _get_condition_rating(self, condition_factor: float) -> str:
        """Get condition rating from factor"""
        if condition_factor >= 0.9:
            return "excellent"
        elif condition_factor >= 0.75:
            return "good"
        elif condition_factor >= 0.6:
            return "fair"
        else:
            return "poor"
    
    def _calculate_confidence_score(self, analysis: Dict[str, Any]) -> float:
        """Calculate overall confidence in the analysis"""
        score = 0.5  # Base score
        
        # Data completeness bonus
        if analysis.get("condition_analysis", {}).get("mileage"):
            score += 0.1
        if analysis.get("condition_analysis", {}).get("previous_owners"):
            score += 0.05
        
        # Market data availability
        market_analysis = analysis.get("market_analysis", {})
        if market_analysis.get("competitor_count", 0) > 10:
            score += 0.2
        elif market_analysis.get("competitor_count", 0) > 0:
            score += 0.1
        
        # Specification detail
        spec_analysis = analysis.get("specification_analysis", {})
        if spec_analysis.get("engine_capacity_factor"):
            score += 0.05
        if spec_analysis.get("fuel_type_adjustment"):
            score += 0.05
        
        # Ethiopian factors
        ethio_factors = analysis.get("ethiopian_factors", {})
        if ethio_factors.get("regional_demand"):
            score += 0.05
        
        return min(1.0, score)
    
    def _fallback_analysis(self, vehicle: Vehicle) -> Dict[str, Any]:
        """Fallback analysis when main analysis fails"""
        return {
            "vehicle_id": str(vehicle.id),
            "analysis_timestamp": datetime.utcnow().isoformat(),
            "condition_analysis": {
                "age_years": datetime.now().year - vehicle.year,
                "condition_factor": 0.8,
                "condition_rating": "fair"
            },
            "specification_analysis": {
                "make_reliability": self.make_reliability_scores.get(vehicle.make, 0.7),
                "fuel_type_adjustment": 1.0
            },
            "market_analysis": {
                "market_position": "average",
                "price_percentile": 0.5,
                "competitor_count": 0
            },
            "ethiopian_factors": {
                "customs_duty_impact": 0.0,
                "regional_demand": 1.0
            },
            "confidence_score": 0.5
        }
