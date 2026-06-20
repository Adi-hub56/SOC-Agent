"""
Alert deduplication and correlation service
"""
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.incident import Incident
import uuid

class DeduplicationService:
    """Detect and handle duplicate alerts"""
    
    DEDUP_WINDOW_MINUTES = 5  # Consider alerts within 5 min as potential duplicates
    
    @staticmethod
    def check_duplicate(
        db: Session,
        event_id: str,
        event_type: str,
        src_ip: str,
        dest_host: str
    ) -> tuple[bool, int | None]:
        """
        Check if alert is duplicate of recent incident
        
        Returns: (is_duplicate, duplicate_of_id)
        """
        # Check if exact event_id already exists
        existing_exact = db.query(Incident).filter(
            Incident.event_id == event_id
        ).first()
        
        if existing_exact:
            return (True, existing_exact.id)
        
        # Check for similar alerts in last N minutes
        time_window = datetime.utcnow() - timedelta(minutes=DeduplicationService.DEDUP_WINDOW_MINUTES)
        
        similar = db.query(Incident).filter(
            Incident.event_type == event_type,
            Incident.source_ip == src_ip,
            Incident.target_host == dest_host,
            Incident.created_at >= time_window,
            Incident.is_duplicate == False
        ).first()
        
        if similar:
            return (True, similar.id)
        
        return (False, None)
    
    @staticmethod
    def mark_duplicate(db: Session, incident_id: int, duplicate_of_id: int):
        """Mark incident as duplicate of another"""
        incident = db.query(Incident).filter(Incident.id == incident_id).first()
        if incident:
            incident.is_duplicate = True
            incident.duplicate_of_id = duplicate_of_id
            db.commit()
    
    @staticmethod
    def get_dedup_stats(db: Session) -> dict:
        """Get deduplication statistics"""
        total = db.query(Incident).count()
        duplicates = db.query(Incident).filter(Incident.is_duplicate == True).count()
        unique = total - duplicates
        
        return {
            "total_incidents": total,
            "unique_incidents": unique,
            "duplicates": duplicates,
            "duplicate_percentage": round((duplicates / total * 100), 2) if total > 0 else 0
        }

