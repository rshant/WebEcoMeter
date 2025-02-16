from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from datetime import datetime
from contextlib import contextmanager
from typing import List, Optional

# Database connection
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

# Configure connection pooling
engine = create_engine(
    DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class WebsiteMetrics(Base):
    """Model for storing historical website carbon footprint measurements."""
    __tablename__ = "website_metrics"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    page_size_kb = Column(Float)
    monthly_visits = Column(Integer)
    annual_energy_kwh = Column(Float)
    annual_carbon_kg = Column(Float)
    trees_needed = Column(Integer)

    @classmethod
    def create_measurement(cls, db, url: str, metrics: dict, monthly_visits: int) -> Optional['WebsiteMetrics']:
        """Create a new measurement record with error handling."""
        try:
            new_measurement = cls(
                url=url,
                page_size_kb=metrics['page_size_kb'],
                monthly_visits=monthly_visits,
                annual_energy_kwh=metrics['annual_energy_kwh'],
                annual_carbon_kg=metrics['annual_carbon_kg'],
                trees_needed=metrics['trees_needed']
            )
            db.add(new_measurement)
            db.commit()
            db.refresh(new_measurement)
            return new_measurement
        except Exception as e:
            db.rollback()
            raise Exception(f"Failed to create measurement: {str(e)}")

    @classmethod
    def get_history(cls, db, url: str, limit: int = 10) -> List['WebsiteMetrics']:
        """Get historical measurements for a specific URL with error handling."""
        try:
            return db.query(cls)\
                .filter(cls.url == url)\
                .order_by(cls.timestamp.desc())\
                .limit(limit)\
                .all()
        except Exception as e:
            raise Exception(f"Failed to fetch historical data: {str(e)}")

# Database dependency
@contextmanager
def get_db():
    """Provide a transactional scope around a series of operations."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create tables
Base.metadata.create_all(bind=engine)