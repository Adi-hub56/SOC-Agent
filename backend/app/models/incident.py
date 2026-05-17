
from sqlalchemy import Column, String, DateTime, Integer, JSON, Text, Boolean, ForeignKey
from datetime import datetime
import uuid

from app.database import Base


class Incident(Base):
    __tablename__ = "incidents"
    
    # Primary Key
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Event Data
    event_id = Column(String, unique=True, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    event_type = Column(String)  # ssh_brute_force, sql_injection, etc.
    
    # Raw Data
    raw_event = Column(JSON, nullable=False)
    
    # Analysis Results
    classification = Column(String)  # Attack type
    severity = Column(String)  # CRITICAL, HIGH, MEDIUM, LOW
    threat_score = Column(Integer)  # 0-10
    confidence = Column(Integer)  # 0-100
    
    # Investigation
    investigation_findings = Column(JSON)  # Complete analysis
    recommended_actions = Column(JSON)  # List of actions
    
    # Reports
    pdf_report_path = Column(Text)
    markdown_report_path = Column(Text)
    
    # Status
    status = Column(String, default="pending")  # pending, analyzing, completed, failed
    error_message = Column(Text)
    
    # User who handled it
    analyzed_by = Column(String, ForeignKey("users.id"))
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime)
    
    def __repr__(self):
        return f"<Incident {self.event_id} - {self.severity}>"

