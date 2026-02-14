"""
SQLite database setup using SQLAlchemy for scan history
"""
import json
from datetime import datetime
from sqlalchemy import create_engine, Column, String, DateTime, Text, Integer
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "sqlite:///exposechain.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class ScanRecord(Base):
    """Model for storing scan history"""
    __tablename__ = "scan_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    scan_id = Column(String(36), unique=True, nullable=False, index=True)
    target = Column(String(255), nullable=False, index=True)
    scan_type = Column(String(10), nullable=False)
    target_type = Column(String(20), default="domain")
    success = Column(Integer, default=1)  # SQLite boolean
    message = Column(Text, default="")
    data_json = Column(Text, nullable=False)  # JSON-serialized scan data
    ai_analysis_json = Column(Text, nullable=True)  # JSON-serialized AI result
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        """Convert record to dictionary"""
        return {
            "scan_id": self.scan_id,
            "target": self.target,
            "scan_type": self.scan_type,
            "target_type": self.target_type,
            "success": bool(self.success),
            "message": self.message,
            "data": json.loads(self.data_json) if self.data_json else {},
            "ai_analysis": json.loads(self.ai_analysis_json) if self.ai_analysis_json else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
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
