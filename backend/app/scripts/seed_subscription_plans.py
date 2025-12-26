import os
import sys
from pathlib import Path
from decimal import Decimal

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine
from app.models.subscription_plan import SubscriptionPlan, Module, SubscriptionPlanModule, Base
from app.models.person import Base as PersonBase

def seed_subscription_plans():
    """Seed default subscription plans with modules"""
    # Ensure tables exist
    PersonBase.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Get all modules by code for easy lookup
        modules_by_code = {}
        all_modules = db.query(Module).all()
        for module in all_modules:
            modules_by_code[module.code] = module
        
        # Define subscription plans with their modules
        plans = [
            {
                "name": "Free",
                "tier": "free",
                "description": "Perfect for individuals and small businesses getting started",
                "price_monthly": Decimal("0.00"),
                "price_annual": Decimal("0.00"),
                "currency": "USD",
                "is_active": True,
                "max_users": 1,
                "max_storage_gb": 1,
                "module_codes": [
                    "categories",
                    "transactions",
                    "reports",
                    "banking"
                ]
            },
            {
                "name": "Basic",
                "tier": "basic",
                "description": "Essential features for growing businesses",
                "price_monthly": Decimal("29.00"),
                "price_annual": Decimal("290.00"),
                "currency": "USD",
                "is_active": True,
                "max_users": 5,
                "max_storage_gb": 10,
                "module_codes": [
                    "categories",
                    "transactions",
                    "reports",
                    "banking",
                    "accounting",
                    "expenses",
                    "income",
                    "invoicing",
                    "payments",
                    "budgeting"
                ]
            },
            {
                "name": "Professional",
                "tier": "professional",
                "description": "Complete financial management for established businesses",
                "price_monthly": Decimal("99.00"),
                "price_annual": Decimal("990.00"),
                "currency": "USD",
                "is_active": True,
                "max_users": None,  # Unlimited
                "max_storage_gb": None,  # Unlimited
                "module_codes": [
                    "categories",
                    "transactions",
                    "reports",
                    "banking",
                    "accounting",
                    "expenses",
                    "income",
                    "invoicing",
                    "payments",
                    "budgeting",
                    "cashflows",
                    "debt_management",
                    "loans",
                    "salary",
                    "tax_management"
                ]
            }
        ]
        
        created_count = 0
        updated_count = 0
        
        for plan_data in plans:
            module_codes = plan_data.pop("module_codes")
            
            # Check if plan already exists by tier
            existing_plan = db.query(SubscriptionPlan).filter(
                SubscriptionPlan.tier == plan_data["tier"]
            ).first()
            
            if existing_plan:
                # Update plan details
                updated = False
                for key, value in plan_data.items():
                    if hasattr(existing_plan, key) and getattr(existing_plan, key) != value:
                        setattr(existing_plan, key, value)
                        updated = True
                
                if updated:
                    db.commit()
                
                # Update modules
                plan = existing_plan
                updated_count += 1
            else:
                # Create new plan
                plan = SubscriptionPlan(**plan_data)
                db.add(plan)
                db.flush()
                created_count += 1
                print(f"Plan '{plan_data['name']}' created successfully")
            
            # Get module IDs from codes
            module_ids = []
            missing_modules = []
            for code in module_codes:
                if code in modules_by_code:
                    module_ids.append(modules_by_code[code].id)
                else:
                    missing_modules.append(code)
            
            if missing_modules:
                print(f"Warning: Modules not found for plan '{plan_data['name']}': {', '.join(missing_modules)}")
            
            # Remove existing plan-module relationships
            db.query(SubscriptionPlanModule).filter(
                SubscriptionPlanModule.plan_id == plan.id
            ).delete()
            
            # Add new module relationships
            for module_id in module_ids:
                plan_module = SubscriptionPlanModule(
                    plan_id=plan.id,
                    module_id=module_id,
                    is_enabled=True
                )
                db.add(plan_module)
            
            db.commit()
            print(f"Plan '{plan_data['name']}' configured with {len(module_ids)} modules")
        
        print(f"\nSubscription plan seeding completed: {created_count} created, {updated_count} updated")
        
    except Exception as e:
        print(f"Error seeding subscription plans: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_subscription_plans()

