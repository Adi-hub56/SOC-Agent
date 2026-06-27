from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TwoFASetup(BaseModel):
    secret: str
    qr_code: str

class TwoFAVerify(BaseModel):
    code: str

class TwoFAResponse(BaseModel):
    is_enabled: bool
    verified_at: Optional[datetime]
    backup_codes: Optional[list[str]] = None

class BackupCodesResponse(BaseModel):
    backup_codes: list[str]
