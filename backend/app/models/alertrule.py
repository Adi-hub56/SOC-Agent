from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey
from app.database import Base
from datetime import datetime

class AlertRule(Base):
    __tablename__ = "alert_rules"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    severity_threshold = Column(String, default="high")  # low, medium, high, critical
    event_type = Column(String, nullable=True)  # Optional filter
    is_enabled = Column(Boolean, default=True)
    action = Column(String, default="email")  # email, slack, both
    created_at = Column(DateTime, default=datetime.utcnow)
