"""
Valuation Calculator AI Component

Calculates vehicle market values using AI algorithms,
market data, and Ethiopian market factors.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import statistics
import math

from ..models import Vehicle, VehicleValuation

logger = logging.getLogger(__name__)


class ValuationCalculator:
    """AI-powered vehicle valuation calculator"""
    
    def __init__(self):
        self.base_values = {
            "sedan": 450000,      # ETB base value for average sedan
            "suv": 650000,        # ETB base value for average SUV
            "hatchback": 350000,  # ETB base value for average hatchback
            "pickup": 750000,     # ETB base value for average pickup
            "truck": 1200000,     # ETB base value for average truck
            "van": 550000,        # ETB base value for average van
            "coupe": 500000,      # ETB base value for average coupe
            "convertible": 600000 # ETB base value for average convertible
        }
        
        self.make_multipliers = {
            "toyota": 1.25,
            "honda": 1.15,
            "mazda": 1.10,
            "nissan": 1.05,
            "hyundai": 0.95,
            "kia": 0.90,
            "bmw": 1.40,
            "mercedes": 1.45,
            "audi": 1.35,
            "volkswagen": 1.20,
            "ford": 1.00,
            "chevrolet": 0.95,
            "subaru": 1.10,
            "mitsubishi": 1.05,
            "suzuki": 0.90
        }
        
        self.ethiopian_adjustments = {
            "addis ababa": 1.15,
            "oromia": 1.00,
            "amhara": 0.95,
            "tigray": 0.90,
            "southern": 0.85,
            "somali": 0.80,
            "afar": 0.75,
            "gambela": 0.80,
            "benishangul": 0.80,
            "harari": 1.05,
            "dire dawa": 1.10
        }
    
    def calculate_value(
        self,
        vehicle: Vehicle,
        similar_vehicles: List[Vehicle],
        market_valuations: List[VehicleValuation],
        ai_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate vehicle market value using AI and market data"""
        try:
            calculation = {
                "vehicle_id": str(vehicle.id),
                "calculation_method": "ai_enhanced",
                "base_value": 0,
                "adjustments": {},
                "final_value": 0,
                "confidence_score": 0.0,
                "supporting_data": {}
            }
            
            # Step 1: Determine base value
            base_value = self._calculate_base_value(vehicle)
            calculation["base_value"] = base_value
            
            # Step 2: Apply adjustments
            adjustments = self._calculate_adjustments(vehicle, ai_analysis)
            calculation["adjustments"] = adjustments
            
            # Step 3: Incorporate market data
            market_adjustment = self._apply_market_data(
                vehicle, similar_vehicles, market_valuations
            )
            calculation["supporting_data"]["market_adjustment"] = market_adjustment
            
            # Step 4: Calculate final value
            final_value = self._apply_all_adjustments(base_value, adjustments, market_adjustment)
            calculation["final_value"] = round(final_value, 2)
            
            # Step 5: Calculate confidence score
            calculation["confidence_score"] = self._calculate_confidence(
                vehicle, similar_vehicles, market_valuations, ai_analysis
            )
            
            return calculation
            
        except Exception as e:
            logger.error(f"Valuation calculation failed: {e}")
            return self._fallback_calculation(vehicle)
    
    def _calculate_base_value(self, vehicle: Vehicle) -> float:
        """Calculate base value for vehicle"""
        # Get base value by body type
        body_type = vehicle.body_type.lower() if vehicle.body_type else "sedan"
        base_value = self.base_values.get(body_type, 450000)
        
        # Apply make multiplier
        make_multiplier = self.make_multipliers.get(vehicle.make.lower(), 1.0)
        base_value *= make_multiplier
        
        # Adjust for engine capacity
        if vehicle.engine_capacity:
            if vehicle.engine_capacity < 1000:  # Small engines
                base_value *= 0.9
            elif vehicle.engine_capacity > 3000:  # Large engines
                base_value *= 1.2
            elif vehicle.engine_capacity > 2500:  # Large but not too large
                base_value *= 1.1
        
        # Adjust for year (base value assumes 5-year-old vehicle)
        current_year = datetime.now().year
        vehicle_age = current_year - vehicle.year
        
        if vehicle_age <= 1:
            base_value *= 1.5  # Nearly new premium
        elif vehicle_age <= 3:
            base_value *= 1.3  # Recent model
        elif vehicle_age <= 5:
            base_value *= 1.0  # Standard assumption
        elif vehicle_age <= 8:
            base_value *= 0.8  # Older but reasonable
        elif vehicle_age <= 12:
            base_value *= 0.6  # Getting old
        else:
            base_value *= 0.4  # Very old
        
        return base_value
    
    def _calculate_adjustments(self, vehicle: Vehicle, ai_analysis: Dict[str, Any]) -> Dict[str, float]:
        """Calculate various value adjustments"""
        adjustments = {}
        
        # Condition adjustment from AI analysis
        condition_analysis = ai_analysis.get("condition_analysis", {})
        if "condition_factor" in condition_analysis:
            adjustments["condition"] = condition_analysis["condition_factor"]
        
        # Specification adjustments
        spec_analysis = ai_analysis.get("specification_analysis", {})
        if spec_analysis.get("fuel_type_adjustment"):
            adjustments["fuel_type"] = spec_analysis["fuel_type_adjustment"]
        if spec_analysis.get("transmission_preference"):
            adjustments["transmission"] = spec_analysis["transmission_preference"]
        if spec_analysis.get("body_type_demand"):
            adjustments["body_type_demand"] = spec_analysis["body_type_demand"]
        
        # Ethiopian factors
        ethio_factors = ai_analysis.get("ethiopian_factors", {})
        if ethio_factors.get("customs_duty_impact"):
            adjustments["customs_duty"] = 1.0 + ethio_factors["customs_duty_impact"]
        if ethio_factors.get("regional_demand"):
            adjustments["regional_demand"] = ethio_factors["regional_demand"]
        if ethio_factors.get("import_year_adjustment"):
            adjustments["import_year"] = ethio_factors["import_year_adjustment"]
        if ethio_factors.get("local_availability"):
            adjustments["local_availability"] = ethio_factors["local_availability"]
        
        # Manual adjustments for missing data
        if not adjustments.get("condition"):
            # Calculate condition based on mileage and age
            current_year = datetime.now().year
            age = current_year - vehicle.year
            mileage_depreciation = 0.0
            
            if vehicle.mileage:
                expected_mileage = age * 20000  # Ethiopian average
                if vehicle.mileage > expected_mileage:
                    excess = vehicle.mileage - expected_mileage
                    mileage_depreciation = min(excess / 100000, 0.3)
            
            condition_factor = max(0.6, 1.0 - (age * 0.1 + mileage_depreciation))
            adjustments["condition"] = condition_factor
        
        if not adjustments.get("regional_demand") and vehicle.region:
            region_lower = vehicle.region.lower()
            for region, multiplier in self.ethiopian_adjustments.items():
                if region in region_lower:
                    adjustments["regional_demand"] = multiplier
                    break
        
        return adjustments
    
    def _apply_market_data(
        self,
        vehicle: Vehicle,
        similar_vehicles: List[Vehicle],
        market_valuations: List[VehicleValuation]
    ) -> Dict[str, Any]:
        """Apply market data adjustments"""
        if not market_valuations:
            return {
                "adjustment_factor": 1.0,
                "sample_size": 0,
                "market_alignment": "no_data"
            }
        
        # Filter relevant market data
        relevant_valuations = []
        for valuation in market_valuations:
            # Check if valuation is for similar vehicle
            for similar in similar_vehicles:
                if similar.id == valuation.vehicle_id:
                    relevant_valuations.append(valuation)
                    break
        
        if not relevant_valuations:
            return {
                "adjustment_factor": 1.0,
                "sample_size": 0,
                "market_alignment": "no_similar_data"
            }
        
        # Calculate market statistics
        market_values = [v.market_value for v in relevant_valuations]
        avg_market_value = statistics.mean(market_values)
        median_market_value = statistics.median(market_values)
        
        # Calculate market adjustment factor
        # This would compare our calculated value to market values
        # For now, use a market-based adjustment
        
        # Market trend adjustment
        market_trend = 1.0
        if len(relevant_valuations) >= 3:
            # Sort by valuation date
            sorted_valuations = sorted(
                relevant_valuations, 
                key=lambda x: x.valuation_date
            )
            
            # Compare recent vs older valuations
            midpoint = len(sorted_valuations) // 2
            recent_avg = statistics.mean([
                v.market_value for v in sorted_valuations[midpoint:]
            ])
            older_avg = statistics.mean([
                v.market_value for v in sorted_valuations[:midpoint]
            ])
            
            if recent_avg > older_avg * 1.05:
                market_trend = 1.05  # Increasing market
            elif recent_avg < older_avg * 0.95:
                market_trend = 0.95  # Decreasing market
        
        # Market saturation adjustment
        saturation_factor = 1.0
        if len(relevant_valuations) > 20:
            saturation_factor = 0.98  # Slight discount for high competition
        elif len(relevant_valuations) < 5:
            saturation_factor = 1.02  # Slight premium for low competition
        
        adjustment_factor = market_trend * saturation_factor
        
        return {
            "adjustment_factor": round(adjustment_factor, 3),
            "sample_size": len(relevant_valuations),
            "market_alignment": "aligned" if 0.95 <= adjustment_factor <= 1.05 else "adjusted",
            "avg_market_value": round(avg_market_value, 2),
            "median_market_value": round(median_market_value, 2),
            "market_trend": "increasing" if market_trend > 1.0 else "decreasing" if market_trend < 1.0 else "stable"
        }
    
    def _apply_all_adjustments(
        self,
        base_value: float,
        adjustments: Dict[str, float],
        market_adjustment: Dict[str, Any]
    ) -> float:
        """Apply all adjustments to base value"""
        adjusted_value = base_value
        
        # Apply individual adjustments
        for adjustment_name, factor in adjustments.items():
            adjusted_value *= factor
        
        # Apply market adjustment
        if market_adjustment.get("adjustment_factor"):
            adjusted_value *= market_adjustment["adjustment_factor"]
        
        # Ensure reasonable bounds
        min_value = base_value * 0.3  # Don't go below 30% of base
        max_value = base_value * 2.0  # Don't exceed 200% of base
        
        return max(min_value, min(max_value, adjusted_value))
    
    def _calculate_confidence(
        self,
        vehicle: Vehicle,
        similar_vehicles: List[Vehicle],
        market_valuations: List[VehicleValuation],
        ai_analysis: Dict[str, Any]
    ) -> float:
        """Calculate confidence score for the valuation"""
        confidence = 0.5  # Base confidence
        
        # Data completeness
        if vehicle.mileage:
            confidence += 0.1
        if vehicle.engine_capacity:
            confidence += 0.05
        if vehicle.region:
            confidence += 0.05
        
        # Market data availability
        if len(market_valuations) >= 10:
            confidence += 0.2
        elif len(market_valuations) >= 5:
            confidence += 0.1
        elif len(market_valuations) >= 1:
            confidence += 0.05
        
        # Similar vehicles
        if len(similar_vehicles) >= 20:
            confidence += 0.1
        elif len(similar_vehicles) >= 10:
            confidence += 0.05
        
        # AI analysis confidence
        ai_confidence = ai_analysis.get("confidence_score", 0.5)
        confidence += (ai_confidence - 0.5) * 0.2  # Weight AI confidence
        
        return min(1.0, max(0.0, confidence))
    
    def _fallback_calculation(self, vehicle: Vehicle) -> Dict[str, Any]:
        """Fallback calculation when main calculation fails"""
        # Simple base calculation
        body_type = vehicle.body_type.lower() if vehicle.body_type else "sedan"
        base_value = self.base_values.get(body_type, 450000)
        
        # Make adjustment
        make_multiplier = self.make_multipliers.get(vehicle.make.lower(), 1.0)
        base_value *= make_multiplier
        
        # Age adjustment
        current_year = datetime.now().year
        age = current_year - vehicle.year
        age_factor = max(0.4, 1.0 - (age * 0.1))
        
        final_value = base_value * age_factor
        
        return {
            "vehicle_id": str(vehicle.id),
            "calculation_method": "fallback_simple",
            "base_value": round(base_value, 2),
            "adjustments": {
                "age": age_factor,
                "make": make_multiplier
            },
            "final_value": round(final_value, 2),
            "confidence_score": 0.5,
            "supporting_data": {
                "fallback_reason": "AI calculation unavailable"
            }
        }
