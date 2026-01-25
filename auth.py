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
    Verify password. Handles both bcrypt hashed passwords, SHA256 hashes, and plain text passwords.
    """
    if not plain_password or not stored_password:
        return False
        
    # Check if stored_password is a bcrypt hash (starts with $2)
    if stored_password.startswith('$2'):
        try:
            import bcrypt
            return bcrypt.checkpw(plain_password.encode('utf-8'), stored_password.encode('utf-8'))
        except:
            pass
    
    # Check if it's a SHA256 hash (64 hex characters)
    elif len(stored_password) == 64 and all(c in '0123456789abcdefABCDEF' for c in stored_password):
        import hashlib
        return hashlib.sha256(plain_password.encode()).hexdigest() == stored_password
    
    # Plain text password comparison (for backward compatibility)
    return plain_password == stored_password

def get_password_hash(password):
    # Ensure password is a string and truncate to 72 characters max for bcrypt compatibility
    if not isinstance(password, str):
        password = str(password)
    if len(password) > 72:
        password = password[:72]
    try:
        # Try using bcrypt directly
        import bcrypt
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    except Exception as e:
        print(f"Error with bcrypt: {e}")
        try:
            # Fallback to passlib
            return pwd_context.hash(password)
        except Exception as e2:
            print(f"Error with passlib: {e2}")
            # Final fallback - simple hash
            import hashlib
            return hashlib.sha256(password.encode()).hexdigest()

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
