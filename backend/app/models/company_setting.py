from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, JSON
from sqlalchemy.orm import declarative_base
from datetime import datetime
from app.models.person import Base

class CompanySetting(Base):
    __tablename__ = "company_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), unique=True, nullable=False, index=True)
    timezone = Column(String, default="UTC", nullable=False)
    locale = Column(String, default="en_US", nullable=False)
    currency = Column(String, default="USD", nullable=False)
    settings_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

