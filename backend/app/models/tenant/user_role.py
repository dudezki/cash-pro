from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime
from app.models.tenant.role import Base

class UserRole(Base):
    __tablename__ = "user_roles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)  # References control DB people.id
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False, index=True)
    company_id = Column(Integer, nullable=False, index=True)  # References control DB company
    assigned_at = Column(DateTime, default=datetime.utcnow, nullable=False)

