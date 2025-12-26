from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, UniqueConstraint
from sqlalchemy.orm import declarative_base
from datetime import datetime
from app.models.person import Base

class PersonCompany(Base):
    __tablename__ = "person_companies"
    
    id = Column(Integer, primary_key=True, index=True)
    person_id = Column(Integer, ForeignKey("people.id"), nullable=False, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    role = Column(String, nullable=False)  # owner, admin, member, viewer
    is_primary = Column(Boolean, default=False, nullable=False)
    joined_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    __table_args__ = (
        UniqueConstraint('person_id', 'company_id', name='uq_person_company'),
    )

