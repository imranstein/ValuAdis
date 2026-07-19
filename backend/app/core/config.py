"""
ValuAdis Configuration Settings

Environment variables and application settings for Ethiopian Property Valuation Platform
"""

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional, Union

PLACEHOLDER_MARKERS = (
    "changeme",
    "change_this",
    "your-",
    "your_",
    "placeholder",
    "replace_with",
)


def has_placeholder(value: Optional[str]) -> bool:
    if not value:
        return False
    normalized = value.strip().lower()
    return any(marker in normalized for marker in PLACEHOLDER_MARKERS)


class Settings(BaseSettings):
    """Application settings"""
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
        enable_decoding=False,
    )
    
    # Application
    APP_NAME: str = "ValuAdis API"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    
    # Database (SQLite for testing, can be changed to PostgreSQL/SQL Server)
    DATABASE_URL: str = "sqlite:///./valuadis.db"
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "valuadis"
    DB_USER: str = "valuadis"
    DB_PASSWORD: str = "password"
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 40
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE_SECONDS: int = 300
    
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
    ALLOWED_HOSTS: Union[List[str], str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
        "http://localhost:3003",
        "http://localhost:3020",
        "http://127.0.0.1:3020",
        "http://localhost:3021",
        "http://127.0.0.1:3021",
        "http://localhost:5173",
    ]

    @field_validator("ALLOWED_HOSTS", mode="before")
    @classmethod
    def parse_allowed_hosts(cls, value):
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value
    
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

    # Property photo storage root. Photos are written to
    # <MEDIA_ROOT>/property_photos/<property_id>/<server-generated-filename>.
    # Relative paths resolve against the backend process's working directory
    # (backend/ when run per CLAUDE.md's documented commands).
    MEDIA_ROOT: str = "media"
    
    # Monitoring
    SENTRY_DSN: Optional[str] = None
    
    # Ethiopian Compliance
    DATA_SOVEREIGNTY_REQUIRED: bool = True
    PROCLAMATION_COMPLIANCE: bool = True


def validate_production_settings(settings: Settings) -> None:
    if settings.ENVIRONMENT != "production":
        return

    if (
        not settings.SECRET_KEY
        or has_placeholder(settings.SECRET_KEY)
        or len(settings.SECRET_KEY) < 32
    ):
        raise ValueError("SECRET_KEY must be set to a strong production secret")

    if (
        not settings.DATABASE_URL
        or settings.DATABASE_URL.startswith("sqlite")
        or "localhost" in settings.DATABASE_URL
        or "127.0.0.1" in settings.DATABASE_URL
        or has_placeholder(settings.DATABASE_URL)
    ):
        raise ValueError("DATABASE_URL must be set to production database")

    if not settings.ALLOWED_HOSTS:
        raise ValueError("ALLOWED_HOSTS must be set in production")

    unsafe_hosts = {"*", "http://localhost", "https://localhost"}
    if any(
        host in unsafe_hosts
        or "localhost" in host
        or "127.0.0.1" in host
        or not host.startswith("https://")
        or has_placeholder(host)
        for host in settings.ALLOWED_HOSTS
    ):
        raise ValueError("ALLOWED_HOSTS must contain only deployed production origins")

    if (
        not settings.REDIS_URL
        or "localhost" in settings.REDIS_URL
        or "127.0.0.1" in settings.REDIS_URL
        or has_placeholder(settings.REDIS_URL)
    ):
        raise ValueError("REDIS_URL must be set to production Redis")

    if not settings.DATA_SOVEREIGNTY_REQUIRED:
        raise ValueError("Data sovereignty is required for Ethiopian compliance")
    

# Create settings instance
settings = Settings()

validate_production_settings(settings)
