from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str

class LoginRequest(BaseModel):
    email_or_username: str  # Accept either email or username
    password: str

class PersonResponse(BaseModel):
    id: int
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    is_active: bool
    is_verified: bool
    is_super_admin: bool
    
    class Config:
        from_attributes = True

class CompanyResponse(BaseModel):
    id: int
    name: str
    slug: str
    database_name: Optional[str]
    
    class Config:
        from_attributes = True

class AuthResponse(BaseModel):
    person: PersonResponse
    companies: List[CompanyResponse]
    current_company_id: Optional[int]
    is_impersonating: bool = False

class SwitchCompanyRequest(BaseModel):
    company_id: int

