
"""
Celery tasks for security alert analysis
Async processing with Groq LLM
"""
from app.celery_app import app
from app.services.llm_agent import LLMAgent
from app.services.report_generator import ReportGenerator
from app.models.incident import Incident
from app.database import SessionLocal
from app.utils.logger import log_info, log_error
import json
from datetime import datetime

@app.task(
    name='analyze_security_alert',
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={'max_retries': 2},
    retry_backoff=True
)
def analyze_security_alert(self, alert_data: dict):
    """
    Analyze security alert asynchronously + generate reports
    """
    db = SessionLocal()
    task_id = self.request.id
    
    try:
        log_info(f"Starting analysis", task_id=task_id, event_id=alert_data.get('event_id'))
        
        self.update_state(state='PROCESSING', meta={'current': 'Initializing LLM'})
        
        agent = LLMAgent(provider="groq")
        
        self.update_state(state='PROCESSING', meta={'current': 'Running 5-step analysis'})
        
        log_info("Running 5-step analysis", task_id=task_id)
        analysis_results = agent.analyze_alert_multi_step(alert_data)
        
        threat_assessment = analysis_results.get("step_2_threat_assessment", {})
        severity = threat_assessment.get("severity", "MEDIUM")
        
        self.update_state(state='PROCESSING', meta={'current': 'Saving to database'})
        
        incident = Incident(
            event_id=alert_data.get('event_id'),
            event_type=alert_data.get('event_type'),
            source_ip=alert_data.get('src_ip'),
            target_host=alert_data.get('dest_host'),
            username=alert_data.get('username'),
            raw_alert=json.dumps(alert_data),
            analysis_results=json.dumps(analysis_results),
            severity=severity,
            status="analyzed",
            task_id=task_id
        )
        
        db.add(incident)
        db.commit()
        db.refresh(incident)
        
        log_info("Incident saved", incident_id=incident.id, task_id=task_id)
        
        self.update_state(state='PROCESSING', meta={'current': 'Generating reports'})
        
        try:
            report_gen = ReportGenerator(incident.id, alert_data.get('event_id'))
            report_paths = report_gen.generate_all(analysis_results, severity)
            log_info("Reports generated", incident_id=incident.id, reports=report_paths)
        except Exception as e:
            log_error("Report generation failed", error=str(e))
            report_paths = {"error": str(e)}
        
        return {
            'status': 'success',
            'incident_id': incident.id,
            'event_id': alert_data.get('event_id'),
            'severity': severity,
            'analysis': analysis_results,
            'reports': report_paths
        }
        
    except Exception as e:
        log_error("Analysis failed", error=str(e), task_id=task_id)
        raise
        
    finally:
        db.close()

