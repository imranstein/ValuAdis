"""
ValuAdis Audit API Schemas

Pydantic schemas for audit report API validation and serialization
Supports Ethiopian compliance reporting and system monitoring
"""

from pydantic import BaseModel, Field, validator
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum


class ReportType(str, Enum):
    """Supported audit report types"""
    SYSTEM = "system"
    COMPLIANCE = "compliance"
    SUMMARY = "summary"


class ScheduleType(str, Enum):
    """Supported schedule types"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"


class DateRangeQuery(BaseModel):
    """Date range query parameters"""
    start_date: Optional[datetime] = Field(None, description="Report start date")
    end_date: Optional[datetime] = Field(None, description="Report end date")
    days_back: Optional[int] = Field(30, description="Days back from end date")
    
    @validator('days_back')
    def validate_days_back(cls, v):
        if v is not None and v <= 0:
            raise ValueError('days_back must be positive')
        return v


class EthiopianComplianceMetrics(BaseModel):
    """Ethiopian compliance metrics schema"""
    total_valuations: int = Field(..., description="Total valuations analyzed")
    compliant_valuations: int = Field(..., description="Compliant valuations count")
    non_compliant_valuations: int = Field(..., description="Non-compliant valuations count")
    compliance_rate: float = Field(..., description="Compliance percentage")
    rule: str = Field(..., description="Compliance rule description")


class MunicipalityCompliance(BaseModel):
    """Municipality compliance analysis"""
    municipality: str = Field(..., description="Municipality name")
    total_valuations: int = Field(..., description="Total valuations in municipality")
    compliant_valuations: int = Field(..., description="Compliant valuations count")
    compliance_rate: float = Field(..., description="Compliance percentage")


class PropertyTypeCompliance(BaseModel):
    """Property type compliance analysis"""
    property_type: str = Field(..., description="Property type")
    total_valuations: int = Field(..., description="Total valuations of this type")
    compliant_valuations: int = Field(..., description="Compliant valuations count")
    compliance_rate: float = Field(..., description="Compliance percentage")


class ComplianceViolation(BaseModel):
    """Individual compliance violation details"""
    valuation_id: int = Field(..., description="Valuation ID")
    property_type: str = Field(..., description="Property type")
    municipality: str = Field(..., description="Municipality")
    market_value: float = Field(..., description="Market value in ETB")
    taxable_value: float = Field(..., description="Taxable value in ETB")
    expected_taxable: float = Field(..., description="Expected taxable value")
    deviation: float = Field(..., description="Deviation from expected")
    created_at: Optional[str] = Field(None, description="Creation timestamp")


class EthiopianComplianceReport(BaseModel):
    """Complete Ethiopian compliance report"""
    total_valuations_analyzed: int = Field(..., description="Total valuations analyzed")
    proclamation_1365_2025_compliance: EthiopianComplianceMetrics = Field(...)
    municipality_analysis: Dict[str, Dict[str, Any]] = Field(...)
    property_type_analysis: Dict[str, Dict[str, Any]] = Field(...)
    compliance_details: List[ComplianceViolation] = Field(...)


class SystemOverview(BaseModel):
    """System overview statistics"""
    total_entities: Dict[str, int] = Field(..., description="Total counts by entity type")
    property_status_distribution: Dict[str, int] = Field(..., description="Property status distribution")
    valuation_status_distribution: Dict[str, int] = Field(..., description="Valuation status distribution")
    municipality_distribution: Dict[str, int] = Field(..., description="Municipality distribution")


class UserActivityMetrics(BaseModel):
    """User activity statistics"""
    new_users: int = Field(..., description="New users in period")
    active_users: int = Field(..., description="Active users in period")
    user_municipality_distribution: Dict[str, int] = Field(..., description="User municipality distribution")
    top_users_by_valuations: List[Dict[str, Any]] = Field(..., description="Top users by valuation count")


class ValuationMetrics(BaseModel):
    """Valuation performance metrics"""
    total_valuations: int = Field(..., description="Total valuations in period")
    financial_metrics: Dict[str, Any] = Field(..., description="Financial summary")
    valuations_by_type: List[Dict[str, Any]] = Field(..., description="Valuations by property type")
    valuations_by_municipality: List[Dict[str, Any]] = Field(..., description="Valuations by municipality")
    daily_trends: List[Dict[str, Any]] = Field(..., description="Daily valuation trends")


class PerformanceMetrics(BaseModel):
    """System performance metrics"""
    database_performance: Dict[str, str] = Field(..., description="Database performance indicators")
    api_performance: Dict[str, str] = Field(..., description="API performance metrics")
    system_resources: Dict[str, str] = Field(..., description="System resource usage")
    overall_health: str = Field(..., description="Overall health status")


class DataIntegrityReport(BaseModel):
    """Data integrity validation report"""
    referential_integrity: Dict[str, Any] = Field(..., description="Referential integrity check")
    data_consistency: Dict[str, Any] = Field(..., description="Data consistency validation")
    duplicate_data: Dict[str, Any] = Field(..., description="Duplicate data analysis")


class SecurityAuditReport(BaseModel):
    """Security audit report"""
    user_authentication: Dict[str, Any] = Field(..., description="User authentication metrics")
    access_patterns: List[Dict[str, Any]] = Field(..., description="Access pattern analysis")
    security_compliance: Dict[str, str] = Field(..., description="Security compliance status")
    overall_security_status: str = Field(..., description="Overall security status")


class ReportMetadata(BaseModel):
    """Report metadata"""
    report_type: str = Field(..., description="Report type")
    generated_at: str = Field(..., description="Generation timestamp")
    period: Optional[Dict[str, str]] = Field(None, description="Report period")
    compliance_standard: Optional[str] = Field(None, description="Compliance standard")


class SystemAuditReport(BaseModel):
    """Complete system audit report"""
    report_metadata: ReportMetadata = Field(..., description="Report metadata")
    system_overview: SystemOverview = Field(..., description="System overview")
    user_activity: UserActivityMetrics = Field(..., description="User activity metrics")
    valuation_metrics: ValuationMetrics = Field(..., description="Valuation metrics")
    ethiopian_compliance: Dict[str, Any] = Field(..., description="Ethiopian compliance analysis")
    performance_metrics: PerformanceMetrics = Field(..., description="Performance metrics")
    data_integrity: DataIntegrityReport = Field(..., description="Data integrity report")
    security_audit: SecurityAuditReport = Field(..., description="Security audit report")


class SummaryMetrics(BaseModel):
    """Summary dashboard metrics"""
    total_users: int = Field(..., description="Total users")
    total_properties: int = Field(..., description="Total properties")
    total_valuations: int = Field(..., description="Total valuations")
    recent_valuations_7_days: int = Field(..., description="Recent valuations (7 days)")
    ethiopian_compliance_rate: float = Field(..., description="Ethiopian compliance rate")


class SummaryReport(BaseModel):
    """Summary report for dashboard"""
    summary: SummaryMetrics = Field(..., description="Summary metrics")
    generated_at: str = Field(..., description="Generation timestamp")


# Response schemas


class AuditReportResponse(BaseModel):
    """System audit report response"""
    success: bool = Field(..., description="Operation success status")
    report: SystemAuditReport = Field(..., description="Complete audit report")
    metadata: Dict[str, Any] = Field(..., description="Response metadata")


class ComplianceReportResponse(BaseModel):
    """Ethiopian compliance report response"""
    success: bool = Field(..., description="Operation success status")
    compliance_report: EthiopianComplianceReport = Field(..., description="Compliance report")
    metadata: Dict[str, Any] = Field(..., description="Response metadata")


class SummaryReportResponse(BaseModel):
    """Summary report response"""
    success: bool = Field(..., description="Operation success status")
    summary: SummaryReport = Field(..., description="Summary metrics")
    metadata: Dict[str, Any] = Field(..., description="Response metadata")


class ExportReportResponse(BaseModel):
    """Export report response"""
    success: bool = Field(..., description="Export success status")
    message: str = Field(..., description="Export message")
    filename: str = Field(..., description="Exported filename")
    download_url: str = Field(..., description="Download URL")
    metadata: Dict[str, Any] = Field(..., description="Export metadata")


class HealthCheckResponse(BaseModel):
    """Audit system health check response"""
    success: bool = Field(..., description="Health check success")
    health: Dict[str, Any] = Field(..., description="Health status details")


class MetricsResponse(BaseModel):
    """Audit metrics response"""
    success: bool = Field(..., description="Metrics retrieval success")
    metric_type: str = Field(..., description="Type of metrics returned")
    metrics: Dict[str, Any] = Field(..., description="Metrics data")
    generated_at: str = Field(..., description="Generation timestamp")


class ScheduleReportRequest(BaseModel):
    """Schedule audit report request"""
    report_type: ReportType = Field(..., description="Type of report to schedule")
    schedule: str = Field(..., description="Schedule expression")
    recipients: List[str] = Field(..., description="Email recipients")
    start_date: Optional[datetime] = Field(None, description="Report start date")
    end_date: Optional[datetime] = Field(None, description="Report end date")
    
    @validator('recipients')
    def validate_recipients(cls, v):
        if not v:
            raise ValueError('At least one recipient must be specified')
        
        # Basic email validation
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        for email in v:
            if not re.match(email_pattern, email):
                raise ValueError(f'Invalid email format: {email}')
        
        return v
    
    @validator('schedule')
    def validate_schedule(cls, v):
        valid_schedules = ["daily", "weekly", "monthly"]
        if v not in valid_schedules and not v.startswith("cron:"):
            raise ValueError(f'Invalid schedule: {v}. Use {valid_schedules} or cron:expression')
        return v


class ScheduleReportResponse(BaseModel):
    """Schedule report response"""
    success: bool = Field(..., description="Scheduling success status")
    message: str = Field(..., description="Scheduling message")
    schedule_details: Dict[str, Any] = Field(..., description="Schedule configuration")
    metadata: Dict[str, Any] = Field(..., description="Scheduling metadata")


# Request schemas


class AuditReportRequest(BaseModel):
    """Audit report generation request"""
    report_type: ReportType = Field(..., description="Type of report to generate")
    date_range: Optional[DateRangeQuery] = Field(None, description="Date range for report")
    format: str = Field("json", description="Report format")
    
    @validator('format')
    def validate_format(cls, v):
        if v.lower() not in ["json", "csv", "pdf"]:
            raise ValueError('Format must be json, csv, or pdf')
        return v.lower()


class ComplianceReportRequest(BaseModel):
    """Ethiopian compliance report request"""
    include_violations: bool = Field(True, description="Include compliance violations")
    municipality_filter: Optional[List[str]] = Field(None, description="Filter by municipalities")
    property_type_filter: Optional[List[str]] = Field(None, description="Filter by property types")
    
    @validator('municipality_filter')
    def validate_municipalities(cls, v):
        if v:
            valid_municipalities = [
                "Addis Ababa", "Dire Dawa", "Mekelle", 
                "Bahirdar", "Gondar", "Hawassa"
            ]
            for mun in v:
                if mun not in valid_municipalities:
                    raise ValueError(f'Invalid municipality: {mun}. Valid: {valid_municipalities}')
        return v
    
    @validator('property_type_filter')
    def validate_property_types(cls, v):
        if v:
            valid_types = ["residential", "commercial", "agricultural"]
            for prop_type in v:
                if prop_type not in valid_types:
                    raise ValueError(f'Invalid property type: {prop_type}. Valid: {valid_types}')
        return v


# Utility schemas


class ErrorResponse(BaseModel):
    """Standard error response"""
    success: bool = Field(False, description="Operation success status")
    error: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Error details")
    timestamp: str = Field(..., description="Error timestamp")


class SuccessResponse(BaseModel):
    """Standard success response"""
    success: bool = Field(True, description="Operation success status")
    message: str = Field(..., description="Success message")
    data: Optional[Dict[str, Any]] = Field(None, description="Response data")
    timestamp: str = Field(..., description="Response timestamp")
