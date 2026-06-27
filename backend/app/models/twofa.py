from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from app.database import Base
from datetime import datetime

class TwoFA(Base):
    __tablename__ = "two_fa"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    is_enabled = Column(Boolean, default=False)
    secret = Column(String, nullable=True)  # TOTP secret
    backup_codes = Column(String, nullable=True)  # Comma-separated backup codes
    created_at = Column(DateTime, default=datetime.utcnow)
    verified_at = Column(DateTime, nullable=True)
