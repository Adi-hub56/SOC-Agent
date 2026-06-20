from app.services.deduplication import DeduplicationService
from app.services.correlation import CorrelationService
from app.services.export import ExportService
from fastapi.responses import StreamingResponse
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.incident import (
    AlertRequest, AnalysisResponse, IncidentListResponse,
    TaskResponse, TaskStatusResponse, ErrorResponse
)
from app.tasks.analysis import analyze_security_alert
from app.models.incident import Incident
from app.utils.logger import log_info, log_error
from app.celery_app import app as celery_app
from app.exceptions import IncidentNotFound, TaskNotFound, AnalysisException
from datetime import datetime
import json

router = APIRouter(prefix="/api", tags=["incidents"])

# ============================================================
# POST /api/analyze - ASYNC endpoint
# ============================================================
@router.post("/analyze", response_model=TaskResponse, status_code=202)
async def analyze_alert_async(alert: AlertRequest, db: Session = Depends(get_db)):
    """
    Analyze a security alert asynchronously
    
    Returns 202 Accepted with task_id
    Use GET /api/tasks/{task_id} to check status
    """
    try:
        log_info("Alert received (async)", event_id=alert.event_id)
        
        # Check for duplicate
        existing = db.query(Incident).filter(
            Incident.event_id == alert.event_id
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Alert {alert.event_id} already processed"
            )
        
        # Create initial incident record
        alert_dict = alert.dict()
        
        # Check for duplicates using service
        is_dup, dup_of_id = DeduplicationService.check_duplicate(
            db,
            alert.event_id,
            alert.event_type,
            alert.src_ip,
            alert.dest_host
        )
        
        incident = Incident(
            event_id=alert.event_id,
            event_type=alert.event_type,
            source_ip=alert.src_ip,
            target_host=alert.dest_host,
            username=alert.username,
            raw_alert=json.dumps(alert_dict),
            status="PENDING",
            is_duplicate=is_dup,
            duplicate_of_id=dup_of_id
        )
        db.add(incident)
        db.commit()
        db.refresh(incident)
        
        # Log if duplicate
        if is_dup:
            log_info("Duplicate alert detected", event_id=alert.event_id, duplicate_of=dup_of_id)
        
        # Queue the analysis task
        task = analyze_security_alert.delay(alert_dict)
        
        # Update incident with task_id
        incident.task_id = task.id
        db.commit()
        
        log_info("Task queued", task_id=task.id, event_id=alert.event_id)
        
        return TaskResponse(
            task_id=task.id,
            event_id=alert.event_id,
            status="PENDING",
            message=f"Analysis queued. Check status with: GET /api/tasks/{task.id}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        log_error("Failed to queue analysis", error=str(e))
        raise AnalysisException(str(e))
# ============================================================
# POST /api/analyze/batch - BATCH analysis (multiple alerts)
# ============================================================

@router.post("/analyze/batch", status_code=202)
async def analyze_batch(alerts: list[AlertRequest], db: Session = Depends(get_db)):
    """
    Analyze multiple security alerts in one request
    
    Returns list of task IDs (one per alert)
    
    Example:
    POST /api/analyze/batch
    [
      {"event_id": "evt_001", "event_type": "failed_ssh_login", ...},
      {"event_id": "evt_002", "event_type": "malware_detected", ...}
    ]
    """
    try:
        if not alerts or len(alerts) > 50:
            raise HTTPException(
                status_code=400,
                detail="Batch size must be 1-50 alerts"
            )
        
        log_info("Batch analysis received", count=len(alerts))
        
        results = []
        
        for alert in alerts:
            try:
                # Check for duplicate
                existing = db.query(Incident).filter(
                    Incident.event_id == alert.event_id
                ).first()
                
                if existing:
                    results.append({
                        "event_id": alert.event_id,
                        "status": "SKIPPED",
                        "reason": "Already processed"
                    })
                    continue
                
                # Create incident record
                alert_dict = alert.dict()
                incident = Incident(
                    event_id=alert.event_id,
                    event_type=alert.event_type,
                    source_ip=alert.src_ip,
                    target_host=alert.dest_host,
                    username=alert.username,
                    raw_alert=json.dumps(alert_dict),
                    status="PENDING"
                )
                db.add(incident)
                db.commit()
                db.refresh(incident)
                
                # Queue task
                task = analyze_security_alert.delay(alert_dict)
                incident.task_id = task.id
                db.commit()
                
                results.append({
                    "event_id": alert.event_id,
                    "task_id": task.id,
                    "status": "QUEUED"
                })
                
            except Exception as e:
                log_error("Failed to queue alert", event_id=alert.event_id, error=str(e))
                results.append({
                    "event_id": alert.event_id,
                    "status": "FAILED",
                    "error": str(e)
                })
        
        return {
            "batch_size": len(alerts),
            "processed": len([r for r in results if r["status"] in ["QUEUED", "SKIPPED"]]),
            "results": results
        }
        
    except HTTPException:
        raise
    except Exception as e:
        log_error("Batch analysis failed", error=str(e))
        raise AnalysisException(str(e))
# ============================================================
# GET /api/tasks/{task_id} - Check task status
# ============================================================

@router.get("/tasks/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str, db: Session = Depends(get_db)):
    """
    Check status of a security alert analysis task
    
    Status values:
    - PENDING: Waiting to be processed
    - PROCESSING: Currently analyzing
    - SUCCESS: Complete with results
    - FAILURE: Error occurred
    """
    try:
        # Get the celery task
        task = celery_app.AsyncResult(task_id)
        
        # Get the incident record
        incident = db.query(Incident).filter(
            Incident.task_id == task_id
        ).first()
        
        if not incident:
            raise TaskNotFound(task_id)
        
        log_info("Task status checked", task_id=task_id)
        
        celery_state = task.state
        
        if celery_state == 'PENDING':
            return TaskStatusResponse(
                task_id=task_id,
                status="PENDING",
                event_id=incident.event_id,
                created_at=incident.created_at
            )
        
        elif celery_state == 'PROCESSING':
            return TaskStatusResponse(
                task_id=task_id,
                status="PROCESSING",
                event_id=incident.event_id,
                created_at=incident.created_at
            )
        
        elif celery_state == 'SUCCESS':
            analysis = json.loads(incident.analysis_results) if incident.analysis_results else None
            return TaskStatusResponse(
                task_id=task_id,
                status="SUCCESS",
                event_id=incident.event_id,
                result={
                    "incident_id": incident.id,
                    "severity": incident.severity,
                    "analysis": analysis
                },
                created_at=incident.created_at
            )
        
        elif celery_state == 'FAILURE':
            return TaskStatusResponse(
                task_id=task_id,
                status="FAILURE",
                event_id=incident.event_id,
                error=str(task.info),
                created_at=incident.created_at
            )
        
        else:
            return TaskStatusResponse(
                task_id=task_id,
                status=celery_state,
                event_id=incident.event_id,
                created_at=incident.created_at
            )
        
    except TaskNotFound:
        raise
    except Exception as e:
        log_error("Failed to get task status", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================
# GET /api/incidents - List incidents with filters
# ============================================================

@router.get("/incidents", response_model=list[IncidentListResponse])
async def list_incidents(
    db: Session = Depends(get_db),
    limit: int = Query(50, ge=1, le=100, description="Max results (1-100)"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    severity: str = Query(None, description="Filter: CRITICAL, HIGH, MEDIUM, LOW, INFO"),
    status: str = Query(None, description="Filter: pending, analyzing, analyzed, failed"),
    event_id: str = Query(None, description="Search by event_id"),
    start_date: str = Query(None, description="Filter: ISO 8601 start date"),
    end_date: str = Query(None, description="Filter: ISO 8601 end date"),
    sort_by: str = Query("created_at", description="Sort by: created_at, severity, event_id, status"),
    order: str = Query("desc", description="Sort order: asc or desc")
):
    """
    List incidents with advanced filtering, searching, and sorting
    
    Examples:
    - /api/incidents?severity=HIGH&limit=10
    - /api/incidents?event_id=evt_001
    - /api/incidents?start_date=2026-05-20&end_date=2026-05-21
    - /api/incidents?status=analyzed&sort_by=severity&order=asc
    - /api/incidents?limit=20&offset=40
    """
    try:
        query = db.query(Incident)
        
        # Apply filters
        if severity:
            severity = severity.upper()
            valid_severities = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'INFO']
            if severity not in valid_severities:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid severity. Must be one of: {valid_severities}"
                )
            query = query.filter(Incident.severity == severity)
        
        if status:
            status = status.lower()
            query = query.filter(Incident.status == status)
        
        if event_id:
            query = query.filter(Incident.event_id.contains(event_id))
        
        # Date range filtering
        if start_date:
            try:
                start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                query = query.filter(Incident.created_at >= start)
            except:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid start_date format. Use ISO 8601"
                )
        
        if end_date:
            try:
                end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                query = query.filter(Incident.created_at <= end)
            except:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid end_date format. Use ISO 8601"
                )
        
        # Apply sorting
        sort_by = sort_by.lower()
        order_asc = order.lower() == 'asc'
        
        if sort_by == 'created_at':
            query = query.order_by(Incident.created_at.asc() if order_asc else Incident.created_at.desc())
        elif sort_by == 'severity':
            query = query.order_by(Incident.severity.asc() if order_asc else Incident.severity.desc())
        elif sort_by == 'event_id':
            query = query.order_by(Incident.event_id.asc() if order_asc else Incident.event_id.desc())
        elif sort_by == 'status':
            query = query.order_by(Incident.status.asc() if order_asc else Incident.status.desc())
        else:
            query = query.order_by(Incident.created_at.desc())
        
        # Count total before pagination
        total = query.count()
        
        # Apply pagination
        incidents = query.offset(offset).limit(limit).all()
        
        log_info(
            "Incidents listed",
            count=len(incidents),
            total=total,
            filters={"severity": severity, "status": status, "event_id": event_id}
        )
        
        return incidents
        
    except HTTPException:
        raise
    except Exception as e:
        log_error("Failed to fetch incidents", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to fetch incidents")

# ============================================================
# GET /api/incidents/stats - Incident statistics
# ============================================================

@router.get("/incidents/stats")
async def get_incident_stats(
    db: Session = Depends(get_db),
    start_date: str = Query(None, description="ISO 8601 start date"),
    end_date: str = Query(None, description="ISO 8601 end date")
):
    """
    Get statistics about incidents
    
    Returns:
    - Total incidents
    - Count by severity
    - Count by status
    - Count by event type
    - Average severity score
    """
    try:
        query = db.query(Incident)
        
        # Apply date filters if provided
        if start_date:
            try:
                start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                query = query.filter(Incident.created_at >= start)
            except:
                raise HTTPException(status_code=400, detail="Invalid start_date format")
        
        if end_date:
            try:
                end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                query = query.filter(Incident.created_at <= end)
            except:
                raise HTTPException(status_code=400, detail="Invalid end_date format")
        
        incidents = query.all()
        
        # Calculate statistics
        total = len(incidents)
        
        # By severity
        by_severity = {}
        for incident in incidents:
            severity = incident.severity or 'UNKNOWN'
            by_severity[severity] = by_severity.get(severity, 0) + 1
        
        # By status
        by_status = {}
        for incident in incidents:
            status = incident.status or 'UNKNOWN'
            by_status[status] = by_status.get(status, 0) + 1
        
        # By event type
        by_event_type = {}
        for incident in incidents:
            event_type = incident.event_type or 'UNKNOWN'
            by_event_type[event_type] = by_event_type.get(event_type, 0) + 1
        
        # Average severity score
        severity_scores = {'CRITICAL': 5, 'HIGH': 4, 'MEDIUM': 3, 'LOW': 2, 'INFO': 1}
        scores = [severity_scores.get(i.severity, 0) for i in incidents]
        avg_score = sum(scores) / len(scores) if scores else 0
        
        # Date range
        if incidents:
            date_range = {
                "earliest": min([i.created_at for i in incidents]).isoformat(),
                "latest": max([i.created_at for i in incidents]).isoformat()
            }
        else:
            date_range = {"earliest": None, "latest": None}
        
        log_info("Statistics retrieved", total=total)
        
        return {
            "total_incidents": total,
            "by_severity": by_severity,
            "by_status": by_status,
            "by_event_type": by_event_type,
            "avg_severity_score": round(avg_score, 2),
            "date_range": date_range
        }
        
    except HTTPException:
        raise
    except Exception as e:
        log_error("Failed to get statistics", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get statistics")

# ============================================================
# GET /api/incidents/{incident_id} - Get single incident
# ============================================================

@router.get("/incidents/{incident_id}", response_model=AnalysisResponse)
async def get_incident(incident_id: int, db: Session = Depends(get_db)):
    """Get details of a specific incident"""
    try:
        incident = db.query(Incident).filter(
            Incident.id == incident_id
        ).first()
        
        if not incident:
            raise IncidentNotFound(incident_id)
        
        analysis = json.loads(
            incident.analysis_results
        ) if incident.analysis_results else {}
        
        return AnalysisResponse(
            incident_id=incident.id,
            event_id=incident.event_id,
            analysis=analysis,
            severity=incident.severity,
            status=incident.status,
            created_at=incident.created_at
        )
    except IncidentNotFound:
        raise
    except Exception as e:
        log_error("Failed to fetch incident", error=str(e))
        raise HTTPException(status_code=500, detail="Error fetching incident")

# ============================================================
# GET /api/reports/{incident_id} - Get report paths
# ============================================================

@router.get("/reports/{incident_id}")
async def get_incident_reports(incident_id: int, db: Session = Depends(get_db)):
    """Get paths to generated reports for an incident"""
    try:
        incident = db.query(Incident).filter(
            Incident.id == incident_id
        ).first()
        
        if not incident:
            raise IncidentNotFound(incident_id)
        
        from pathlib import Path
        reports_dir = Path("/tmp/soc-agent-reports")
        
        md_file = reports_dir / f"incident_{incident_id}_{incident.event_id}.md"
        pdf_file = reports_dir / f"incident_{incident_id}_{incident.event_id}.pdf"
        
        return {
            "incident_id": incident_id,
            "event_id": incident.event_id,
            "markdown_path": str(md_file) if md_file.exists() else None,
            "pdf_path": str(pdf_file) if pdf_file.exists() else None,
            "markdown_exists": md_file.exists(),
            "pdf_exists": pdf_file.exists()
        }
        
    except IncidentNotFound:
        raise
    except Exception as e:
        log_error("Failed to get reports", error=str(e))
        raise HTTPException(status_code=500, detail="Error fetching reports")
# ============================================================
# GET /api/incidents/dedup/stats - Deduplication statistics
# ============================================================

@router.get("/incidents/dedup/stats")
async def get_dedup_stats(db: Session = Depends(get_db)):
    """Get deduplication statistics"""
    try:
        stats = DeduplicationService.get_dedup_stats(db)
        log_info("Dedup stats retrieved")
        return stats
    except Exception as e:
        log_error("Failed to get dedup stats", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get statistics")

# ============================================================
# GET /api/incidents/{id}/correlated - Get correlated incidents
# ============================================================

@router.get("/incidents/{incident_id}/correlated")
async def get_correlated_incidents(incident_id: int, db: Session = Depends(get_db)):
    """Get incidents correlated with given incident"""
    try:
        incident = db.query(Incident).filter(Incident.id == incident_id).first()
        
        if not incident:
            raise IncidentNotFound(incident_id)
        
        correlated = CorrelationService.get_correlated_incidents(db, incident_id)
        
        log_info("Correlated incidents retrieved", incident_id=incident_id)
        
        return {
            "incident_id": incident_id,
            "correlation_group_id": incident.correlation_group_id,
            "correlation_reason": incident.correlation_reason,
            "correlated_count": len(correlated),
            "correlated_incidents": correlated
        }
    except IncidentNotFound:
        raise
    except Exception as e:
        log_error("Failed to get correlated incidents", error=str(e))
        raise HTTPException(status_code=500, detail="Error fetching correlated incidents")

# ============================================================
# GET /api/incidents/correlation/stats - Correlation statistics
# ============================================================

@router.get("/incidents/correlation/stats")
async def get_correlation_stats(db: Session = Depends(get_db)):
    """Get correlation statistics"""
    try:
        stats = CorrelationService.get_correlation_stats(db)
        log_info("Correlation stats retrieved")
        return stats
    except Exception as e:
        log_error("Failed to get correlation stats", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get statistics")

# ============================================================
# GET /api/export/csv - Export incidents as CSV
# ============================================================

@router.get("/export/csv")
async def export_csv(
    db: Session = Depends(get_db),
    severity: str = Query(None, description="Filter by severity"),
    limit: int = Query(None, ge=1, le=10000, description="Max incidents to export")
):
    """
    Export incidents as CSV file
    
    Query Parameters:
    - severity: Filter by severity (CRITICAL, HIGH, MEDIUM, LOW, INFO)
    - limit: Max incidents to include
    """
    try:
        query = db.query(Incident)
        
        if severity:
            query = query.filter(Incident.severity == severity.upper())
        
        if limit:
            query = query.limit(limit)
        
        incident_ids = [i.id for i in query.all()]
        csv_data = ExportService.export_to_csv(db, incident_ids)
        
        filename = ExportService.get_export_filename("csv")
        
        log_info("Incidents exported as CSV", count=len(incident_ids))
        
        return StreamingResponse(
            iter([csv_data]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        log_error("Failed to export CSV", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to export CSV")

# ============================================================
# GET /api/export/json - Export incidents as JSON
# ============================================================

@router.get("/export/json")
async def export_json(
    db: Session = Depends(get_db),
    severity: str = Query(None, description="Filter by severity"),
    limit: int = Query(None, ge=1, le=10000, description="Max incidents to export")
):
    """
    Export incidents as JSON file
    
    Query Parameters:
    - severity: Filter by severity
    - limit: Max incidents to include
    """
    try:
        query = db.query(Incident)
        
        if severity:
            query = query.filter(Incident.severity == severity.upper())
        
        if limit:
            query = query.limit(limit)
        
        incident_ids = [i.id for i in query.all()]
        json_data = ExportService.export_to_json(db, incident_ids)
        
        filename = ExportService.get_export_filename("json")
        
        log_info("Incidents exported as JSON", count=len(incident_ids))
        
        return StreamingResponse(
            iter([json_data]),
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except Exception as e:
        log_error("Failed to export JSON", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to export JSON")
 # ============================================================
# POST /api/chat - AI Chatbot endpoint
# ============================================================

@router.post("/chat")
async def chat(
    message: str = Query(..., description="User question"),
    db: Session = Depends(get_db)
):
    """
    AI-powered chatbot for incident analysis
    Uses Groq LLM to answer questions about incidents
    """
    try:
        from app.services.llm_agent import LLMAgent
        
        # Get incidents for context
        incidents = db.query(Incident).order_by(Incident.created_at.desc()).limit(10).all()
        
        # Create context summary
        context = f"""
        You are a SOC analyst assistant. You have access to incident data.
        
        Current Incidents:
        """
        
        for inc in incidents:
            context += f"\n- {inc.event_id}: {inc.event_type} from {inc.source_ip} to {inc.target_host} (Severity: {inc.severity})"
        
        context += f"\n\nUser Question: {message}\n\nProvide a concise, helpful response."
        
        # Use LLM to answer
        agent = LLMAgent()
        response = agent.analyze_with_context(context)
        
        log_info("Chat query processed", message=message)
        
        return {
            "message": message,
            "response": response,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        log_error("Chat failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")
