from sqlalchemy.orm import Session
from app.core.database import get_tenant_db, create_database
from app.models.company import Company
from typing import Optional

def get_tenant_database_name(company_id: int, company_slug: str) -> str:
    """Generate tenant database name"""
    # Use slug for readability, fallback to ID
    safe_slug = company_slug.lower().replace("-", "_").replace(" ", "_")
    return f"tenant_{safe_slug}_{company_id}"

def ensure_tenant_database(db: Session, company: Company) -> Optional[str]:
    """Ensure tenant database exists, create if not"""
    if company.database_name:
        return company.database_name
    
    database_name = get_tenant_database_name(company.id, company.slug)
    
    # Create database if it doesn't exist
    created = create_database(database_name)
    
    if created or not company.database_name:
        # Update company record
        company.database_name = database_name
        db.commit()
        db.refresh(company)
    
    return database_name

