from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

def verify_password(plain_password, stored_password):
    """
    Verify password. Handles both bcrypt hashed passwords and plain text passwords.
    If stored_password looks like a bcrypt hash, use bcrypt verification.
    Otherwise, do a plain text comparison (for backward compatibility).
    """
    # Check if stored_password is a bcrypt hash (starts with $2a$, $2b$, or $2y$)
    if stored_password and stored_password.startswith('$2'):
        try:
            return pwd_context.verify(plain_password, stored_password)
        except Exception:
            # If verification fails, fall back to plain text comparison
            return plain_password == stored_password
    else:
        # Plain text password comparison
        return plain_password == stored_password

def get_password_hash(password):
    # Truncate password to 72 characters max for bcrypt compatibility
    if len(password) > 72:
        password = password[:72]
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return payload  # Return full payload to access user_type
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

# Simple admin credentials (for demo purposes)
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin"

def authenticate_admin(username: str, password: str):
    """Authenticate admin with plain text comparison"""
    # Strip whitespace and convert to lowercase for username comparison
    username_clean = username.strip().lower() if username else ""
    password_clean = password.strip() if password else ""
    
    if username_clean == ADMIN_USERNAME.lower() and password_clean == ADMIN_PASSWORD:
        return True
    return False

def verify_token_and_get_payload(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_type: str = payload.get("user_type")
        if username is None or user_type is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return {"username": username, "user_type": user_type}
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_current_admin(payload: dict = Depends(verify_token_and_get_payload)):
    """Verify that the current user is an admin"""
    username = payload.get("sub")
    user_type = payload.get("user_type", "").lower()
    
    # Check if user_type is admin OR if username is admin (for backward compatibility)
    if user_type != "admin" and username != ADMIN_USERNAME:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return username
