from pydantic import BaseModel, EmailStr, HttpUrl
from typing import Optional

class UserSettingsUpdate(BaseModel):
    email: Optional[EmailStr] = None
    theme: Optional[str] = None
    email_notifications: Optional[bool] = None
    slack_webhook_url: Optional[str] = None
    slack_notifications: Optional[bool] = None

class UserSettingsResponse(BaseModel):
    id: int
    username: str
    email: str
    theme: str
    email_notifications: bool
    slack_webhook_url: Optional[str] = None
    slack_notifications: bool

    class Config:
        from_attributes = True

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str
