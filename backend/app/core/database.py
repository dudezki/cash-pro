from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool
from app.core.config import settings
from typing import Generator, Optional
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Control database engine
# Construct DATABASE_URL if not provided or if it doesn't start with postgresql
if not hasattr(settings, 'DATABASE_URL') or not settings.DATABASE_URL or not settings.DATABASE_URL.startswith('postgresql'):
    database_url = f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:5432/{settings.POSTGRES_DB}"
else:
    database_url = settings.DATABASE_URL

engine = create_engine(
    database_url,
    poolclass=NullPool,
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Generator[Session, None, None]:
    """Get control database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_tenant_db_connection_string(company_id: int, database_name: str) -> str:
    """Generate connection string for tenant database"""
    return f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:5432/{database_name}"

def get_tenant_db(company_id: int, database_name: str) -> Generator[Session, None, None]:
    """Get tenant database session"""
    connection_string = get_tenant_db_connection_string(company_id, database_name)
    tenant_engine = create_engine(connection_string, poolclass=NullPool, echo=False)
    TenantSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=tenant_engine)
    db = TenantSessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_database(database_name: str) -> bool:
    """Create a new PostgreSQL database"""
    try:
        # Connect to postgres database to create new database
        conn = psycopg2.connect(
            host=settings.POSTGRES_HOST,
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD,
            database="postgres"
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{database_name}'")
        exists = cursor.fetchone()
        
        if not exists:
            cursor.execute(f'CREATE DATABASE "{database_name}"')
            cursor.close()
            conn.close()
            return True
        else:
            cursor.close()
            conn.close()
            return False
    except Exception as e:
        print(f"Error creating database: {e}")
        return False

