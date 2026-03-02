"""
ValuAdis Custom Exceptions

Custom exception classes for the Ethiopian Property Valuation Platform
"""


class ValuAdisException(Exception):
    """Base exception for ValuAdis platform"""
    pass


class AuthenticationException(ValuAdisException):
    """Authentication related exceptions"""
    pass


class AuthorizationException(ValuAdisException):
    """Authorization related exceptions"""
    pass


class ValidationException(ValuAdisException):
    """Data validation exceptions"""
    pass


class PropertyValidationError(ValidationException):
    """Property-specific validation exceptions"""
    pass


class DatabaseException(ValuAdisException):
    """Database operation exceptions"""
    pass


class ExternalServiceException(ValuAdisException):
    """External service integration exceptions"""
    pass


class MpesaException(ExternalServiceException):
    """M-Pesa payment service exceptions"""
    pass


class ComplianceException(ValuAdisException):
    """Proclamation 1365/2025 compliance exceptions"""
    pass


class DataSovereigntyException(ValuAdisException):
    """Data sovereignty violations"""
    pass


class SpatialOperationException(ValuAdisException):
    """PostGIS spatial operation exceptions"""
    pass


class FileOperationException(ValuAdisException):
    """File upload/download exceptions"""
    pass


class CacheException(ValuAdisException):
    """Redis cache operation exceptions"""
    pass
