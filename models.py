from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
import os
from datetime import datetime
from contextlib import contextmanager
from typing import List, Optional
import time

# Database connection with retries
def create_db_engine(retries=3, delay=1):
    """Create database engine with connection retries."""
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

    for attempt in range(retries):
        try:
            return create_engine(
                DATABASE_URL,
                poolclass=QueuePool,
                pool_size=5,
                max_overflow=10,
                pool_timeout=30,
                pool_recycle=1800,
                pool_pre_ping=True,
                connect_args={
                    'connect_timeout': 10,
                    'keepalives': 1,
                    'keepalives_idle': 30,
                    'keepalives_interval': 10,
                    'keepalives_count': 5
                }
            )
        except Exception as e:
            if attempt == retries - 1:
                raise Exception(f"Failed to create database engine after {retries} attempts: {str(e)}")
            time.sleep(delay)

engine = create_db_engine()
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
        """Create a new measurement record with error handling and retries."""
        max_retries = 3
        retry_delay = 1

        for attempt in range(max_retries):
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
                if attempt == max_retries - 1:
                    raise Exception(f"Failed to create measurement after {max_retries} attempts: {str(e)}")
                time.sleep(retry_delay)

    @classmethod
    def get_history(cls, db, url: str, limit: int = 10) -> List['WebsiteMetrics']:
        """Get historical measurements for a specific URL with error handling and retries."""
        max_retries = 3
        retry_delay = 1

        for attempt in range(max_retries):
            try:
                return db.query(cls)\
                    .filter(cls.url == url)\
                    .order_by(cls.timestamp.desc())\
                    .limit(limit)\
                    .all()
            except Exception as e:
                if attempt == max_retries - 1:
                    raise Exception(f"Failed to fetch historical data after {max_retries} attempts: {str(e)}")
                time.sleep(retry_delay)

@contextmanager
def get_db():
    """Provide a transactional scope around a series of operations with connection handling."""
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()
        raise
    finally:
        db.close()

# Create tables
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    raise Exception(f"Failed to create database tables: {str(e)}")