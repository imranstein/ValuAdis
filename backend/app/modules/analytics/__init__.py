"""
Analytics Module

Owns /api/v1/analytics: dashboards, property/valuation distributions,
municipality exposure, and market insights (backed by the shared ml_service).
"""

from .routes import router as analytics_router

__all__ = ["analytics_router"]
