from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.twofa import TwoFA
from app.schemas.twofa import TwoFASetup, TwoFAVerify, TwoFAResponse, BackupCodesResponse
from app.utils.auth import SECRET_KEY, ALGORITHM
from jose import jwt
import pyotp
import qrcode
from io import BytesIO
import base64
import secrets
import string

router = APIRouter(prefix="/2fa", tags=["2fa"])

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

def generate_backup_codes(count: int = 10) -> list[str]:
    """Generate backup codes"""
    codes = []
    for _ in range(count):
        code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
        codes.append(f"{code[:4]}-{code[4:]}")
    return codes

def get_qr_code(secret: str, user_email: str) -> str:
    """Generate QR code for TOTP"""
    totp = pyotp.TOTP(secret)
    uri = totp.provisioning_uri(name=user_email, issuer_name='SOC Agent')
    
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(uri)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    img_base64 = base64.b64encode(buffer.getvalue()).decode()
    
    return f"data:image/png;base64,{img_base64}"

@router.get("/status", response_model=TwoFAResponse)
def get_2fa_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    two_fa = db.query(TwoFA).filter(TwoFA.user_id == current_user.id).first()
    
    if not two_fa:
        return {"is_enabled": False, "verified_at": None}
    
    backup_codes = two_fa.backup_codes.split(",") if two_fa.backup_codes else []
    
    return {
        "is_enabled": two_fa.is_enabled,
        "verified_at": two_fa.verified_at,
        "backup_codes": backup_codes if two_fa.is_enabled else None
    }

@router.post("/setup", response_model=TwoFASetup)
def setup_2fa(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate secret and QR code for 2FA setup"""
    
    # Generate secret
    secret = pyotp.random_base32()
    
    # Generate QR code
    qr_code = get_qr_code(secret, current_user.email)
    
    # Generate backup codes
    backup_codes = generate_backup_codes()
    
    # Save to DB (not verified yet)
    two_fa = db.query(TwoFA).filter(TwoFA.user_id == current_user.id).first()
    if not two_fa:
        two_fa = TwoFA(user_id=current_user.id)
        db.add(two_fa)
    
    two_fa.secret = secret
    two_fa.backup_codes = ",".join(backup_codes)
    two_fa.is_enabled = False
    db.commit()
    
    return {
        "secret": secret,
        "qr_code": qr_code
    }

@router.post("/verify")
def verify_2fa(
    verify_data: TwoFAVerify,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Verify TOTP code and enable 2FA"""
    
    two_fa = db.query(TwoFA).filter(TwoFA.user_id == current_user.id).first()
    if not two_fa or not two_fa.secret:
        raise HTTPException(status_code=400, detail="2FA not set up")
    
    totp = pyotp.TOTP(two_fa.secret)
    if not totp.verify(verify_data.code):
        raise HTTPException(status_code=400, detail="Invalid code")
    
    two_fa.is_enabled = True
    two_fa.verified_at = datetime.utcnow()
    db.commit()
    
    return {"message": "2FA enabled successfully"}

@router.post("/disable")
def disable_2fa(
    verify_data: TwoFAVerify,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Disable 2FA"""
    
    two_fa = db.query(TwoFA).filter(TwoFA.user_id == current_user.id).first()
    if not two_fa:
        raise HTTPException(status_code=400, detail="2FA not enabled")
    
    # Verify code before disabling
    totp = pyotp.TOTP(two_fa.secret)
    if not totp.verify(verify_data.code):
        raise HTTPException(status_code=400, detail="Invalid code")
    
    two_fa.is_enabled = False
    two_fa.secret = None
    two_fa.backup_codes = None
    db.commit()
    
    return {"message": "2FA disabled successfully"}

@router.get("/backup-codes", response_model=BackupCodesResponse)
def get_backup_codes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get backup codes"""
    
    two_fa = db.query(TwoFA).filter(TwoFA.user_id == current_user.id).first()
    if not two_fa or not two_fa.is_enabled:
        raise HTTPException(status_code=400, detail="2FA not enabled")
    
    backup_codes = two_fa.backup_codes.split(",") if two_fa.backup_codes else []
    
    return {"backup_codes": backup_codes}
