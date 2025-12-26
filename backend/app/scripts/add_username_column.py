import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import psycopg2
from app.core.config import settings

def add_username_column():
    """Add username column to people table if it doesn't exist"""
    try:
        conn = psycopg2.connect(
            host=settings.POSTGRES_HOST,
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD,
            database=settings.POSTGRES_DB
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Check if column exists
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='people' AND column_name='username'
        """)
        
        if cursor.fetchone():
            print("Username column already exists")
        else:
            # Add username column
            cursor.execute("""
                ALTER TABLE people 
                ADD COLUMN username VARCHAR UNIQUE
            """)
            print("Username column added successfully")
            
            # Create index
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS ix_people_username ON people(username)
            """)
            print("Username index created")
        
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error adding username column: {e}")
        raise

if __name__ == "__main__":
    add_username_column()

