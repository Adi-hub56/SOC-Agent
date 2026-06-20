from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.utils.logger import log_info
from datetime import datetime
import psutil
import os

router = APIRouter(prefix="/api", tags=["system"])

@router.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint
    Returns system status
    """
    try:
        # Check database
        db.execute("SELECT 1")
        db_status = "healthy"
    except:
        db_status = "unhealthy"
    
    return {
        "status": "healthy",
        "service": "SOC Agent API",
        "version": "1.0.0",
        "llm_provider": "groq",
        "database": db_status,
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/system/info")
async def system_info():
    """Get system resource information"""
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "cpu": {
            "percent": cpu_percent,
            "count": os.cpu_count()
        },
        "memory": {
            "total_gb": round(memory.total / (1024**3), 2),
            "used_gb": round(memory.used / (1024**3), 2),
            "percent": memory.percent
        },
        "disk": {
            "total_gb": round(disk.total / (1024**3), 2),
            "used_gb": round(disk.used / (1024**3), 2),
            "percent": disk.percent
        }
    }
