from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean, Index
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class Incident(Base):
    __tablename__ = "incidents"
    __table_args__ = (
        Index('idx_event_id', 'event_id'),
        Index('idx_source_ip', 'source_ip'),
        Index('idx_correlation_group', 'correlation_group_id'),
        Index('idx_is_duplicate', 'is_duplicate'),
        {'extend_existing': True}
    )
    
    # Core fields
    id = Column(Integer, primary_key=True)
    event_id = Column(String, unique=True)
    event_type = Column(String)
    source_ip = Column(String)
    target_host = Column(String)
    username = Column(String, nullable=True)
    raw_alert = Column(Text)
    analysis_results = Column(Text, nullable=True)
    severity = Column(String, nullable=True)
    status = Column(String, default="pending")
    task_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Deduplication fields
    is_duplicate = Column(Boolean, default=False)
    duplicate_of_id = Column(Integer, ForeignKey('incidents.id'), nullable=True)
    
    # Correlation fields
    correlation_group_id = Column(String, nullable=True)
    is_correlated = Column(Boolean, default=False)
    correlation_reason = Column(String, nullable=True)
