"""
Vehicle Data Service

Integration with NHTSA vPIC API for vehicle data retrieval
including makes, models, years, and VIN decoding.
"""

import httpx
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import asyncio
from functools import lru_cache

logger = logging.getLogger(__name__)

FALLBACK_MAKES = [
    "Toyota",
    "Nissan",
    "Hyundai",
    "Suzuki",
    "Isuzu",
    "Mitsubishi",
    "Honda",
    "Mercedes-Benz",
    "Kia",
    "Ford",
]

FALLBACK_MODELS = {
    "toyota": ["Corolla", "Vitz", "Yaris", "RAV4", "Hilux", "Land Cruiser"],
    "nissan": ["Sunny", "Patrol", "X-Trail", "Navara", "Qashqai"],
    "hyundai": ["Accent", "Elantra", "Tucson", "Santa Fe", "H-1"],
    "suzuki": ["Swift", "Vitara", "Dzire", "Jimny"],
    "isuzu": ["D-Max", "NPR", "NQR"],
    "mitsubishi": ["L200", "Pajero", "Outlander", "Attrage"],
    "honda": ["Civic", "Fit", "CR-V", "Accord"],
    "mercedes-benz": ["C-Class", "E-Class", "Sprinter", "Actros"],
    "kia": ["Picanto", "Sportage", "Sorento", "Rio"],
    "ford": ["Ranger", "Escape", "Transit", "Focus"],
}

class VehicleDataService:
    """Service for fetching vehicle data from NHTSA vPIC API"""
    
    def __init__(self):
        self.base_url = "https://vpic.nhtsa.dot.gov/api"
        self.cache_timeout = 3600  # 1 hour cache
        self._cache = {}
        
    async def get_all_makes(self) -> List[str]:
        """Get all vehicle makes from NHTSA API"""
        cache_key = "all_makes"
        
        if self._is_cache_valid(cache_key):
            return self._cache[cache_key]["data"]
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(f"{self.base_url}/vehicles/getallmakes")
                response.raise_for_status()
                
                data = response.json()
                makes = [result["Make_Name"] for result in data.get("Results", [])]
                
                # Cache the results
                self._cache[cache_key] = {
                    "data": makes,
                    "timestamp": datetime.utcnow()
                }
                
                logger.info(f"Fetched {len(makes)} vehicle makes from NHTSA API")
                return makes
                
        except Exception as e:
            logger.error(f"Failed to fetch vehicle makes: {e}")
            return FALLBACK_MAKES
    
    async def get_models_for_make(self, make: str) -> List[str]:
        """Get all models for a specific make"""
        cache_key = f"models_{make.lower()}"
        
        if self._is_cache_valid(cache_key):
            return self._cache[cache_key]["data"]
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(f"{self.base_url}/vehicles/getmodelsformake/{make}")
                response.raise_for_status()
                
                data = response.json()
                models = [result["Model_Name"] for result in data.get("Results", [])]
                
                # Remove duplicates and sort
                models = sorted(list(set(models)))
                
                # Cache the results
                self._cache[cache_key] = {
                    "data": models,
                    "timestamp": datetime.utcnow()
                }
                
                logger.info(f"Fetched {len(models)} models for {make} from NHTSA API")
                return models
                
        except Exception as e:
            logger.error(f"Failed to fetch models for {make}: {e}")
            return FALLBACK_MODELS.get(make.lower(), [])
    
    async def decode_vin(self, vin: str) -> Dict[str, Any]:
        """Decode VIN to get vehicle specifications"""
        cache_key = f"vin_{vin}"
        
        if self._is_cache_valid(cache_key):
            return self._cache[cache_key]["data"]
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(f"{self.base_url}/vehicles/decodevinvalues/{vin}")
                response.raise_for_status()
                
                data = response.json()
                results = data.get("Results", [])
                
                # Convert results to key-value pairs
                decoded_data = {}
                for result in results:
                    if result.get("Value") and result.get("Value") != "":
                        decoded_data[result["Variable"]] = result["Value"]
                
                # Cache the results
                self._cache[cache_key] = {
                    "data": decoded_data,
                    "timestamp": datetime.utcnow()
                }
                
                logger.info(f"Successfully decoded VIN: {vin}")
                return decoded_data
                
        except Exception as e:
            logger.error(f"Failed to decode VIN {vin}: {e}")
            return {}
    
    async def get_vehicle_types_for_make(self, make: str) -> List[str]:
        """Get vehicle types for a specific make"""
        cache_key = f"types_{make.lower()}"
        
        if self._is_cache_valid(cache_key):
            return self._cache[cache_key]["data"]
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(f"{self.base_url}/vehicles/GetVehicleTypesForMakes/{make}")
                response.raise_for_status()
                
                data = response.json()
                vehicle_types = [result["VehicleTypeName"] for result in data.get("Results", [])]
                
                # Remove duplicates and sort
                vehicle_types = sorted(list(set(vehicle_types)))
                
                # Cache the results
                self._cache[cache_key] = {
                    "data": vehicle_types,
                    "timestamp": datetime.utcnow()
                }
                
                logger.info(f"Fetched {len(vehicle_types)} vehicle types for {make}")
                return vehicle_types
                
        except Exception as e:
            logger.error(f"Failed to fetch vehicle types for {make}: {e}")
            return []
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached data is still valid"""
        if cache_key not in self._cache:
            return False
        
        cache_entry = self._cache[cache_key]
        timestamp = cache_entry["timestamp"]
        
        # Check if cache is still valid (1 hour)
        return (datetime.utcnow() - timestamp).total_seconds() < self.cache_timeout
    
    def clear_cache(self):
        """Clear all cached data"""
        self._cache.clear()
        logger.info("Vehicle data cache cleared")
    
    def get_cache_info(self) -> Dict[str, Any]:
        """Get cache information for monitoring"""
        cache_info = {
            "total_entries": len(self._cache),
            "entries": {}
        }
        
        for key, entry in self._cache.items():
            age_seconds = (datetime.utcnow() - entry["timestamp"]).total_seconds()
            cache_info["entries"][key] = {
                "age_seconds": age_seconds,
                "data_size": len(str(entry["data"])),
                "is_valid": age_seconds < self.cache_timeout
            }
        
        return cache_info

# Singleton instance
vehicle_data_service = VehicleDataService()
