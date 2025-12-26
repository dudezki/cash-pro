from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime
from app.models.tenant.role import Base

class RolePermission(Base):
    __tablename__ = "role_permissions"
    
    id = Column(Integer, primary_key=True, index=True)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False, index=True)
    permission_id = Column(Integer, ForeignKey("permissions.id"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

