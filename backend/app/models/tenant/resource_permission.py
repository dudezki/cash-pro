from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime
from app.models.tenant.role import Base

class ResourcePermission(Base):
    __tablename__ = "resource_permissions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)  # References control DB people.id
    resource_type = Column(String, nullable=False, index=True)
    resource_id = Column(Integer, nullable=False, index=True)
    permission = Column(String, nullable=False)  # e.g., "read", "write", "delete"
    granted_at = Column(DateTime, default=datetime.utcnow, nullable=False)

