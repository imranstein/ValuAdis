"""
Market Comparator AI Component

Compares vehicles against market data and similar vehicles
to determine competitive positioning and pricing.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import statistics

from ...models import Vehicle, VehicleValuation

logger = logging.getLogger(__name__)


class MarketComparator:
    """AI-powered market comparison engine"""
    
    def __init__(self):
        self.comparison_weights = {
            "make_match": 0.3,
            "model_match": 0.25,
            "year_proximity": 0.2,
            "mileage_similarity": 0.15,
            "regional_proximity": 0.1
        }
    
    def compare_vehicle(
        self,
        target_vehicle: Vehicle,
        similar_vehicles: List[Vehicle],
        market_valuations: Optional[List[VehicleValuation]] = None
    ) -> Dict[str, Any]:
        """Compare target vehicle against market"""
        try:
            comparison = {
                "target_vehicle": {
                    "id": str(target_vehicle.id),
                    "make": target_vehicle.make,
                    "model": target_vehicle.model,
                    "year": target_vehicle.year,
                    "mileage": target_vehicle.mileage,
                    "region": target_vehicle.region
                },
                "comparable_vehicles": [],
                "market_analysis": {},
                "price_positioning": {},
                "recommendations": []
            }
            
            # Find comparable vehicles
            comparable_vehicles = self._find_comparable_vehicles(
                target_vehicle, similar_vehicles, market_valuations
            )
            comparison["comparable_vehicles"] = comparable_vehicles
            
            # Analyze market positioning
            if comparable_vehicles:
                comparison["market_analysis"] = self._analyze_market_data(comparable_vehicles)
                comparison["price_positioning"] = self._analyze_price_positioning(
                    target_vehicle, comparable_vehicles
                )
                comparison["recommendations"] = self._generate_recommendations(
                    target_vehicle, comparable_vehicles
                )
            
            return comparison
            
        except Exception as e:
            logger.error(f"Market comparison failed: {e}")
            return self._fallback_comparison(target_vehicle)
    
    def _find_comparable_vehicles(
        self,
        target_vehicle: Vehicle,
        similar_vehicles: List[Vehicle],
        market_valuations: Optional[List[VehicleValuation]] = None
    ) -> List[Dict[str, Any]]:
        """Find and score comparable vehicles"""
        comparable = []
        
        for vehicle in similar_vehicles:
            if vehicle.id == target_vehicle.id:
                continue
            
            # Calculate similarity score
            similarity_score = self._calculate_similarity(target_vehicle, vehicle)
            
            # Include vehicles with reasonable similarity
            if similarity_score >= 0.3:  # 30% similarity threshold
                vehicle_data = {
                    "id": str(vehicle.id),
                    "make": vehicle.make,
                    "model": vehicle.model,
                    "year": vehicle.year,
                    "mileage": vehicle.mileage,
                    "region": vehicle.region,
                    "similarity_score": round(similarity_score, 3),
                    "market_value": None,
                    "valuation_date": None
                }
                
                # Add market valuation if available
                if market_valuations:
                    for valuation in market_valuations:
                        if valuation.vehicle_id == vehicle.id and valuation.status == "approved":
                            vehicle_data["market_value"] = valuation.market_value
                            vehicle_data["valuation_date"] = valuation.valuation_date.isoformat()
                            break
                
                comparable.append(vehicle_data)
        
        # Sort by similarity score (highest first)
        comparable.sort(key=lambda x: x["similarity_score"], reverse=True)
        
        # Return top 20 most comparable vehicles
        return comparable[:20]
    
    def _calculate_similarity(self, vehicle1: Vehicle, vehicle2: Vehicle) -> float:
        """Calculate similarity score between two vehicles"""
        score = 0.0
        
        # Make match (exact or same manufacturer family)
        if vehicle1.make.lower() == vehicle2.make.lower():
            score += self.comparison_weights["make_match"]
        elif self._is_same_manufacturer_family(vehicle1.make, vehicle2.make):
            score += self.comparison_weights["make_match"] * 0.5
        
        # Model match (exact or similar)
        if vehicle1.model.lower() == vehicle2.model.lower():
            score += self.comparison_weights["model_match"]
        elif self._is_similar_model(vehicle1.model, vehicle2.model):
            score += self.comparison_weights["model_match"] * 0.7
        
        # Year proximity
        year_diff = abs(vehicle1.year - vehicle2.year)
        if year_diff == 0:
            score += self.comparison_weights["year_proximity"]
        elif year_diff <= 1:
            score += self.comparison_weights["year_proximity"] * 0.8
        elif year_diff <= 2:
            score += self.comparison_weights["year_proximity"] * 0.6
        elif year_diff <= 3:
            score += self.comparison_weights["year_proximity"] * 0.4
        elif year_diff <= 5:
            score += self.comparison_weights["year_proximity"] * 0.2
        
        # Mileage similarity
        if vehicle1.mileage and vehicle2.mileage:
            mileage_diff = abs(vehicle1.mileage - vehicle2.mileage)
            mileage_ratio = min(vehicle1.mileage, vehicle2.mileage) / max(vehicle1.mileage, vehicle2.mileage)
            
            if mileage_ratio >= 0.9:
                score += self.comparison_weights["mileage_similarity"]
            elif mileage_ratio >= 0.8:
                score += self.comparison_weights["mileage_similarity"] * 0.8
            elif mileage_ratio >= 0.7:
                score += self.comparison_weights["mileage_similarity"] * 0.6
            elif mileage_ratio >= 0.5:
                score += self.comparison_weights["mileage_similarity"] * 0.4
        
        # Regional proximity
        if vehicle1.region and vehicle2.region:
            if vehicle1.region.lower() == vehicle2.region.lower():
                score += self.comparison_weights["regional_proximity"]
            elif self._is_adjacent_region(vehicle1.region, vehicle2.region):
                score += self.comparison_weights["regional_proximity"] * 0.7
        
        return score
    
    def _is_same_manufacturer_family(self, make1: str, make2: str) -> bool:
        """Check if makes are from same manufacturer family"""
        families = {
            "toyota": ["toyota", "lexus"],
            "honda": ["honda", "acura"],
            "nissan": ["nissan", "infiniti"],
            "hyundai": ["hyundai", "genesis", "kia"],
            "volkswagen": ["volkswagen", "audi", "porsche", "bentley"],
            "bmw": ["bmw", "mini"],
            "mercedes": ["mercedes", "maybach", "smart"]
        }
        
        make1_lower = make1.lower()
        make2_lower = make2.lower()
        
        for family, brands in families.items():
            if make1_lower in brands and make2_lower in brands:
                return True
        
        return False
    
    def _is_similar_model(self, model1: str, model2: str) -> bool:
        """Check if models are similar (same series or category)"""
        model1_lower = model1.lower()
        model2_lower = model2.lower()
        
        # Common model series
        series_patterns = [
            ("corolla", ["corolla", "corolla altis", "corolla fielder"]),
            ("civic", ["civic", "civic sedan", "civic hatchback"]),
            ("accord", ["accord", "accord sedan"]),
            ("camry", ["camry", "camry hybrid"]),
            ("elantra", ["elantra", "elantra sport"]),
            ("rio", ["rio", "rio sedan"]),
        ]
        
        for base, variants in series_patterns:
            if any(variant in model1_lower for variant in variants) and \
               any(variant in model2_lower for variant in variants):
                return True
        
        return False
    
    def _is_adjacent_region(self, region1: str, region2: str) -> bool:
        """Check if regions are adjacent in Ethiopia"""
        region1_lower = region1.lower()
        region2_lower = region2.lower()
        
        # Ethiopian regional adjacencies (simplified)
        adjacencies = {
            "addis ababa": ["oromia", "amhara"],
            "oromia": ["addis ababa", "amhara", "southern", "somali"],
            "amhara": ["addis ababa", "oromia", "tigray", "southern"],
            "tigray": ["amhara", "afar"],
            "afar": ["tigray", "amhara", "somali"],
            "somali": ["afar", "oromia", "southern"],
            "southern": ["oromia", "amhara", "somali", "gambela"]
        }
        
        for region, adjacent in adjacencies.items():
            if region in region1_lower and any(adj in region2_lower for adj in adjacent):
                return True
            if region in region2_lower and any(adj in region1_lower for adj in adjacent):
                return True
        
        return False
    
    def _analyze_market_data(self, comparable_vehicles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze market data from comparable vehicles"""
        # Filter vehicles with market values
        priced_vehicles = [v for v in comparable_vehicles if v.get("market_value")]
        
        if not priced_vehicles:
            return {
                "sample_size": 0,
                "price_range": {"min": 0, "max": 0, "avg": 0},
                "market_trend": "insufficient_data"
            }
        
        prices = [v["market_value"] for v in priced_vehicles]
        
        # Calculate price statistics
        price_stats = {
            "min": min(prices),
            "max": max(prices),
            "avg": statistics.mean(prices),
            "median": statistics.median(prices)
        }
        
        # Calculate price distribution
        price_ranges = {
            "low_end": price_stats["min"],
            "mid_range": price_stats["median"],
            "high_end": price_stats["max"]
        }
        
        # Market trend based on valuation dates
        recent_valuations = []
        for vehicle in priced_vehicles:
            if vehicle.get("valuation_date"):
                try:
                    valuation_date = datetime.fromisoformat(vehicle["valuation_date"])
                    recent_valuations.append((valuation_date, vehicle["market_value"]))
                except ValueError:
                    continue
        
        market_trend = "stable"
        if len(recent_valuations) >= 3:
            recent_valuations.sort(key=lambda x: x[0])
            first_half = recent_valuations[:len(recent_valuations)//2]
            second_half = recent_valuations[len(recent_valuations)//2:]
            
            first_avg = statistics.mean([price for _, price in first_half])
            second_avg = statistics.mean([price for _, price in second_half])
            
            if second_avg > first_avg * 1.05:
                market_trend = "increasing"
            elif second_avg < first_avg * 0.95:
                market_trend = "decreasing"
        
        return {
            "sample_size": len(priced_vehicles),
            "price_range": price_stats,
            "price_distribution": price_ranges,
            "market_trend": market_trend,
            "data_quality": "good" if len(priced_vehicles) >= 5 else "limited"
        }
    
    def _analyze_price_positioning(
        self,
        target_vehicle: Vehicle,
        comparable_vehicles: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze price positioning relative to market"""
        priced_vehicles = [v for v in comparable_vehicles if v.get("market_value")]
        
        if not priced_vehicles:
            return {
                "position": "unknown",
                "percentile": 0.5,
                "recommendation": "insufficient_data"
            }
        
        prices = [v["market_value"] for v in priced_vehicles]
        avg_price = statistics.mean(prices)
        median_price = statistics.median(prices)
        
        # Determine positioning (would need target vehicle's estimated price)
        # For now, provide market context
        return {
            "market_average": round(avg_price, 2),
            "market_median": round(median_price, 2),
            "price_range": {"min": min(prices), "max": max(prices)},
            "competitor_count": len(priced_vehicles),
            "market_maturity": "established" if len(priced_vehicles) >= 10 else "developing"
        }
    
    def _generate_recommendations(
        self,
        target_vehicle: Vehicle,
        comparable_vehicles: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate market-based recommendations"""
        recommendations = []
        
        if not comparable_vehicles:
            return ["Limited market data available - consider expanding search criteria"]
        
        # Analyze market saturation
        if len(comparable_vehicles) > 50:
            recommendations.append("High market saturation - consider competitive pricing")
        elif len(comparable_vehicles) < 5:
            recommendations.append("Low market saturation - opportunity for premium pricing")
        
        # Analyze regional competition
        regional_vehicles = [
            v for v in comparable_vehicles 
            if v.get("region") and target_vehicle.region and 
            v["region"].lower() == target_vehicle.region.lower()
        ]
        
        if len(regional_vehicles) > 10:
            recommendations.append("Strong regional competition - emphasize unique features")
        elif len(regional_vehicles) < 3:
            recommendations.append("Limited regional competition - favorable market position")
        
        # Analyze pricing strategy
        priced_vehicles = [v for v in comparable_vehicles if v.get("market_value")]
        if priced_vehicles:
            avg_price = statistics.mean([v["market_value"] for v in priced_vehicles])
            
            if target_vehicle.year > datetime.now().year - 2:
                recommendations.append("Recent model year - can command premium pricing")
            elif target_vehicle.year < datetime.now().year - 10:
                recommendations.append("Older model year - competitive pricing recommended")
        
        return recommendations
    
    def _fallback_comparison(self, target_vehicle: Vehicle) -> Dict[str, Any]:
        """Fallback comparison when main analysis fails"""
        return {
            "target_vehicle": {
                "id": str(target_vehicle.id),
                "make": target_vehicle.make,
                "model": target_vehicle.model,
                "year": target_vehicle.year
            },
            "comparable_vehicles": [],
            "market_analysis": {
                "sample_size": 0,
                "price_range": {"min": 0, "max": 0, "avg": 0},
                "market_trend": "insufficient_data"
            },
            "price_positioning": {
                "position": "unknown",
                "percentile": 0.5
            },
            "recommendations": [
                "Market comparison unavailable - using standard valuation methods"
            ]
        }
