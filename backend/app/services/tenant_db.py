from sqlalchemy.orm import Session
from app.core.database import create_database, get_tenant_db_connection_string
from app.core.tenant_db import get_tenant_database_name, ensure_tenant_database
from app.models.company import Company
from app.models.tenant.role import Role, Base as TenantBase
from app.models.tenant.permission import Permission
from app.models.tenant.role_permission import RolePermission
from app.models.tenant.chart_of_accounts import ChartOfAccount, AccountType
from app.models.tenant.account import Account
from app.models.tenant.journal_entry import JournalEntry
from app.models.tenant.journal_entry_line import JournalEntryLine
from app.models.tenant.transaction import Transaction
from app.models.tenant.category import Category
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
    
    # Create all tenant tables (including financial models)
    TenantBase.metadata.create_all(bind=tenant_engine)
    
    # Initialize default roles and permissions
    initialize_tenant_rbac(tenant_engine, company_id)
    
    # Initialize default chart of accounts
    initialize_chart_of_accounts(tenant_engine, company_id)
    
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


def initialize_chart_of_accounts(engine, company_id: int):
    """Initialize default chart of accounts structure for a tenant"""
    TenantSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    tenant_db = TenantSessionLocal()
    
    try:
        # Check if chart of accounts already exists
        existing = tenant_db.query(ChartOfAccount).filter(
            ChartOfAccount.company_id == company_id
        ).first()
        
        if existing:
            # Chart of accounts already initialized
            return
        
        # Default chart of accounts structure
        default_accounts = [
            # Assets (1000-1999)
            {"code": "1000", "name": "Cash", "type": AccountType.ASSET, "parent_id": None},
            {"code": "1100", "name": "Bank Accounts", "type": AccountType.ASSET, "parent_id": None},
            {"code": "1200", "name": "Accounts Receivable", "type": AccountType.ASSET, "parent_id": None},
            {"code": "1300", "name": "Inventory", "type": AccountType.ASSET, "parent_id": None},
            {"code": "1400", "name": "Prepaid Expenses", "type": AccountType.ASSET, "parent_id": None},
            {"code": "1500", "name": "Fixed Assets", "type": AccountType.ASSET, "parent_id": None},
            
            # Liabilities (2000-2999)
            {"code": "2000", "name": "Accounts Payable", "type": AccountType.LIABILITY, "parent_id": None},
            {"code": "2100", "name": "Short-term Debt", "type": AccountType.LIABILITY, "parent_id": None},
            {"code": "2200", "name": "Long-term Debt", "type": AccountType.LIABILITY, "parent_id": None},
            {"code": "2300", "name": "Accrued Expenses", "type": AccountType.LIABILITY, "parent_id": None},
            
            # Equity (3000-3999)
            {"code": "3000", "name": "Capital", "type": AccountType.EQUITY, "parent_id": None},
            {"code": "3100", "name": "Retained Earnings", "type": AccountType.EQUITY, "parent_id": None},
            {"code": "3200", "name": "Current Year Earnings", "type": AccountType.EQUITY, "parent_id": None},
            
            # Revenue (4000-4999)
            {"code": "4000", "name": "Sales Revenue", "type": AccountType.REVENUE, "parent_id": None},
            {"code": "4100", "name": "Service Revenue", "type": AccountType.REVENUE, "parent_id": None},
            {"code": "4200", "name": "Other Income", "type": AccountType.REVENUE, "parent_id": None},
            
            # Expenses (5000-5999)
            {"code": "5000", "name": "Cost of Goods Sold", "type": AccountType.EXPENSE, "parent_id": None},
            {"code": "5100", "name": "Operating Expenses", "type": AccountType.EXPENSE, "parent_id": None},
            {"code": "5200", "name": "Salaries and Wages", "type": AccountType.EXPENSE, "parent_id": None},
            {"code": "5300", "name": "Rent Expense", "type": AccountType.EXPENSE, "parent_id": None},
            {"code": "5400", "name": "Utilities", "type": AccountType.EXPENSE, "parent_id": None},
            {"code": "5500", "name": "Marketing and Advertising", "type": AccountType.EXPENSE, "parent_id": None},
            {"code": "5600", "name": "Depreciation", "type": AccountType.EXPENSE, "parent_id": None},
            {"code": "5700", "name": "Interest Expense", "type": AccountType.EXPENSE, "parent_id": None},
            {"code": "5800", "name": "Tax Expense", "type": AccountType.EXPENSE, "parent_id": None},
        ]
        
        # Create accounts
        account_map = {}  # Map codes to IDs for parent relationships
        for acc_data in default_accounts:
            account = ChartOfAccount(
                account_code=acc_data["code"],
                account_name=acc_data["name"],
                account_type=acc_data["type"],
                parent_account_id=None,  # Will set parent_id later if needed
                is_active=True,
                company_id=company_id
            )
            tenant_db.add(account)
            tenant_db.flush()
            account_map[acc_data["code"]] = account.id
        
        tenant_db.commit()
        print(f"Initialized default chart of accounts for company {company_id}")
    except Exception as e:
        print(f"Error initializing chart of accounts: {e}")
        tenant_db.rollback()
    finally:
        tenant_db.close()

