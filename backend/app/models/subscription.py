from sqlalchemy import Column, Integer, String, ForeignKey, Enum, Numeric, DateTime
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime
import enum
from app.models.person import Base

class SubscriptionStatus(str, enum.Enum):
    TRIAL = "trial"
    ACTIVE = "active"
    CANCELLED = "cancelled"
    EXPIRED = "expired"

class BillingCycle(str, enum.Enum):
    MONTHLY = "monthly"
    ANNUAL = "annual"

class Subscription(Base):
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    plan_name = Column(String, nullable=False)
    plan_tier = Column(String, nullable=False)
    status = Column(Enum(SubscriptionStatus), default=SubscriptionStatus.TRIAL, nullable=False, index=True)
    billing_cycle = Column(Enum(BillingCycle), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    currency = Column(String, default="USD", nullable=False)
    starts_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    ends_at = Column(DateTime, nullable=True)
    cancelled_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

