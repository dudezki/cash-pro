from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.middleware import require_auth, get_current_person, get_current_company
from app.core.security import verify_password, get_password_hash, generate_session_token, hash_session_token, get_session_expiry
from app.models.person import Person
from app.models.company import Company
from app.models.person_company import PersonCompany
from app.models.subscription import Subscription, SubscriptionStatus, BillingCycle
from app.models.session import Session as SessionModel
from app.models.company_setting import CompanySetting
from app.schemas.auth import RegisterRequest, LoginRequest, AuthResponse, PersonResponse, CompanyResponse, SwitchCompanyRequest
from app.services.tenant_db import create_tenant_database
from datetime import datetime
import re

router = APIRouter()

def generate_slug(name: str) -> str:
    """Generate URL-friendly slug from name"""
    slug = name.lower()
    slug = re.sub(r'[^a-z0-9]+', '-', slug)
    slug = re.sub(r'^-+|-+$', '', slug)
    return slug

@router.post("/register", response_model=AuthResponse)
async def register(
    request_data: RegisterRequest,
    response: Response,
    db: Session = Depends(get_db)
):
    """Register a new user (Person only, no Company/Subscription)"""
    # Check if email already exists
    existing_person = db.query(Person).filter(Person.email == request_data.email).first()
    if existing_person:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Generate username from email
    username = request_data.email.split('@')[0]
    # Ensure unique username
    base_username = username
    counter = 1
    while db.query(Person).filter(Person.username == username).first():
        username = f"{base_username}{counter}"
        counter += 1
    
    # Create person only (no company, no subscription)
    hashed_password = get_password_hash(request_data.password)
    person = Person(
        email=request_data.email,
        username=username,
        hashed_password=hashed_password,
        first_name=request_data.first_name,
        last_name=request_data.last_name,
        is_active=True,
        is_verified=False
    )
    db.add(person)
    db.commit()
    db.refresh(person)
    
    # Create session (no company_id since user has no organization yet)
    session_token = generate_session_token()
    token_hash = hash_session_token(session_token)
    expires_at = get_session_expiry()
    
    session = SessionModel(
        person_id=person.id,
        company_id=None,  # No company yet
        session_token=token_hash,
        expires_at=expires_at,
        ip_address=None,
        user_agent=None
    )
    db.add(session)
    db.commit()
    
    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=60 * 60 * 24 * 7
    )
    
    return AuthResponse(
        person=PersonResponse.model_validate(person),
        companies=[],  # No companies yet
        current_company_id=None,  # No company yet
        is_impersonating=False
    )

@router.post("/login", response_model=AuthResponse)
async def login(
    request_data: LoginRequest,
    response: Response,
    db: Session = Depends(get_db)
):
    """Login and create session - accepts email or username"""
    # Try to find person by email or username
    # Check if input contains @ to determine if it's an email
    login_identifier = request_data.email_or_username.strip()
    
    if '@' in login_identifier:
        # Treat as email
        person = db.query(Person).filter(Person.email == login_identifier).first()
    else:
        # Treat as username
        person = db.query(Person).filter(Person.username == login_identifier).first()
    
    # If not found by username, try email as fallback (for backwards compatibility)
    if not person:
        person = db.query(Person).filter(Person.email == login_identifier).first()
    
    if not person:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email/username or password"
        )
    
    if not verify_password(request_data.password, person.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email/username or password"
        )
    
    if not person.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is inactive"
        )
    
    # Get primary company
    person_company = db.query(PersonCompany).filter(
        PersonCompany.person_id == person.id,
        PersonCompany.is_primary == True
    ).first()
    
    if not person_company:
        # Get any company
        person_company = db.query(PersonCompany).filter(
            PersonCompany.person_id == person.id
        ).first()
    
    company_id = person_company.company_id if person_company else None
    
    # Create session
    session_token = generate_session_token()
    token_hash = hash_session_token(session_token)
    expires_at = get_session_expiry()
    
    session = SessionModel(
        person_id=person.id,
        company_id=company_id,
        session_token=token_hash,
        expires_at=expires_at
    )
    db.add(session)
    db.commit()
    
    # Get all companies
    person_companies = db.query(PersonCompany).filter(
        PersonCompany.person_id == person.id
    ).all()
    companies = [db.query(Company).filter(Company.id == pc.company_id).first() for pc in person_companies]
    
    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=60 * 60 * 24 * 7
    )
    
    return AuthResponse(
        person=PersonResponse.model_validate(person),
        companies=[CompanyResponse.model_validate(c) for c in companies],
        current_company_id=company_id,
        is_impersonating=session.impersonated_by is not None
    )

@router.post("/logout")
async def logout(
    request: Request,
    response: Response,
    db: Session = Depends(get_db)
):
    """Logout and invalidate session"""
    session_token = request.cookies.get("session_token")
    if session_token:
        token_hash = hash_session_token(session_token)
        session = db.query(SessionModel).filter(
            SessionModel.session_token == token_hash
        ).first()
        if session:
            db.delete(session)
            db.commit()
    
    response.delete_cookie(key="session_token")
    return {"message": "Logged out successfully"}

@router.get("/me", response_model=AuthResponse)
async def get_current_user(
    request: Request,
    db: Session = Depends(get_db)
):
    """Get current authenticated user"""
    person = require_auth(request, db)
    
    # Get current company from session
    session_token = request.cookies.get("session_token")
    company_id = None
    is_impersonating = False
    
    if session_token:
        token_hash = hash_session_token(session_token)
        session = db.query(SessionModel).filter(
            SessionModel.session_token == token_hash
        ).first()
        if session:
            company_id = session.company_id
            is_impersonating = session.impersonated_by is not None
    
    # Get all companies
    person_companies = db.query(PersonCompany).filter(
        PersonCompany.person_id == person.id
    ).all()
    companies = [db.query(Company).filter(Company.id == pc.company_id).first() for pc in person_companies]
    
    return AuthResponse(
        person=PersonResponse.model_validate(person),
        companies=[CompanyResponse.model_validate(c) for c in companies],
        current_company_id=company_id,
        is_impersonating=is_impersonating
    )

@router.post("/switch-company")
async def switch_company(
    request_data: SwitchCompanyRequest,
    request: Request,
    response: Response,
    db: Session = Depends(get_db)
):
    """Switch current company context"""
    person = require_auth(request, db)
    
    # Verify person has access to company
    person_company = db.query(PersonCompany).filter(
        PersonCompany.person_id == person.id,
        PersonCompany.company_id == request_data.company_id
    ).first()
    
    if not person_company:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this company"
        )
    
    # Update session
    session_token = request.cookies.get("session_token")
    if session_token:
        token_hash = hash_session_token(session_token)
        session = db.query(SessionModel).filter(
            SessionModel.session_token == token_hash
        ).first()
        if session:
            session.company_id = request_data.company_id
            db.commit()
    
    return {"message": "Company switched successfully", "company_id": request_data.company_id}

