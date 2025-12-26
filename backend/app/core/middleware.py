from fastapi import Request, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.session import Session as SessionModel
from app.models.person import Person
from app.models.company import Company
from datetime import datetime
from typing import Optional

def get_current_session(request: Request, db: Session) -> Optional[SessionModel]:
    """Get current session from cookie"""
    session_token = request.cookies.get("session_token")
    if not session_token:
        return None
    
    # Hash token for lookup
    from app.core.security import hash_session_token
    token_hash = hash_session_token(session_token)
    
    session = db.query(SessionModel).filter(
        SessionModel.session_token == token_hash,
        SessionModel.expires_at > datetime.utcnow()
    ).first()
    
    return session

def get_current_person(request: Request, db: Session) -> Optional[Person]:
    """Get current authenticated person"""
    session = get_current_session(request, db)
    if not session:
        return None
    
    return db.query(Person).filter(Person.id == session.person_id).first()

def get_current_company(request: Request, db: Session) -> Optional[Company]:
    """Get current company context from session"""
    session = get_current_session(request, db)
    if not session or not session.company_id:
        return None
    
    return db.query(Company).filter(Company.id == session.company_id).first()

def require_auth(request: Request, db: Session) -> Person:
    """Require authentication, raise 401 if not authenticated"""
    person = get_current_person(request, db)
    if not person:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    if not person.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is inactive"
        )
    return person

def require_super_admin(request: Request, db: Session) -> Person:
    """Require super admin, raise 403 if not super admin"""
    person = require_auth(request, db)
    if not person.is_super_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super admin access required"
        )
    return person

