from passlib.context import CryptContext
from datetime import datetime, timedelta
import secrets
import hashlib

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password"""
    # Bcrypt has a 72 byte limit, truncate if necessary
    if len(password.encode('utf-8')) > 72:
        password = password[:72]
    return pwd_context.hash(password)

def generate_session_token() -> str:
    """Generate a secure random session token"""
    return secrets.token_urlsafe(32)

def hash_session_token(token: str) -> str:
    """Hash a session token for storage"""
    return hashlib.sha256(token.encode()).hexdigest()

def get_session_expiry() -> datetime:
    """Get session expiry time (7 days from now)"""
    return datetime.utcnow() + timedelta(days=7)

