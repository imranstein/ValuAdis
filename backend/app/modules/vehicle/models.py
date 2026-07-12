"""
Vehicle models for module-level imports.

Re-exports the centralized SQLAlchemy models from app.data.models so the
module has a single metadata registration and no duplicated model classes.
"""

from app.data.models.vehicle import Vehicle
from app.data.models.vehicle_valuation import VehicleValuation, VehicleValuationStatus

__all__ = ["Vehicle", "VehicleValuation", "VehicleValuationStatus"]
