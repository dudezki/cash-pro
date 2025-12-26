from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.core.database import get_db, get_tenant_db
from app.core.middleware import require_auth, get_current_person, get_current_company
from app.models.company import Company
from app.models.tenant.role import Role
from app.models.tenant.permission import Permission
from app.models.tenant.role_permission import RolePermission
from app.models.tenant.user_role import UserRole
from app.models.tenant.resource_permission import ResourcePermission
from app.schemas.rbac import (
    RoleResponse, PermissionResponse, CreateRoleRequest,
    AssignRoleRequest, ResourcePermissionRequest
)
from typing import List

router = APIRouter()

@router.get("/roles", response_model=List[RoleResponse])
async def get_roles(
    request: Request,
    db: Session = Depends(get_db)
):
    """Get all roles for current company"""
    person = require_auth(request, db)
    company = get_current_company(request, db)
    
    if not company or not company.database_name:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company database not found"
        )
    
    try:
        tenant_db_gen = get_tenant_db(company.id, company.database_name)
        tenant_db = next(tenant_db_gen)
        
        try:
            roles = tenant_db.query(Role).filter(
                Role.company_id == company.id
            ).all()
            
            result = []
            for role in roles:
                role_perms = tenant_db.query(RolePermission).filter(
                    RolePermission.role_id == role.id
                ).all()
                
                permissions = []
                for rp in role_perms:
                    perm = tenant_db.query(Permission).filter(
                        Permission.id == rp.permission_id
                    ).first()
                    if perm:
                        permissions.append(PermissionResponse.model_validate(perm))
                
                result.append(RoleResponse(
                    id=role.id,
                    name=role.name,
                    description=role.description,
                    company_id=role.company_id,
                    permissions=permissions
                ))
            
            return result
        finally:
            tenant_db.close()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching roles: {str(e)}"
        )

@router.post("/roles", response_model=RoleResponse)
async def create_role(
    request_data: CreateRoleRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """Create a new role (admin/owner only)"""
    person = require_auth(request, db)
    company = get_current_company(request, db)
    
    if not company or not company.database_name:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company database not found"
        )
    
    # Check if user is admin or owner
    from app.models.person_company import PersonCompany
    person_company = db.query(PersonCompany).filter(
        PersonCompany.person_id == person.id,
        PersonCompany.company_id == company.id
    ).first()
    
    if not person_company or person_company.role not in ["owner", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin or owner access required"
        )
    
    try:
        tenant_db_gen = get_tenant_db(company.id, company.database_name)
        tenant_db = next(tenant_db_gen)
        
        try:
            # Check if role already exists
            existing = tenant_db.query(Role).filter(
                Role.name == request_data.name,
                Role.company_id == company.id
            ).first()
            
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Role already exists"
                )
            
            # Create role
            role = Role(
                name=request_data.name,
                description=request_data.description,
                company_id=company.id
            )
            tenant_db.add(role)
            tenant_db.flush()
            
            # Assign permissions
            for perm_id in request_data.permission_ids:
                permission = tenant_db.query(Permission).filter(
                    Permission.id == perm_id
                ).first()
                
                if permission:
                    role_perm = RolePermission(
                        role_id=role.id,
                        permission_id=permission.id
                    )
                    tenant_db.add(role_perm)
            
            tenant_db.commit()
            tenant_db.refresh(role)
            
            # Get permissions for response
            role_perms = tenant_db.query(RolePermission).filter(
                RolePermission.role_id == role.id
            ).all()
            
            permissions = []
            for rp in role_perms:
                perm = tenant_db.query(Permission).filter(
                    Permission.id == rp.permission_id
                ).first()
                if perm:
                    permissions.append(PermissionResponse.model_validate(perm))
            
            return RoleResponse(
                id=role.id,
                name=role.name,
                description=role.description,
                company_id=role.company_id,
                permissions=permissions
            )
        finally:
            tenant_db.close()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating role: {str(e)}"
        )

@router.get("/permissions", response_model=List[PermissionResponse])
async def get_permissions(
    request: Request,
    db: Session = Depends(get_db)
):
    """Get all available permissions"""
    require_auth(request, db)
    company = get_current_company(request, db)
    
    if not company or not company.database_name:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company database not found"
        )
    
    try:
        tenant_db_gen = get_tenant_db(company.id, company.database_name)
        tenant_db = next(tenant_db_gen)
        
        try:
            permissions = tenant_db.query(Permission).all()
            return [PermissionResponse.model_validate(p) for p in permissions]
        finally:
            tenant_db.close()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching permissions: {str(e)}"
        )

@router.post("/assign-role")
async def assign_role(
    request_data: AssignRoleRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """Assign a role to a user (admin/owner only)"""
    person = require_auth(request, db)
    company = get_current_company(request, db)
    
    if not company or not company.database_name:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company database not found"
        )
    
    # Check permissions
    from app.models.person_company import PersonCompany
    person_company = db.query(PersonCompany).filter(
        PersonCompany.person_id == person.id,
        PersonCompany.company_id == company.id
    ).first()
    
    if not person_company or person_company.role not in ["owner", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin or owner access required"
        )
    
    try:
        tenant_db_gen = get_tenant_db(company.id, company.database_name)
        tenant_db = next(tenant_db_gen)
        
        try:
            # Check if assignment already exists
            existing = tenant_db.query(UserRole).filter(
                UserRole.user_id == request_data.user_id,
                UserRole.role_id == request_data.role_id,
                UserRole.company_id == company.id
            ).first()
            
            if existing:
                return {"message": "Role already assigned"}
            
            user_role = UserRole(
                user_id=request_data.user_id,
                role_id=request_data.role_id,
                company_id=company.id
            )
            tenant_db.add(user_role)
            tenant_db.commit()
            
            return {"message": "Role assigned successfully"}
        finally:
            tenant_db.close()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error assigning role: {str(e)}"
        )

