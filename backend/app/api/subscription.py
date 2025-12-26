from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.middleware import require_auth, get_current_person, get_current_company
from app.models.company import Company
from app.models.subscription import Subscription, SubscriptionStatus, BillingCycle
from app.models.person_company import PersonCompany
from app.schemas.subscription import CreateSubscriptionRequest, SubscriptionResponse
from app.services.tenant_db import create_tenant_database
from datetime import datetime, timedelta

router = APIRouter()

@router.post("", response_model=SubscriptionResponse)
async def create_subscription(
    request_data: CreateSubscriptionRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """Create a subscription for the user's company"""
    person = require_auth(request, db)
    
    # Get user's company
    person_company = db.query(PersonCompany).filter(
        PersonCompany.person_id == person.id,
        PersonCompany.role == "owner"
    ).first()
    
    if not person_company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No company found. Please create a company first."
        )
    
    company = db.query(Company).filter(Company.id == person_company.company_id).first()
    
    # Check if company already has an active subscription
    existing_subscription = db.query(Subscription).filter(
        Subscription.company_id == company.id,
        Subscription.status.in_([SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIAL])
    ).first()
    
    if existing_subscription:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Company already has an active subscription"
        )
    
    # Calculate end date based on billing cycle
    starts_at = datetime.utcnow()
    if request_data.billing_cycle == BillingCycle.MONTHLY:
        ends_at = starts_at + timedelta(days=30)
    else:  # Annual
        ends_at = starts_at + timedelta(days=365)
    
    # Create subscription
    subscription = Subscription(
        company_id=company.id,
        plan_name=request_data.plan_name,
        plan_tier=request_data.plan_tier,
        status=SubscriptionStatus.ACTIVE,  # Activate immediately
        billing_cycle=request_data.billing_cycle,
        price=request_data.price,
        currency=request_data.currency,
        starts_at=starts_at,
        ends_at=ends_at
    )
    db.add(subscription)
    db.commit()
    db.refresh(subscription)
    
    # Create tenant database when subscription is activated
    try:
        database_name = create_tenant_database(company.id, company.slug, db)
        print(f"Tenant database '{database_name}' created for company '{company.name}'")
    except Exception as e:
        print(f"Error creating tenant database: {e}")
        # Don't fail the subscription creation if DB creation fails
        # It can be created manually later
    
    return SubscriptionResponse.model_validate(subscription)

@router.get("/plans")
async def get_available_plans(db: Session = Depends(get_db)):
    """Get available subscription plans (active plans from database)"""
    plans = db.query(SubscriptionPlan).filter(
        SubscriptionPlan.is_active == True
    ).order_by(SubscriptionPlan.price_monthly.asc()).all()
    
    result = []
    for plan in plans:
        # Get module names for features
        module_names = [pm.module.name for pm in plan.modules if pm.is_enabled]
        
        result.append({
            "id": plan.tier,
            "name": plan.name,
            "tier": plan.tier,
            "billing_cycle": "monthly",
            "price": float(plan.price_monthly),
            "currency": plan.currency,
            "features": module_names if module_names else [plan.description] if plan.description else []
        })
    
    return {"plans": result}

