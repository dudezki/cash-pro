from sqlalchemy.orm import Session
from app.core.database import create_database, get_tenant_db_connection_string
from app.core.tenant_db import get_tenant_database_name, ensure_tenant_database
from app.models.company import Company
from app.models.tenant.role import Role, Base as TenantBase
from app.models.tenant.permission import Permission
from app.models.tenant.role_permission import RolePermission
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from typing import Optional

def create_tenant_database(company_id: int, company_slug: str, db: Session) -> Optional[str]:
    """Create tenant database and initialize schema"""
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        return None
    
    # Ensure database exists
    database_name = ensure_tenant_database(db, company)
    if not database_name:
        return None
    
    # Create tenant database connection
    connection_string = get_tenant_db_connection_string(company_id, database_name)
    tenant_engine = create_engine(connection_string, echo=False)
    
    # Create all tenant tables
    TenantBase.metadata.create_all(bind=tenant_engine)
    
    # Initialize default roles and permissions
    initialize_tenant_rbac(tenant_engine, company_id)
    
    return database_name

def initialize_tenant_rbac(engine, company_id: int):
    """Initialize default RBAC roles and permissions for a tenant"""
    TenantSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    tenant_db = TenantSessionLocal()
    
    try:
        # Create default permissions
        default_permissions = [
            {"resource_type": "invoice", "action": "read", "description": "Read invoices"},
            {"resource_type": "invoice", "action": "write", "description": "Create/edit invoices"},
            {"resource_type": "invoice", "action": "delete", "description": "Delete invoices"},
            {"resource_type": "customer", "action": "read", "description": "Read customers"},
            {"resource_type": "customer", "action": "write", "description": "Create/edit customers"},
            {"resource_type": "customer", "action": "delete", "description": "Delete customers"},
        ]
        
        for perm_data in default_permissions:
            existing = tenant_db.query(Permission).filter(
                Permission.resource_type == perm_data["resource_type"],
                Permission.action == perm_data["action"]
            ).first()
            if not existing:
                permission = Permission(**perm_data)
                tenant_db.add(permission)
        
        tenant_db.commit()
        
        # Create default roles
        default_roles = [
            {
                "name": "Owner",
                "description": "Full access to all resources",
                "permissions": ["invoice:read", "invoice:write", "invoice:delete", "customer:read", "customer:write", "customer:delete"]
            },
            {
                "name": "Admin",
                "description": "Administrative access",
                "permissions": ["invoice:read", "invoice:write", "customer:read", "customer:write"]
            },
            {
                "name": "Member",
                "description": "Standard user access",
                "permissions": ["invoice:read", "customer:read"]
            },
            {
                "name": "Viewer",
                "description": "Read-only access",
                "permissions": ["invoice:read", "customer:read"]
            }
        ]
        
        for role_data in default_roles:
            existing_role = tenant_db.query(Role).filter(
                Role.name == role_data["name"],
                Role.company_id == company_id
            ).first()
            
            if not existing_role:
                role = Role(
                    name=role_data["name"],
                    description=role_data["description"],
                    company_id=company_id
                )
                tenant_db.add(role)
                tenant_db.flush()
                
                # Assign permissions to role
                for perm_str in role_data["permissions"]:
                    resource_type, action = perm_str.split(":")
                    permission = tenant_db.query(Permission).filter(
                        Permission.resource_type == resource_type,
                        Permission.action == action
                    ).first()
                    
                    if permission:
                        role_perm = RolePermission(
                            role_id=role.id,
                            permission_id=permission.id
                        )
                        tenant_db.add(role_perm)
        
        tenant_db.commit()
    finally:
        tenant_db.close()

