"""
Property Module Models

The SQLAlchemy model remains registered in app.data.models (shared metadata,
Alembic migrations, and spatial regression coverage live there). This module
re-exports it as the property module's model surface.
"""

from app.data.models.property import Property
from app.data.models.property_photo import PropertyPhoto

__all__ = ["Property", "PropertyPhoto"]
