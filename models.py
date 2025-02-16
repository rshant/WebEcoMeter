from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from datetime import datetime

# Database connection
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class WebsiteMetrics(Base):
    """Model for storing historical website carbon footprint measurements."""
    __tablename__ = "website_metrics"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    page_size_kb = Column(Float)
    monthly_visits = Column(Integer)
    annual_energy_kwh = Column(Float)
    annual_carbon_kg = Column(Float)
    trees_needed = Column(Integer)

    @classmethod
    def create_measurement(cls, db, url: str, metrics: dict, monthly_visits: int):
        """Create a new measurement record."""
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

    @classmethod
    def get_history(cls, db, url: str, limit: int = 10):
        """Get historical measurements for a specific URL."""
        return db.query(cls).filter(cls.url == url)\
            .order_by(cls.timestamp.desc())\
            .limit(limit)\
            .all()

# Create tables
Base.metadata.create_all(bind=engine)

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
