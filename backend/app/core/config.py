"""
ValuAdis Configuration Settings

Environment variables and application settings for Ethiopian Property Valuation Platform
"""

from pydantic_settings import BaseSettings
from typing import List, Optional
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "ValuAdis API"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    
    # Database (PostgreSQL + PostGIS)
    DATABASE_URL: str = "postgresql://valuadis_user:valuadis_2025@localhost:5432/valuadis"
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "valuadis"
    DB_USER: str = "valuadis"
    DB_PASSWORD: str = "password"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: Optional[str] = None
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS
    ALLOWED_HOSTS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
        "http://localhost:3003",
        "http://localhost:3020",
        "http://127.0.0.1:3020",
        "http://localhost:5173",
        "*"  # Temporary: Allow all origins for debugging
    ]
    
    # M-Pesa Ethiopia
    MPESA_CONSUMER_KEY: str = ""
    MPESA_CONSUMER_SECRET: str = ""
    MPESA_SHORTCODE: str = ""
    MPESA_PASSKEY: str = ""
    MPESA_ENVIRONMENT: str = "sandbox"  # sandbox or production
    
    # File Storage
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: List[str] = [".jpg", ".jpeg", ".png", ".pdf"]
    
    # Monitoring
    SENTRY_DSN: Optional[str] = None
    
    # Ethiopian Compliance
    DATA_SOVEREIGNTY_REQUIRED: bool = True
    PROCLAMATION_COMPLIANCE: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


# Create settings instance
settings = Settings()

# Validate critical settings
if settings.ENVIRONMENT == "production":
    if not settings.SECRET_KEY or settings.SECRET_KEY == "your-secret-key-change-in-production":
        raise ValueError("SECRET_KEY must be set in production")
    
    if not settings.DATABASE_URL or "localhost" in settings.DATABASE_URL:
        raise ValueError("DATABASE_URL must be set to production database")
    
    if "*" in settings.ALLOWED_HOSTS:
        raise ValueError("ALLOWED_HOSTS cannot contain wildcard '*' in production")
    
    if not settings.DATA_SOVEREIGNTY_REQUIRED:
        raise ValueError("Data sovereignty is required for Ethiopian compliance")
