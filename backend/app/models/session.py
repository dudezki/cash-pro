from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime
from app.models.person import Base

class Session(Base):
    __tablename__ = "sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    person_id = Column(Integer, ForeignKey("people.id"), nullable=False, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True, index=True)
    session_token = Column(String, unique=True, index=True, nullable=False)
    expires_at = Column(DateTime, nullable=False, index=True)
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    impersonated_by = Column(Integer, ForeignKey("people.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

