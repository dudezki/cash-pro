from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.subscription import SubscriptionStatus, BillingCycle

class CreateSubscriptionRequest(BaseModel):
    plan_name: str
    plan_tier: str
    billing_cycle: BillingCycle
    price: float
    currency: str = "USD"

class SubscriptionResponse(BaseModel):
    id: int
    company_id: int
    plan_name: str
    plan_tier: str
    status: SubscriptionStatus
    billing_cycle: BillingCycle
    price: float
    currency: str
    starts_at: datetime
    ends_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

