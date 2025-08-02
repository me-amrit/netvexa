"""
Authentication module for NETVEXA platform.
Handles JWT tokens, user authentication, and API key management.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import secrets
import string
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database import async_session, User, ApiKey
from config import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme for JWT tokens
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

# HTTP Bearer for API keys
api_key_scheme = HTTPBearer(auto_error=False)

# JWT settings
SECRET_KEY = settings.JWT_SECRET_KEY or "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[str] = None
    email: Optional[str] = None


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    company_name: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: str
    email: str
    company_name: str
    is_active: bool
    created_at: datetime


class PasswordReset(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """Create a JWT refresh token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def generate_api_key() -> str:
    """Generate a secure API key."""
    alphabet = string.ascii_letters + string.digits
    return 'nv_' + ''.join(secrets.choice(alphabet) for _ in range(32))


def generate_reset_token() -> str:
    """Generate a secure password reset token."""
    return secrets.token_urlsafe(32)


async def get_user_by_email(email: str) -> Optional[User]:
    """Get user by email."""
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()


async def get_user_by_id(user_id: str) -> Optional[User]:
    """Get user by ID."""
    async with async_session() as session:
        return await session.get(User, user_id)


async def authenticate_user(email: str, password: str) -> Optional[User]:
    """Authenticate a user with email and password."""
    user = await get_user_by_email(email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """Get the current authenticated user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type")
        
        if user_id is None or token_type != "access":
            raise credentials_exception
            
        token_data = TokenData(user_id=user_id)
    except JWTError:
        raise credentials_exception
    
    user = await get_user_by_id(user_id=token_data.user_id)
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )
    
    return user


async def get_current_user_optional(
    token: str = Depends(oauth2_scheme)
) -> Optional[User]:
    """Get the current user if authenticated, otherwise return None."""
    try:
        return await get_current_user(token)
    except HTTPException:
        return None


async def verify_api_key(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(api_key_scheme)
) -> Optional[ApiKey]:
    """Verify an API key and return the associated ApiKey object."""
    if not credentials:
        return None
    
    async with async_session() as session:
        result = await session.execute(
            select(ApiKey).where(
                ApiKey.key == credentials.credentials,
                ApiKey.is_active == True
            )
        )
        api_key = result.scalar_one_or_none()
        
        if api_key:
            # Update last used timestamp
            api_key.last_used_at = datetime.utcnow()
            session.add(api_key)
            await session.commit()
            
        return api_key


async def get_current_user_or_api_key(
    token: Optional[str] = Depends(oauth2_scheme),
    api_key: Optional[ApiKey] = Depends(verify_api_key)
) -> Dict[str, Any]:
    """
    Get the current authenticated user or API key.
    This allows both JWT token and API key authentication.
    """
    if api_key:
        # API key authentication
        user = await get_user_by_id(api_key.user_id)
        return {
            "user": user,
            "auth_type": "api_key",
            "api_key": api_key
        }
    
    # Try JWT authentication
    try:
        user = await get_current_user(token)
        return {
            "user": user,
            "auth_type": "jwt",
            "api_key": None
        }
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Provide either a valid JWT token or API key.",
            headers={"WWW-Authenticate": "Bearer"},
        )