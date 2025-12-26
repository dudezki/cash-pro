from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class ModuleBase(BaseModel):
    name: str
    code: str
    description: Optional[str] = None
    category: Optional[str] = None
    is_active: bool = True


class ModuleCreate(ModuleBase):
    pass


class ModuleUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    is_active: Optional[bool] = None


class ModuleResponse(ModuleBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class SubscriptionPlanModuleResponse(BaseModel):
    id: int
    plan_id: int
    module_id: int
    is_enabled: bool
    module: ModuleResponse
    
    class Config:
        from_attributes = True


class SubscriptionPlanBase(BaseModel):
    name: str
    tier: str
    description: Optional[str] = None
    price_monthly: float
    price_annual: float
    currency: str = "USD"
    is_active: bool = True
    max_users: Optional[int] = None
    max_storage_gb: Optional[int] = None


class SubscriptionPlanCreate(SubscriptionPlanBase):
    module_ids: Optional[List[int]] = None  # List of module IDs to enable


class SubscriptionPlanUpdate(BaseModel):
    name: Optional[str] = None
    tier: Optional[str] = None
    description: Optional[str] = None
    price_monthly: Optional[float] = None
    price_annual: Optional[float] = None
    currency: Optional[str] = None
    is_active: Optional[bool] = None
    max_users: Optional[int] = None
    max_storage_gb: Optional[int] = None
    module_ids: Optional[List[int]] = None  # Update modules


class SubscriptionPlanResponse(SubscriptionPlanBase):
    id: int
    created_at: datetime
    updated_at: datetime
    modules: List[SubscriptionPlanModuleResponse] = []
    
    class Config:
        from_attributes = True


class SubscriptionPlanDetailResponse(SubscriptionPlanResponse):
    """Extended response with statistics"""
    total_subscribers: int = 0
    active_subscribers: int = 0
    trial_subscribers: int = 0
    cancelled_subscribers: int = 0
    expired_subscribers: int = 0
    total_companies: int = 0
    enabled_modules_count: int = 0

