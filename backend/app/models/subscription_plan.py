from sqlalchemy import Column, Integer, String, Numeric, Boolean, DateTime, Text, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.person import Base


class SubscriptionPlan(Base):
    """Subscription plan template that defines available plans"""
    __tablename__ = "subscription_plans"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True, index=True)
    tier = Column(String, nullable=False, unique=True, index=True)  # trial, starter, professional, enterprise
    description = Column(Text, nullable=True)
    price_monthly = Column(Numeric(10, 2), nullable=False, default=0.00)
    price_annual = Column(Numeric(10, 2), nullable=False, default=0.00)
    currency = Column(String, default="USD", nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    max_users = Column(Integer, nullable=True)  # null = unlimited
    max_storage_gb = Column(Integer, nullable=True)  # null = unlimited
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationship to modules
    modules = relationship("SubscriptionPlanModule", back_populates="plan", cascade="all, delete-orphan")


class Module(Base):
    """Available modules/features that can be assigned to plans"""
    __tablename__ = "modules"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True, index=True)
    code = Column(String, nullable=False, unique=True, index=True)  # e.g., "invoices", "reports", "analytics"
    description = Column(Text, nullable=True)
    category = Column(String, nullable=True)  # e.g., "financial", "reporting", "advanced"
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationship to plans
    plan_modules = relationship("SubscriptionPlanModule", back_populates="module")


class SubscriptionPlanModule(Base):
    """Junction table linking subscription plans to modules"""
    __tablename__ = "subscription_plan_modules"
    
    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey("subscription_plans.id", ondelete="CASCADE"), nullable=False, index=True)
    module_id = Column(Integer, ForeignKey("modules.id", ondelete="CASCADE"), nullable=False, index=True)
    is_enabled = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    plan = relationship("SubscriptionPlan", back_populates="modules")
    module = relationship("Module", back_populates="plan_modules")
    
    # Unique constraint: one plan-module combination
    __table_args__ = (
        UniqueConstraint('plan_id', 'module_id', name='uq_plan_module'),
    )

