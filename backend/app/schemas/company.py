from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CreateCompanyRequest(BaseModel):
    name: str
    legal_name: Optional[str] = None
    tax_id: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None

