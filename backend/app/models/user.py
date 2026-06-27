from sqlalchemy import Column, Integer, String, DateTime, Boolean
from app.database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="analyst")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Settings fields
    theme = Column(String, default="dark")  # dark or light
    email_notifications = Column(Boolean, default=True)
    slack_webhook_url = Column(String, nullable=True)
    slack_notifications = Column(Boolean, default=False)
