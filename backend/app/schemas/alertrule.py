from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class AlertRuleCreate(BaseModel):
    name: str
    severity_threshold: str
    event_type: Optional[str] = None
    action: str

class AlertRuleUpdate(BaseModel):
    name: Optional[str] = None
    severity_threshold: Optional[str] = None
    event_type: Optional[str] = None
    action: Optional[str] = None
    is_enabled: Optional[bool] = None

class AlertRuleResponse(BaseModel):
    id: int
    name: str
    severity_threshold: str
    event_type: Optional[str]
    is_enabled: bool
    action: str
    created_at: datetime

    class Config:
        from_attributes = True
