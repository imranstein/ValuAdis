from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime
from app.core.scraper_limits import (
    SCRAPER_CREATE_DEFAULT_PAGES,
    SCRAPER_CREATE_MAX_PAGES,
    SCRAPER_RUN_SCHEMA_MAX_PAGES,
    SCRAPER_RUN_SCHEMA_MAX_TARGET_ITEMS,
)


class ScraperSelectorsSchema(BaseModel):
    """Schema for CSS selectors configuration"""
    title: str = Field(..., description="CSS selector for property title")
    price: str = Field(..., description="CSS selector for property price")
    location: str = Field(..., description="CSS selector for property location")
    area: Optional[str] = Field(None, description="CSS selector for property area")
    property_type: Optional[str] = Field(None, description="CSS selector for property type")
    bedrooms: Optional[str] = Field(None, description="CSS selector for bedrooms")
    bathrooms: Optional[str] = Field(None, description="CSS selector for bathrooms")
    listing_url: str = Field(..., description="CSS selector for listing URL")


class ScraperTargetCreate(BaseModel):
    """Schema for creating a new scraper target"""
    domain: str = Field(..., min_length=3, max_length=255, description="Domain name (e.g., livingethio.com)")
    url_template: str = Field(..., min_length=10, max_length=500, description="URL template with {page} placeholder")
    enabled: bool = Field(default=True, description="Whether scraper is enabled")
    selectors: Dict[str, Any] = Field(..., description="CSS selectors configuration")
    schedule: str = Field(default="daily", description="Scraping schedule (daily, weekly, custom)")
    max_pages: int = Field(
        default=SCRAPER_CREATE_DEFAULT_PAGES,
        ge=1,
        le=SCRAPER_CREATE_MAX_PAGES,
        description="Maximum pages to scrape"
    )

    @field_validator("url_template")
    @classmethod
    def validate_url_template(cls, v):
        if '{page}' not in v:
            raise ValueError('URL template must contain {page} placeholder')
        return v

    @field_validator("schedule")
    @classmethod
    def validate_schedule(cls, v):
        valid_schedules = ['daily', 'weekly', 'custom', 'manual']
        if v not in valid_schedules:
            raise ValueError(f'Schedule must be one of: {", ".join(valid_schedules)}')
        return v


class ScraperTargetUpdate(BaseModel):
    """Schema for updating a scraper target"""
    domain: Optional[str] = Field(None, min_length=3, max_length=255)
    url_template: Optional[str] = Field(None, min_length=10, max_length=500)
    enabled: Optional[bool] = None
    selectors: Optional[Dict[str, Any]] = None
    schedule: Optional[str] = None
    max_pages: Optional[int] = Field(None, ge=1, le=SCRAPER_CREATE_MAX_PAGES)

    @field_validator("url_template")
    @classmethod
    def validate_url_template(cls, v):
        if v and '{page}' not in v:
            raise ValueError('URL template must contain {page} placeholder')
        return v

    @field_validator("schedule")
    @classmethod
    def validate_schedule(cls, v):
        if v:
            valid_schedules = ['daily', 'weekly', 'custom', 'manual']
            if v not in valid_schedules:
                raise ValueError(f'Schedule must be one of: {", ".join(valid_schedules)}')
        return v


class ScraperTargetResponse(BaseModel):
    """Schema for scraper target response"""
    id: int
    domain: str
    url_template: str
    enabled: bool
    selectors: Dict[str, Any]
    schedule: str
    max_pages: int
    last_run: Optional[datetime]
    last_status: Optional[str]
    total_listings: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class ScraperLogResponse(BaseModel):
    """Schema for scraper log response"""
    id: int
    scraper_id: int
    started_at: datetime
    completed_at: Optional[datetime]
    status: Optional[str]
    listings_found: int
    listings_saved: int
    error_message: Optional[str]
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class ScraperStatsResponse(BaseModel):
    """Schema for scraper statistics"""
    total_scrapers: int
    active_scrapers: int
    inactive_scrapers: int
    total_listings: int
    last_24h_listings: int
    last_run: Optional[datetime]
    avg_success_rate: float


class ScraperHealthResponse(BaseModel):
    """Per-source operational health for the scraper ops desk"""
    id: int
    domain: str
    enabled: bool
    last_run: Optional[datetime]
    last_status: Optional[str]
    consecutive_failures: int
    total_listings: int
    last_error_message: Optional[str]


class ScraperTestRequest(BaseModel):
    """Schema for testing scraper configuration"""
    url_template: str
    selectors: Dict[str, Any]
    test_page: int = Field(default=1, ge=1, description="Page number to test")


class ScraperTestResponse(BaseModel):
    """Schema for scraper test results"""
    success: bool
    items_found: int
    sample_items: list
    error_message: Optional[str]


class ScraperRunRequest(BaseModel):
    """Schema for manual scraper run"""
    max_pages: Optional[int] = Field(None, ge=1, le=SCRAPER_RUN_SCHEMA_MAX_PAGES)
    target_items: Optional[int] = Field(None, ge=1, le=SCRAPER_RUN_SCHEMA_MAX_TARGET_ITEMS)
