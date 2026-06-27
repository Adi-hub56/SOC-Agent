from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.apikey import APIKey
from app.models.user import User
from app.schemas.apikey import APIKeyCreate, APIKeyResponse, APIKeyListResponse
from app.utils.auth import SECRET_KEY, ALGORITHM
from jose import jwt

router = APIRouter(prefix="/api-keys", tags=["api-keys"])
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

@router.post("/", response_model=APIKeyResponse)
def create_api_key(
    key_data: APIKeyCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    new_key = APIKey(
        user_id=current_user.id,
        name=key_data.name,
        key=APIKey.generate_key()
    )
    db.add(new_key)
    db.commit()
    db.refresh(new_key)
    
    return new_key

@router.get("/", response_model=list[APIKeyListResponse])
def list_api_keys(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    keys = db.query(APIKey).filter(APIKey.user_id == current_user.id).all()
    
    # Mask keys - show only last 8 chars
    for key in keys:
        if len(key.key) > 8:
            key.key = "sk_" + "*" * (len(key.key) - 11) + key.key[-8:]
    
    return keys

@router.delete("/{key_id}")
def revoke_api_key(
    key_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    api_key = db.query(APIKey).filter(
        APIKey.id == key_id,
        APIKey.user_id == current_user.id
    ).first()
    
    if not api_key:
        raise HTTPException(status_code=404, detail="API Key not found")
    
    db.delete(api_key)
    db.commit()
    
    return {"message": "API Key revoked successfully"}

@router.put("/{key_id}/toggle")
def toggle_api_key(
    key_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    api_key = db.query(APIKey).filter(
        APIKey.id == key_id,
        APIKey.user_id == current_user.id
    ).first()
    
    if not api_key:
        raise HTTPException(status_code=404, detail="API Key not found")
    
    api_key.is_active = not api_key.is_active
    db.commit()
    db.refresh(api_key)
    
    return {"is_active": api_key.is_active}

