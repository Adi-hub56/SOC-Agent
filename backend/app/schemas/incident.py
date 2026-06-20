from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum
from typing import Optional

# Enums for validation
class EventType(str, Enum):
    FAILED_SSH_LOGIN = "failed_ssh_login"
    MALWARE_DETECTED = "malware_detected"
    SQL_INJECTION = "sql_injection"
    XSS_ATTACK = "xss_attack"
    DDoS = "ddos"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    DATA_EXFILTRATION = "data_exfiltration"
    OTHER = "other"

class Severity(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"

# Request Models
class AlertRequest(BaseModel):
    event_id: str = Field(..., min_length=1, max_length=100, description="Unique event identifier")
    event_type: EventType = Field(..., description="Type of security event")
    timestamp: str = Field(..., description="ISO 8601 timestamp")
    src_ip: str = Field(..., description="Source IP address")
    dest_host: str = Field(..., description="Destination host/server")
    username: Optional[str] = Field(None, max_length=100, description="User involved")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional event details")
    
    @validator('src_ip')
    def validate_ip(cls, v):
        """Validate IP address format"""
        parts = v.split('.')
        if len(parts) != 4:
            raise ValueError('Invalid IP address format')
        for part in parts:
            try:
                num = int(part)
                if num < 0 or num > 255:
                    raise ValueError('IP octets must be 0-255')
            except ValueError:
                raise ValueError('Invalid IP address format')
        return v
    
    @validator('timestamp')
    def validate_timestamp(cls, v):
        """Validate ISO 8601 timestamp"""
        try:
            datetime.fromisoformat(v.replace('Z', '+00:00'))
        except:
            raise ValueError('Invalid ISO 8601 timestamp format')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "event_id": "evt_001",
                "event_type": "failed_ssh_login",
                "timestamp": "2026-05-21T14:00:00Z",
                "src_ip": "10.0.0.50",
                "dest_host": "prod-server",
                "username": "admin",
                "details": {"failed_attempts": 5}
            }
        }

# Response Models
class AnalysisResponse(BaseModel):
    incident_id: int
    event_id: str
    analysis: Dict[str, Any]
    severity: str
    status: str
    created_at: datetime

class IncidentListResponse(BaseModel):
    incident_id: int = Field(..., alias='id')
    event_id: str
    event_type: str
    severity: Optional[str] = None
    status: str
    created_at: datetime
    
    class Config:
        populate_by_name = True
class TaskResponse(BaseModel):
    task_id: str = Field(..., description="Celery task ID")
    event_id: str
    status: str
    message: str

class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    event_id: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: Optional[datetime] = None

class ErrorResponse(BaseModel):
    """Standard error response"""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed explanation")
    status_code: int = Field(..., description="HTTP status code")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ValidationError(BaseModel):
    """Validation error response"""
    error: str = "Validation failed"
    fields: Dict[str, str] = Field(..., description="Field errors")
    status_code: int = 422
# ============================================================
# Query Models (for GET request filters)
# ============================================================

class IncidentQueryParams(BaseModel):
    """Query parameters for listing incidents"""
    limit: int = 50
    offset: int = 0
    severity: Optional[str] = None
    status: Optional[str] = None
    event_id: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    sort_by: str = "created_at"
    order: str = "desc"
    
    @validator('limit')
    def validate_limit(cls, v):
        if v < 1 or v > 100:
            raise ValueError('Limit must be between 1 and 100')
        return v
    
    @validator('offset')
    def validate_offset(cls, v):
        if v < 0:
            raise ValueError('Offset cannot be negative')
        return v
    
    @validator('sort_by')
    def validate_sort_by(cls, v):
        valid = ['created_at', 'severity', 'event_id', 'status']
        if v not in valid:
            raise ValueError(f'sort_by must be one of: {valid}')
        return v
    
    @validator('order')
    def validate_order(cls, v):
        if v.lower() not in ['asc', 'desc']:
            raise ValueError('order must be "asc" or "desc"')
        return v.lower()

class IncidentStatsResponse(BaseModel):
    """Statistics about incidents"""
    total_incidents: int
    by_severity: Dict[str, int]
    by_status: Dict[str, int]
    by_event_type: Dict[str, int]
    avg_severity_score: float
    date_range: Dict[str, str]
