"""
Auth Module

Owns /api/v1/auth: register, login, refresh (bearer + httpOnly cookie),
logout, and current-user. The cross-cutting AuthService and security
primitives stay in app/services and app/core because every module's routes
depend on them.
"""

from .routes import router as auth_router

__all__ = ["auth_router"]
