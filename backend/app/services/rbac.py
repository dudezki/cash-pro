from sqlalchemy.orm import Session
from app.models.person_company import PersonCompany
from app.models.tenant.role import Role
from app.models.tenant.permission import Permission
from app.models.tenant.role_permission import RolePermission
from app.models.tenant.user_role import UserRole
from app.models.tenant.resource_permission import ResourcePermission
from app.core.database import get_tenant_db
from app.models.company import Company
from typing import Optional

async def check_permission(
    db: Session,
    person_id: int,
    company_id: int,
    resource_type: str,
    action: str
) -> bool:
    """Check if person has permission for resource_type:action"""
    # Get company to find tenant database
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company or not company.database_name:
        return False
    
    # Get company-level role from PersonCompany
    person_company = db.query(PersonCompany).filter(
        PersonCompany.person_id == person_id,
        PersonCompany.company_id == company_id
    ).first()
    
    if not person_company:
        return False
    
    # Owner and Admin have full access
    if person_company.role in ["owner", "admin"]:
        return True
    
    # Check tenant database for RBAC permissions
    try:
        tenant_db_gen = get_tenant_db(company_id, company.database_name)
        tenant_db = next(tenant_db_gen)
        
        try:
            # Check role-based permissions
            user_roles = tenant_db.query(UserRole).filter(
                UserRole.user_id == person_id,
                UserRole.company_id == company_id
            ).all()
            
            for user_role in user_roles:
                role_perms = tenant_db.query(RolePermission).filter(
                    RolePermission.role_id == user_role.role_id
                ).all()
                
                for role_perm in role_perms:
                    permission = tenant_db.query(Permission).filter(
                        Permission.id == role_perm.permission_id,
                        Permission.resource_type == resource_type,
                        Permission.action == action
                    ).first()
                    
                    if permission:
                        return True
            
            # Check direct resource permissions
            resource_perm = tenant_db.query(ResourcePermission).filter(
                ResourcePermission.user_id == person_id,
                ResourcePermission.resource_type == resource_type,
                ResourcePermission.permission == action
            ).first()
            
            if resource_perm:
                return True
            
            # Check company-level role permissions (fallback)
            # Member can read, Viewer can only read
            if person_company.role == "member" and action == "read":
                return True
            if person_company.role == "viewer" and action == "read":
                return True
            
            return False
        finally:
            tenant_db.close()
    except Exception as e:
        print(f"Error checking permission: {e}")
        return False

def get_user_permissions(db: Session, person_id: int, company_id: int) -> list:
    """Get all permissions for a user in a company"""
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company or not company.database_name:
        return []
    
    permissions = []
    
    try:
        tenant_db_gen = get_tenant_db(company_id, company.database_name)
        tenant_db = next(tenant_db_gen)
        
        try:
            # Get role-based permissions
            user_roles = tenant_db.query(UserRole).filter(
                UserRole.user_id == person_id,
                UserRole.company_id == company_id
            ).all()
            
            for user_role in user_roles:
                role_perms = tenant_db.query(RolePermission).filter(
                    RolePermission.role_id == user_role.role_id
                ).all()
                
                for role_perm in role_perms:
                    permission = tenant_db.query(Permission).filter(
                        Permission.id == role_perm.permission_id
                    ).first()
                    
                    if permission:
                        perm_str = f"{permission.resource_type}:{permission.action}"
                        if perm_str not in permissions:
                            permissions.append(perm_str)
            
            # Get direct resource permissions
            resource_perms = tenant_db.query(ResourcePermission).filter(
                ResourcePermission.user_id == person_id
            ).all()
            
            for resource_perm in resource_perms:
                perm_str = f"{resource_perm.resource_type}:{resource_perm.permission}"
                if perm_str not in permissions:
                    permissions.append(perm_str)
        finally:
            tenant_db.close()
    except Exception as e:
        print(f"Error getting permissions: {e}")
    
    return permissions

