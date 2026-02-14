"""
Supabase PostgreSQL database setup using SQLAlchemy for scan history
"""
import json
import os
from datetime import datetime
from sqlalchemy import create_engine, Column, String, DateTime, Integer, JSON
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import NullPool

# Get database URL from environment variable (Supabase connection string)
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/exposechain"  # Fallback for local dev
)

# Configure engine for PostgreSQL with connection pooling
engine = create_engine(
    DATABASE_URL,
    poolclass=NullPool,  # Serverless-friendly: no persistent connections
    pool_pre_ping=True,  # Verify connections before using
    echo=False
)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()


class ScanRecord(Base):
    """Model for storing scan history"""
    __tablename__ = "scan_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    scan_id = Column(String(255), unique=True, nullable=False, index=True)
    target = Column(String(255), nullable=False, index=True)
    scan_type = Column(String(50), nullable=False, index=True)
    dns_results = Column(JSON, nullable=True)  # Native JSON type for PostgreSQL
    whois_results = Column(JSON, nullable=True)
    geolocation_results = Column(JSON, nullable=True)
    ssl_results = Column(JSON, nullable=True)
    ai_analysis = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """Convert record to dictionary"""
        return {
            "scan_id": self.scan_id,
            "target": self.target,
            "scan_type": self.scan_type,
            "dns_results": self.dns_results,
            "whois_results": self.whois_results,
            "geolocation_results": self.geolocation_results,
            "ssl_results": self.ssl_results,
            "ai_analysis": self.ai_analysis,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


def init_db():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
