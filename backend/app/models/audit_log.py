from sqlalchemy import Column, Integer, String, DateTime, Text
from app.database import Base
from datetime import datetime

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    action = Column(String)
    resource = Column(String)
    details = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
