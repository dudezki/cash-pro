from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.middleware import require_auth, require_super_admin
from app.models.subscription_plan import SubscriptionPlan, Module, SubscriptionPlanModule
from app.schemas.subscription_plan import (
    SubscriptionPlanCreate,
    SubscriptionPlanUpdate,
    SubscriptionPlanResponse,
    SubscriptionPlanDetailResponse,
    ModuleCreate,
    ModuleUpdate,
    ModuleResponse
)
from app.models.subscription import Subscription, SubscriptionStatus

router = APIRouter()


# ============ Subscription Plan Endpoints ============

@router.get("/plans", response_model=List[SubscriptionPlanResponse])
async def list_plans(
    request: Request,
    db: Session = Depends(get_db),
    active_only: bool = False
):
    """List all subscription plans (super admin only)"""
    require_super_admin(request, db)
    
    query = db.query(SubscriptionPlan)
    if active_only:
        query = query.filter(SubscriptionPlan.is_active == True)
    
    plans = query.order_by(SubscriptionPlan.price_monthly.asc()).all()
    return plans


@router.post("/plans", response_model=SubscriptionPlanResponse, status_code=status.HTTP_201_CREATED)
async def create_plan(
    plan_data: SubscriptionPlanCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    """Create a new subscription plan (super admin only)"""
    require_super_admin(request, db)
    
    # Check if tier already exists
    existing = db.query(SubscriptionPlan).filter(
        SubscriptionPlan.tier == plan_data.tier
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Plan with tier '{plan_data.tier}' already exists"
        )
    
    # Create plan
    plan = SubscriptionPlan(
        name=plan_data.name,
        tier=plan_data.tier,
        description=plan_data.description,
        price_monthly=plan_data.price_monthly,
        price_annual=plan_data.price_annual,
        currency=plan_data.currency,
        is_active=plan_data.is_active,
        max_users=plan_data.max_users,
        max_storage_gb=plan_data.max_storage_gb
    )
    db.add(plan)
    db.flush()
    
    # Add modules if provided
    if plan_data.module_ids:
        for module_id in plan_data.module_ids:
            # Verify module exists
            module = db.query(Module).filter(Module.id == module_id).first()
            if not module:
                db.rollback()
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Module with id {module_id} not found"
                )
            
            plan_module = SubscriptionPlanModule(
                plan_id=plan.id,
                module_id=module_id,
                is_enabled=True
            )
            db.add(plan_module)
    
    db.commit()
    db.refresh(plan)
    return plan


@router.get("/plans/{plan_id}", response_model=SubscriptionPlanDetailResponse)
async def get_plan(
    plan_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """Get a specific subscription plan with statistics (super admin only)"""
    require_super_admin(request, db)
    
    plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan not found"
        )
    
    # Get subscription statistics
    subscriptions = db.query(Subscription).filter(Subscription.plan_tier == plan.tier).all()
    
    total_subscribers = len(subscriptions)
    active_subscribers = len([s for s in subscriptions if s.status == SubscriptionStatus.ACTIVE])
    trial_subscribers = len([s for s in subscriptions if s.status == SubscriptionStatus.TRIAL])
    cancelled_subscribers = len([s for s in subscriptions if s.status == SubscriptionStatus.CANCELLED])
    expired_subscribers = len([s for s in subscriptions if s.status == SubscriptionStatus.EXPIRED])
    
    # Get unique companies subscribed to this plan
    company_ids = list(set([s.company_id for s in subscriptions]))
    total_companies = len(company_ids)
    
    # Count enabled modules
    enabled_modules_count = len([pm for pm in plan.modules if pm.is_enabled])
    
    # Create response with statistics
    plan_dict = {
        **SubscriptionPlanResponse.model_validate(plan).model_dump(),
        "total_subscribers": total_subscribers,
        "active_subscribers": active_subscribers,
        "trial_subscribers": trial_subscribers,
        "cancelled_subscribers": cancelled_subscribers,
        "expired_subscribers": expired_subscribers,
        "total_companies": total_companies,
        "enabled_modules_count": enabled_modules_count
    }
    
    return SubscriptionPlanDetailResponse(**plan_dict)


@router.put("/plans/{plan_id}", response_model=SubscriptionPlanResponse)
async def update_plan(
    plan_id: int,
    plan_data: SubscriptionPlanUpdate,
    request: Request,
    db: Session = Depends(get_db)
):
    """Update a subscription plan (super admin only)"""
    require_super_admin(request, db)
    
    plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan not found"
        )
    
    # Check tier uniqueness if tier is being updated
    if plan_data.tier and plan_data.tier != plan.tier:
        existing = db.query(SubscriptionPlan).filter(
            SubscriptionPlan.tier == plan_data.tier,
            SubscriptionPlan.id != plan_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Plan with tier '{plan_data.tier}' already exists"
            )
    
    # Update plan fields
    update_data = plan_data.model_dump(exclude_unset=True, exclude={'module_ids'})
    for field, value in update_data.items():
        setattr(plan, field, value)
    
    # Update modules if provided
    if plan_data.module_ids is not None:
        # Remove existing plan-module relationships
        db.query(SubscriptionPlanModule).filter(
            SubscriptionPlanModule.plan_id == plan_id
        ).delete()
        
        # Add new relationships
        for module_id in plan_data.module_ids:
            module = db.query(Module).filter(Module.id == module_id).first()
            if not module:
                db.rollback()
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Module with id {module_id} not found"
                )
            
            plan_module = SubscriptionPlanModule(
                plan_id=plan.id,
                module_id=module_id,
                is_enabled=True
            )
            db.add(plan_module)
    
    db.commit()
    db.refresh(plan)
    return plan


@router.delete("/plans/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_plan(
    plan_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """Delete a subscription plan (super admin only)"""
    require_super_admin(request, db)
    
    plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan not found"
        )
    
    db.delete(plan)
    db.commit()
    return None


# ============ Module Endpoints ============

@router.get("/modules", response_model=List[ModuleResponse])
async def list_modules(
    request: Request,
    db: Session = Depends(get_db),
    active_only: bool = False
):
    """List all modules (super admin only)"""
    require_super_admin(request, db)
    
    query = db.query(Module)
    if active_only:
        query = query.filter(Module.is_active == True)
    
    modules = query.order_by(Module.category.asc(), Module.name.asc()).all()
    return modules


@router.post("/modules", response_model=ModuleResponse, status_code=status.HTTP_201_CREATED)
async def create_module(
    module_data: ModuleCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    """Create a new module (super admin only)"""
    require_super_admin(request, db)
    
    # Check if code already exists
    existing = db.query(Module).filter(Module.code == module_data.code).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Module with code '{module_data.code}' already exists"
        )
    
    module = Module(**module_data.model_dump())
    db.add(module)
    db.commit()
    db.refresh(module)
    return module


@router.get("/modules/{module_id}", response_model=ModuleResponse)
async def get_module(
    module_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """Get a specific module (super admin only)"""
    require_super_admin(request, db)
    
    module = db.query(Module).filter(Module.id == module_id).first()
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module not found"
        )
    return module


@router.put("/modules/{module_id}", response_model=ModuleResponse)
async def update_module(
    module_id: int,
    module_data: ModuleUpdate,
    request: Request,
    db: Session = Depends(get_db)
):
    """Update a module (super admin only)"""
    require_super_admin(request, db)
    
    module = db.query(Module).filter(Module.id == module_id).first()
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module not found"
        )
    
    # Check code uniqueness if code is being updated
    if module_data.code and module_data.code != module.code:
        existing = db.query(Module).filter(
            Module.code == module_data.code,
            Module.id != module_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Module with code '{module_data.code}' already exists"
            )
    
    update_data = module_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(module, field, value)
    
    db.commit()
    db.refresh(module)
    return module


@router.delete("/modules/{module_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_module(
    module_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """Delete a module (super admin only)"""
    require_super_admin(request, db)
    
    module = db.query(Module).filter(Module.id == module_id).first()
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Module not found"
        )
    
    db.delete(module)
    db.commit()
    return None

