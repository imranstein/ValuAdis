"""
Users Module

Owns /api/v1/users: user CRUD, role and permission assignment.
"""

from .routes import router as users_router

__all__ = ["users_router"]
