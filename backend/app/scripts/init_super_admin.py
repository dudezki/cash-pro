import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine
from app.models.person import Person, Base
from app.core.security import get_password_hash
from app.core.config import settings

def init_super_admin():
    """Initialize super admin account"""
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        username = settings.SUPER_ADMIN_USERNAME
        password = settings.SUPER_ADMIN_PASSWORD
        
        # Strip whitespace and newlines
        if username:
            username = username.strip().strip('\n\r')
        if password:
            password = password.strip().strip('\n\r')
        
        # Check password length in bytes
        password_bytes = len(password.encode('utf-8')) if password else 0
        print(f"DEBUG: Username length: {len(username) if username else 0}, Password bytes: {password_bytes}")
        
        if not username or not password or username == "admin@example.com" or password == "change_me":
            print("WARNING: SUPER_ADMIN_USERNAME or SUPER_ADMIN_PASSWORD not properly configured")
            print(f"Current values: USERNAME={username or 'NOT SET'}, PASSWORD={'*' * min(len(password), 20) if password else 'NOT SET'}")
            print("Please set SUPER_ADMIN_USERNAME and SUPER_ADMIN_PASSWORD in .env file")
            # Still try to create with defaults if they exist
            if not username or username == "admin@example.com":
                return
        
        # Ensure password is within bcrypt limit (72 bytes)
        if password_bytes > 72:
            print(f"WARNING: Password is {password_bytes} bytes, truncating to 72 bytes")
            # Truncate to 72 bytes
            password_encoded = password.encode('utf-8')[:72]
            password = password_encoded.decode('utf-8', errors='ignore')
        
        # Check if super admin already exists
        super_admin = db.query(Person).filter(
            Person.email == username,
            Person.is_super_admin == True
        ).first()
        
        # Hash password before using
        try:
            hashed_password = get_password_hash(password)
        except Exception as hash_error:
            print(f"Error hashing password: {hash_error}")
            print(f"Password length: {len(password)}, Password bytes: {len(password.encode('utf-8'))}")
            raise
        
        if super_admin:
            # Update password if needed
            super_admin.hashed_password = hashed_password
            # Ensure username is set
            if not super_admin.username:
                admin_username = username.split('@')[0] if '@' in username else username
                super_admin.username = admin_username
            db.commit()
            print(f"Super admin '{username}' already exists, password updated")
        else:
            # Check if user exists but is not super admin
            existing_user = db.query(Person).filter(Person.email == username).first()
            
            if existing_user:
                # Upgrade to super admin
                existing_user.is_super_admin = True
                existing_user.hashed_password = hashed_password
                # Ensure username is set
                if not existing_user.username:
                    admin_username = username.split('@')[0] if '@' in username else username
                    existing_user.username = admin_username
                db.commit()
                print(f"User '{username}' upgraded to super admin")
            else:
                # Create new super admin
                # Extract username from email if it's an email, otherwise use as-is
                admin_username = username.split('@')[0] if '@' in username else username
                super_admin = Person(
                    email=username if '@' in username else f"{username}@cashpro.local",
                    username=admin_username,
                    hashed_password=hashed_password,
                    first_name="Super",
                    last_name="Admin",
                    is_active=True,
                    is_verified=True,
                    is_super_admin=True
                )
                db.add(super_admin)
                db.commit()
                print(f"Super admin '{username}' created successfully")
    except Exception as e:
        print(f"Error initializing super admin: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_super_admin()

