
from sqlalchemy import Column, String, DateTime, JSON, ForeignKey
from datetime import datetime
import uuid

from app.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    # Primary Key
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # User who performed action
    user_id = Column(String, ForeignKey("users.id"))
    
    # Action Details
    action = Column(String, nullable=False)  # create, update, delete, analyze, etc.
    incident_id = Column(String, ForeignKey("incidents.id"))
    
    # Details of what changed
    details = Column(JSON)
    
    # Timestamp
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<AuditLog {self.action} by {self.user_id}>"

