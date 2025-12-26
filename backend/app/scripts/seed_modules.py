import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine
from app.models.subscription_plan import Module, Base
from app.models.person import Base as PersonBase

def seed_modules():
    """Seed all financial modules into the database"""
    # Ensure tables exist
    PersonBase.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Define all financial modules
        modules = [
            {
                "name": "Accounting",
                "code": "accounting",
                "description": "Core accounting and bookkeeping with double-entry accounting principles",
                "category": "Financial",
                "is_active": True
            },
            {
                "name": "Cashflows",
                "code": "cashflows",
                "description": "Cash flow tracking and management",
                "category": "Financial",
                "is_active": True
            },
            {
                "name": "Debt Management",
                "code": "debt_management",
                "description": "Track and manage debts",
                "category": "Financial",
                "is_active": True
            },
            {
                "name": "Loans",
                "code": "loans",
                "description": "Loan management and tracking",
                "category": "Financial",
                "is_active": True
            },
            {
                "name": "Categories",
                "code": "categories",
                "description": "Transaction and expense categorization",
                "category": "Financial",
                "is_active": True
            },
            {
                "name": "Transactions",
                "code": "transactions",
                "description": "General transaction management with double-entry accounting",
                "category": "Financial",
                "is_active": True
            },
            {
                "name": "Expenses",
                "code": "expenses",
                "description": "Expense tracking and management",
                "category": "Financial",
                "is_active": True
            },
            {
                "name": "Salary",
                "code": "salary",
                "description": "Salary and payroll management",
                "category": "Financial",
                "is_active": True
            },
            {
                "name": "Income",
                "code": "income",
                "description": "Income tracking and recording",
                "category": "Financial",
                "is_active": True
            },
            {
                "name": "Reports",
                "code": "reports",
                "description": "Financial reports and analytics",
                "category": "Financial",
                "is_active": True
            },
            {
                "name": "Banking",
                "code": "banking",
                "description": "Bank account management and reconciliation",
                "category": "Financial",
                "is_active": True
            },
            {
                "name": "Invoicing",
                "code": "invoicing",
                "description": "Invoice creation and management",
                "category": "Financial",
                "is_active": True
            },
            {
                "name": "Payments",
                "code": "payments",
                "description": "Payment processing and tracking",
                "category": "Financial",
                "is_active": True
            },
            {
                "name": "Budgeting",
                "code": "budgeting",
                "description": "Budget planning and tracking",
                "category": "Financial",
                "is_active": True
            },
            {
                "name": "Tax Management",
                "code": "tax_management",
                "description": "Tax calculation and reporting",
                "category": "Financial",
                "is_active": True
            }
        ]
        
        created_count = 0
        skipped_count = 0
        
        for module_data in modules:
            # Check if module already exists by code
            existing = db.query(Module).filter(Module.code == module_data["code"]).first()
            
            if existing:
                # Update if needed
                updated = False
                for key, value in module_data.items():
                    if hasattr(existing, key) and getattr(existing, key) != value:
                        setattr(existing, key, value)
                        updated = True
                
                if updated:
                    db.commit()
                    print(f"Module '{module_data['name']}' updated")
                else:
                    skipped_count += 1
            else:
                # Create new module
                module = Module(**module_data)
                db.add(module)
                db.commit()
                db.refresh(module)
                created_count += 1
                print(f"Module '{module_data['name']}' created successfully")
        
        print(f"\nModule seeding completed: {created_count} created, {skipped_count} already existed")
        
    except Exception as e:
        print(f"Error seeding modules: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_modules()

