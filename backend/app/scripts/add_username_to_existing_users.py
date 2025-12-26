import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine
from app.models.person import Person, Base

def add_usernames_to_existing_users():
    """Add username to existing users who don't have one"""
    # Ensure tables exist
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Get all users without username (using is_ for None check in SQLAlchemy)
        from sqlalchemy import or_
        users_without_username = db.query(Person).filter(
            or_(Person.username == None, Person.username == '')
        ).all()
        
        updated_count = 0
        for user in users_without_username:
            # Generate username from email (part before @)
            if '@' in user.email:
                username = user.email.split('@')[0]
            else:
                username = user.email
            
            # Ensure uniqueness
            base_username = username
            counter = 1
            while db.query(Person).filter(Person.username == username).first():
                username = f"{base_username}{counter}"
                counter += 1
            
            user.username = username
            updated_count += 1
            print(f"Added username '{username}' to user '{user.email}'")
        
        db.commit()
        print(f"Updated {updated_count} users with usernames")
    except Exception as e:
        print(f"Error adding usernames: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    add_usernames_to_existing_users()

