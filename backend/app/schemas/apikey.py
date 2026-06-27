from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class APIKeyCreate(BaseModel):
    name: str

class APIKeyResponse(BaseModel):
    id: int
    name: str
    key: str  # Only shown once on creation
    is_active: bool
    last_used: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True

class APIKeyListResponse(BaseModel):
    id: int
    name: str
    key: str  # Masked: show only last 8 chars
    is_active: bool
    last_used: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True
