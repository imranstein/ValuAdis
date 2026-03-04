"""
Vehicle Valuation Module

Handles vehicle valuation operations including:
- Vehicle data collection and validation
- Market value calculation using AI
- Ethiopian vehicle market integration
- Certificate generation for vehicle valuations
"""

from .routes import router as vehicle_router
from .services import VehicleValuationService
from .models import Vehicle, VehicleValuation
from .repositories import VehicleRepository, VehicleValuationRepository

__all__ = [
    "vehicle_router",
    "VehicleValuationService",
    "Vehicle",
    "VehicleValuation",
    "VehicleRepository",
    "VehicleValuationRepository",
]
