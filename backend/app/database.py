from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# Database URL
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://soc_user:soc_password_dev@postgres:5432/soc_agent"
)

# Create engine
engine = create_engine(DATABASE_URL)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base for all models
Base = declarative_base()

def init_db():
    """Initialize database - create all tables"""
    from app.models.incident import Incident
    from app.models.user import User
    from app.models.audit_log import AuditLog
    Base.metadata.create_all(bind=engine)
    print("✅ Database initialized - all tables created")

def get_db():
    """Dependency for database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
