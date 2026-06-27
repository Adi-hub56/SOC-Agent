from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.settings import UserSettingsUpdate, UserSettingsResponse, ChangePasswordRequest
from app.utils.auth import verify_password, hash_password, SECRET_KEY, ALGORITHM
from jose import jwt

router = APIRouter(prefix="/user", tags=["user"])
def get_current_user(
    authorization: str = Header(None),
    db: Session = Depends(get_db)
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

@router.get("/settings", response_model=UserSettingsResponse)
def get_settings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return current_user

@router.put("/settings", response_model=UserSettingsResponse)
def update_settings(
    settings: UserSettingsUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if settings.email and settings.email != current_user.email:
        existing = db.query(User).filter(User.email == settings.email).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already in use")
        current_user.email = settings.email
    
    if settings.theme:
        current_user.theme = settings.theme
    
    if settings.email_notifications is not None:
        current_user.email_notifications = settings.email_notifications
    
    if settings.slack_webhook_url is not None:
        current_user.slack_webhook_url = settings.slack_webhook_url
    
    if settings.slack_notifications is not None:
        current_user.slack_notifications = settings.slack_notifications
    
    db.commit()
    db.refresh(current_user)
    return current_user

@router.post("/change-password")
def change_password(
    pwd_request: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not verify_password(pwd_request.old_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="Old password is incorrect")
    
    current_user.password_hash = hash_password(pwd_request.new_password)
    db.commit()
    
    return {"message": "Password changed successfully"}
