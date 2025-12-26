from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class PermissionResponse(BaseModel):
    id: int
    resource_type: str
    action: str
    description: Optional[str]
    
    class Config:
        from_attributes = True

class RoleResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    company_id: int
    permissions: List[PermissionResponse] = []
    
    class Config:
        from_attributes = True

class CreateRoleRequest(BaseModel):
    name: str
    description: Optional[str]
    permission_ids: List[int] = []

class AssignRoleRequest(BaseModel):
    user_id: int
    role_id: int

class ResourcePermissionRequest(BaseModel):
    user_id: int
    resource_type: str
    resource_id: int
    permission: str

