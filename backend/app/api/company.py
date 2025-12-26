from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.middleware import require_auth, get_current_person
from app.models.company import Company
from app.models.person_company import PersonCompany
from app.models.company_setting import CompanySetting
from app.schemas.company import CreateCompanyRequest
from app.schemas.auth import CompanyResponse
from app.services.tenant_db import create_tenant_database
import re

router = APIRouter()

def generate_slug(name: str) -> str:
    """Generate URL-friendly slug from name"""
    slug = name.lower()
    slug = re.sub(r'[^a-z0-9]+', '-', slug)
    slug = re.sub(r'^-+|-+$', '', slug)
    return slug

@router.post("", response_model=CompanyResponse)
async def create_company(
    request_data: CreateCompanyRequest,
    request: Request,
    response: Response,
    db: Session = Depends(get_db)
):
    """Create a new company for the authenticated user"""
    person = require_auth(request, db)
    
    # Check if user already has a company
    existing_company = db.query(PersonCompany).filter(
        PersonCompany.person_id == person.id
    ).first()
    
    if existing_company:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already has a company"
        )
    
    # Generate slug
    slug = generate_slug(request_data.name)
    
    # Ensure unique slug
    base_slug = slug
    counter = 1
    while db.query(Company).filter(Company.slug == slug).first():
        slug = f"{base_slug}-{counter}"
        counter += 1
    
    # Create company
    company = Company(
        name=request_data.name,
        slug=slug,
        legal_name=request_data.legal_name,
        tax_id=request_data.tax_id,
        address_line1=request_data.address_line1,
        address_line2=request_data.address_line2,
        city=request_data.city,
        state=request_data.state,
        postal_code=request_data.postal_code,
        country=request_data.country,
        phone=request_data.phone,
        website=request_data.website
    )
    db.add(company)
    db.flush()
    
    # Create PersonCompany relationship (owner)
    person_company = PersonCompany(
        person_id=person.id,
        company_id=company.id,
        role="owner",
        is_primary=True
    )
    db.add(person_company)
    
    # Create company settings
    company_setting = CompanySetting(
        company_id=company.id
    )
    db.add(company_setting)
    
    db.commit()
    db.refresh(company)
    
    return CompanyResponse.model_validate(company)

