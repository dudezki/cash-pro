from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.schemas.auth import PersonResponse, CompanyResponse

class UserResponse(PersonResponse):
    created_at: datetime
    
    class Config:
        from_attributes = True

class CompanyDetailResponse(CompanyResponse):
    created_at: datetime
    has_database: bool
    
    class Config:
        from_attributes = True

class ImpersonateRequest(BaseModel):
    user_id: int

class CreateUserRequest(BaseModel):
    email: str
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    phone: Optional[str] = None
    is_active: bool = True
    is_verified: bool = False
    is_super_admin: bool = False

