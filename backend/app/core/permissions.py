from functools import wraps
from fastapi import Request, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.middleware import get_current_person, get_current_company
from app.services.rbac import check_permission
from typing import Callable

def require_permission(resource_type: str, action: str):
    """Decorator to require a specific permission"""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract request and db from kwargs or args
            request = None
            db = None
            
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                elif isinstance(arg, Session):
                    db = arg
            
            if not request:
                for key, value in kwargs.items():
                    if isinstance(value, Request):
                        request = value
                    elif isinstance(value, Session) and not db:
                        db = value
            
            if not request or not db:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Request or database session not found"
                )
            
            person = get_current_person(request, db)
            company = get_current_company(request, db)
            
            if not person or not company:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            # Check permission
            has_permission = await check_permission(
                db=db,
                person_id=person.id,
                company_id=company.id,
                resource_type=resource_type,
                action=action
            )
            
            if not has_permission:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission required: {resource_type}:{action}"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

