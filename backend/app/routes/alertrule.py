from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session as DBSession
from app.database import get_db
from app.models.user import User
from app.models.alertrule import AlertRule
from app.schemas.alertrule import AlertRuleCreate, AlertRuleUpdate, AlertRuleResponse
from app.utils.auth import SECRET_KEY, ALGORITHM
from jose import jwt

router = APIRouter(prefix="/alert-rules", tags=["alert-rules"])

def get_current_user(
    authorization: str = Header(None),
    db: DBSession = Depends(get_db)
) -> User:
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        parts = authorization.split(" ")
        if len(parts) != 2:
            raise HTTPException(status_code=401, detail="Invalid authorization header format")
        scheme, token = parts
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid authorization scheme")
    except:
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Token validation failed: {str(e)}")
    
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/", response_model=AlertRuleResponse)
def create_alert_rule(
    rule_data: AlertRuleCreate,
    current_user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db)
):
    """Create a new alert rule"""
    new_rule = AlertRule(
        user_id=current_user.id,
        name=rule_data.name,
        severity_threshold=rule_data.severity_threshold,
        event_type=rule_data.event_type,
        action=rule_data.action
    )
    db.add(new_rule)
    db.commit()
    db.refresh(new_rule)
    return new_rule

@router.get("/", response_model=list[AlertRuleResponse])
def list_alert_rules(
    current_user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db)
):
    """List all alert rules for current user"""
    rules = db.query(AlertRule).filter(AlertRule.user_id == current_user.id).all()
    return rules

@router.get("/{rule_id}", response_model=AlertRuleResponse)
def get_alert_rule(
    rule_id: int,
    current_user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db)
):
    """Get specific alert rule"""
    rule = db.query(AlertRule).filter(
        AlertRule.id == rule_id,
        AlertRule.user_id == current_user.id
    ).first()
    
    if not rule:
        raise HTTPException(status_code=404, detail="Alert rule not found")
    
    return rule

@router.put("/{rule_id}", response_model=AlertRuleResponse)
def update_alert_rule(
    rule_id: int,
    rule_data: AlertRuleUpdate,
    current_user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db)
):
    """Update alert rule"""
    rule = db.query(AlertRule).filter(
        AlertRule.id == rule_id,
        AlertRule.user_id == current_user.id
    ).first()
    
    if not rule:
        raise HTTPException(status_code=404, detail="Alert rule not found")
    
    if rule_data.name:
        rule.name = rule_data.name
    if rule_data.severity_threshold:
        rule.severity_threshold = rule_data.severity_threshold
    if rule_data.event_type:
        rule.event_type = rule_data.event_type
    if rule_data.action:
        rule.action = rule_data.action
    if rule_data.is_enabled is not None:
        rule.is_enabled = rule_data.is_enabled
    
    db.commit()
    db.refresh(rule)
    return rule

@router.delete("/{rule_id}")
def delete_alert_rule(
    rule_id: int,
    current_user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db)
):
    """Delete alert rule"""
    rule = db.query(AlertRule).filter(
        AlertRule.id == rule_id,
        AlertRule.user_id == current_user.id
    ).first()
    
    if not rule:
        raise HTTPException(status_code=404, detail="Alert rule not found")
    
    db.delete(rule)
    db.commit()
    
    return {"message": "Alert rule deleted successfully"}
