"""
Custom exceptions for SOC Agent
"""
from fastapi import HTTPException, status

class AnalysisException(HTTPException):
    """Analysis failed"""
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {detail}"
        )

class ValidationException(HTTPException):
    """Invalid input"""
    def __init__(self, detail: str, fields: dict = None):
        self.fields = fields or {}
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail
        )

class IncidentNotFound(HTTPException):
    """Incident not found"""
    def __init__(self, incident_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incident {incident_id} not found"
        )

class TaskNotFound(HTTPException):
    """Task not found"""
    def __init__(self, task_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )
