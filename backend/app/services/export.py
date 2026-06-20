"""
Incident export service - CSV, JSON formats
"""
from sqlalchemy.orm import Session
from app.models.incident import Incident
import csv
import json
from io import StringIO
from datetime import datetime

class ExportService:
    """Export incidents to various formats"""
    
    @staticmethod
    def export_to_csv(db: Session, incident_ids: list[int] = None) -> str:
        """
        Export incidents to CSV format
        
        Returns: CSV string
        """
        query = db.query(Incident)
        
        if incident_ids:
            query = query.filter(Incident.id.in_(incident_ids))
        
        incidents = query.all()
        
        # Create CSV
        output = StringIO()
        writer = csv.DictWriter(
            output,
            fieldnames=[
                'id', 'event_id', 'event_type', 'severity', 'status',
                'source_ip', 'target_host', 'username', 'created_at',
                'is_duplicate', 'is_correlated', 'correlation_group_id'
            ]
        )
        
        writer.writeheader()
        
        for incident in incidents:
            writer.writerow({
                'id': incident.id,
                'event_id': incident.event_id,
                'event_type': incident.event_type,
                'severity': incident.severity or 'UNKNOWN',
                'status': incident.status,
                'source_ip': incident.source_ip,
                'target_host': incident.target_host,
                'username': incident.username or '',
                'created_at': incident.created_at.isoformat(),
                'is_duplicate': incident.is_duplicate,
                'is_correlated': incident.is_correlated,
                'correlation_group_id': incident.correlation_group_id or ''
            })
        
        return output.getvalue()
    
    @staticmethod
    def export_to_json(db: Session, incident_ids: list[int] = None) -> str:
        """
        Export incidents to JSON format
        
        Returns: JSON string
        """
        query = db.query(Incident)
        
        if incident_ids:
            query = query.filter(Incident.id.in_(incident_ids))
        
        incidents = query.all()
        
        data = {
            "export_timestamp": datetime.utcnow().isoformat(),
            "total_incidents": len(incidents),
            "incidents": [
                {
                    "id": i.id,
                    "event_id": i.event_id,
                    "event_type": i.event_type,
                    "severity": i.severity,
                    "status": i.status,
                    "source_ip": i.source_ip,
                    "target_host": i.target_host,
                    "username": i.username,
                    "created_at": i.created_at.isoformat(),
                    "is_duplicate": i.is_duplicate,
                    "duplicate_of_id": i.duplicate_of_id,
                    "is_correlated": i.is_correlated,
                    "correlation_group_id": i.correlation_group_id,
                    "correlation_reason": i.correlation_reason
                }
                for i in incidents
            ]
        }
        
        return json.dumps(data, indent=2)
    
    @staticmethod
    def get_export_filename(format_type: str) -> str:
        """Generate filename for export"""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        
        if format_type == "csv":
            return f"incidents_{timestamp}.csv"
        elif format_type == "json":
            return f"incidents_{timestamp}.json"
        else:
            return f"incidents_{timestamp}.txt"

