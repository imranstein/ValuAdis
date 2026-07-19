"""
Property Module

Single owner of the property stack: /api/v1/properties routes, request/response
schemas, business logic, and the PostGIS-backed repository. The SQLAlchemy
model stays in app.data.models (re-exported via .models); the shapely/pyproj
SpatialService stays in app.services.spatial_service because it is shared with
valuations.
"""

from .routes import router as property_router
from .services import PropertyService
from .repositories import PropertyRepository
from .models import Property

__all__ = [
    "property_router",
    "PropertyService",
    "PropertyRepository",
    "Property",
]
