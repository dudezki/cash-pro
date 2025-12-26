from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.middleware import require_super_admin, require_auth, get_current_person
from app.core.security import generate_session_token, hash_session_token, get_session_expiry, get_password_hash
from app.models.person import Person
from app.models.company import Company
from app.models.session import Session as SessionModel
from app.schemas.admin import UserResponse, CompanyDetailResponse, ImpersonateRequest, CreateUserRequest
from app.schemas.auth import PersonResponse, CompanyResponse
from app.services.tenant_db import create_tenant_database
from typing import List

router = APIRouter()

@router.get("/users", response_model=List[UserResponse])
async def list_users(
    request: Request,
    db: Session = Depends(get_db)
):
    """List all users (super admin only)"""
    require_super_admin(request, db)
    
    users = db.query(Person).all()
    return [UserResponse.model_validate(user) for user in users]

@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: CreateUserRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """Create a new user (super admin only)"""
    require_super_admin(request, db)
    
    # Check if email already exists
    existing_email = db.query(Person).filter(Person.email == user_data.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User with email '{user_data.email}' already exists"
        )
    
    # Check if username already exists (if provided)
    if user_data.username:
        existing_username = db.query(Person).filter(Person.username == user_data.username).first()
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User with username '{user_data.username}' already exists"
            )
    
    # Hash password
    hashed_password = get_password_hash(user_data.password)
    
    # Create user
    user = Person(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        phone=user_data.phone,
        is_active=user_data.is_active,
        is_verified=user_data.is_verified,
        is_super_admin=user_data.is_super_admin
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return UserResponse.model_validate(user)

@router.get("/companies", response_model=List[CompanyDetailResponse])
async def list_companies(
    request: Request,
    db: Session = Depends(get_db)
):
    """List all companies (super admin only)"""
    require_super_admin(request, db)
    
    companies = db.query(Company).all()
    result = []
    for company in companies:
        result.append(CompanyDetailResponse(
            id=company.id,
            name=company.name,
            slug=company.slug,
            database_name=company.database_name,
            created_at=company.created_at,
            has_database=company.database_name is not None
        ))
    return result

@router.post("/impersonate/{user_id}")
async def impersonate_user(
    user_id: int,
    request: Request,
    response: Response,
    db: Session = Depends(get_db)
):
    """Impersonate a user (super admin only)"""
    super_admin = require_super_admin(request, db)
    
    target_user = db.query(Person).filter(Person.id == user_id).first()
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Create impersonation session
    session_token = generate_session_token()
    token_hash = hash_session_token(session_token)
    expires_at = get_session_expiry()
    
    session = SessionModel(
        person_id=target_user.id,
        company_id=None,  # Will be set when user switches company
        session_token=token_hash,
        expires_at=expires_at,
        impersonated_by=super_admin.id
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
    
    return {
        "message": f"Impersonating user {target_user.email}",
        "user": PersonResponse.model_validate(target_user)
    }

@router.post("/stop-impersonate")
async def stop_impersonate(
    request: Request,
    response: Response,
    db: Session = Depends(get_db)
):
    """Stop impersonating and return to super admin session"""
    super_admin = require_super_admin(request, db)
    
    # Get current impersonation session
    session_token = request.cookies.get("session_token")
    if session_token:
        from app.core.security import hash_session_token
        token_hash = hash_session_token(session_token)
        session = db.query(SessionModel).filter(
            SessionModel.session_token == token_hash
        ).first()
        if session and session.impersonated_by:
            # Delete impersonation session
            db.delete(session)
            db.commit()
    
    # Create new super admin session
    session_token = generate_session_token()
    token_hash = hash_session_token(session_token)
    expires_at = get_session_expiry()
    
    session = SessionModel(
        person_id=super_admin.id,
        company_id=None,
        session_token=token_hash,
        expires_at=expires_at,
        impersonated_by=None
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
    
    return {
        "message": "Stopped impersonating",
        "user": PersonResponse.model_validate(super_admin)
    }

@router.post("/companies/{company_id}/create-db")
async def create_company_database(
    company_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """Manually create tenant database for a company (super admin only)"""
    require_super_admin(request, db)
    
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    if company.database_name:
        return {
            "message": "Database already exists",
            "database_name": company.database_name
        }
    
    try:
        database_name = create_tenant_database(company.id, company.slug, db)
        return {
            "message": "Database created successfully",
            "database_name": database_name
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating database: {str(e)}"
        )

