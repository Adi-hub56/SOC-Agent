"""
Incident correlation service - link related incidents
"""
from sqlalchemy.orm import Session
from app.models.incident import Incident
import uuid

class CorrelationService:
    """Correlate related incidents"""
    
    @staticmethod
    def correlate_by_source_ip(db: Session, src_ip: str) -> list[int]:
        """Find all incidents from same source IP"""
        incidents = db.query(Incident).filter(
            Incident.source_ip == src_ip,
            Incident.is_duplicate == False
        ).all()
        
        return [i.id for i in incidents]
    
    @staticmethod
    def correlate_by_target_host(db: Session, target_host: str) -> list[int]:
        """Find all incidents targeting same host"""
        incidents = db.query(Incident).filter(
            Incident.target_host == target_host,
            Incident.is_duplicate == False
        ).all()
        
        return [i.id for i in incidents]
    
    @staticmethod
    def correlate_by_event_type(db: Session, event_type: str) -> list[int]:
        """Find all incidents of same type"""
        incidents = db.query(Incident).filter(
            Incident.event_type == event_type,
            Incident.is_duplicate == False
        ).all()
        
        return [i.id for i in incidents]
    
    @staticmethod
    def create_correlation_group(
        db: Session,
        incident_ids: list[int],
        reason: str
    ) -> str:
        """
        Create correlation group for incidents
        
        Returns: correlation_group_id
        """
        group_id = str(uuid.uuid4())[:8]
        
        for incident_id in incident_ids:
            incident = db.query(Incident).filter(Incident.id == incident_id).first()
            if incident:
                incident.correlation_group_id = group_id
                incident.is_correlated = True
                incident.correlation_reason = reason
        
        db.commit()
        return group_id
    
    @staticmethod
    def get_correlated_incidents(db: Session, incident_id: int) -> list[dict]:
        """Get all incidents in same correlation group"""
        incident = db.query(Incident).filter(Incident.id == incident_id).first()
        
        if not incident or not incident.correlation_group_id:
            return []
        
        related = db.query(Incident).filter(
            Incident.correlation_group_id == incident.correlation_group_id,
            Incident.id != incident_id
        ).all()
        
        return [
            {
                "id": i.id,
                "event_id": i.event_id,
                "event_type": i.event_type,
                "severity": i.severity,
                "created_at": i.created_at.isoformat()
            }
            for i in related
        ]
    
    @staticmethod
    def get_correlation_stats(db: Session) -> dict:
        """Get correlation statistics"""
        correlated = db.query(Incident).filter(
            Incident.is_correlated == True
        ).count()
        
        total = db.query(Incident).count()
        
        # Count correlation groups
        groups = db.query(
            Incident.correlation_group_id
        ).filter(
            Incident.correlation_group_id != None
        ).distinct().count()
        
        return {
            "total_correlated_incidents": correlated,
            "correlation_groups": groups,
            "avg_incidents_per_group": round(correlated / groups, 1) if groups > 0 else 0
        }

