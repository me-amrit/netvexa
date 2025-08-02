"""
Authentication API routes for NETVEXA platform.
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta
import logging

from database import async_session, User, ApiKey, get_session
from auth import (
    Token, UserCreate, UserLogin, UserResponse, PasswordReset, PasswordResetConfirm,
    get_password_hash, authenticate_user, create_access_token, create_refresh_token,
    get_current_user, generate_api_key, generate_reset_token, get_user_by_email
)
from metrics import metrics_tracker

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate):
    """Register a new user."""
    async with async_session() as session:
        # Check if user already exists
        existing_user = await session.execute(
            select(User).where(User.email == user_data.email)
        )
        if existing_user.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create new user
        user = User(
            email=user_data.email,
            hashed_password=get_password_hash(user_data.password),
            company_name=user_data.company_name
        )
        
        session.add(user)
        await session.commit()
        await session.refresh(user)
        
        # Track registration event
        await metrics_tracker.track_event("user_registered", {
            "user_id": user.id,
            "company_name": user.company_name
        })
        
        return UserResponse(
            id=user.id,
            email=user.email,
            company_name=user.company_name,
            is_active=user.is_active,
            created_at=user.created_at
        )


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login with email and password."""
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create tokens
    access_token = create_access_token(data={"sub": user.id})
    refresh_token = create_refresh_token(data={"sub": user.id})
    
    # Track login event
    await metrics_tracker.track_event("user_login", {
        "user_id": user.id
    })
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(refresh_token: str):
    """Refresh access token using refresh token."""
    from jose import JWTError, jwt
    from auth import SECRET_KEY, ALGORITHM
    
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type")
        
        if user_id is None or token_type != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Get user
        from auth import get_user_by_id
        user = await get_user_by_id(user_id)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        # Create new tokens
        access_token = create_access_token(data={"sub": user.id})
        new_refresh_token = create_refresh_token(data={"sub": user.id})
        
        return Token(
            access_token=access_token,
            refresh_token=new_refresh_token
        )
        
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information."""
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        company_name=current_user.company_name,
        is_active=current_user.is_active,
        created_at=current_user.created_at
    )


@router.post("/password-reset", status_code=status.HTTP_202_ACCEPTED)
async def request_password_reset(
    reset_data: PasswordReset,
    background_tasks: BackgroundTasks
):
    """Request password reset email."""
    user = await get_user_by_email(reset_data.email)
    
    # Always return success to prevent email enumeration
    if user:
        reset_token = generate_reset_token()
        # In production, store this token in Redis with expiration
        # and send email with reset link
        logger.info(f"Password reset token for {user.email}: {reset_token}")
        
        # Track password reset request
        await metrics_tracker.track_event("password_reset_requested", {
            "user_id": user.id
        })
        
        # In production, send email here
        # background_tasks.add_task(send_reset_email, user.email, reset_token)
    
    return {"message": "If the email exists, a password reset link has been sent"}


@router.post("/password-reset-confirm")
async def confirm_password_reset(reset_data: PasswordResetConfirm):
    """Confirm password reset with token."""
    # In production, validate token from Redis
    # For now, just return an error
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Password reset functionality not yet implemented"
    )


# API Key Management
@router.post("/api-keys", response_model=dict)
async def create_api_key(
    name: str,
    current_user: User = Depends(get_current_user)
):
    """Create a new API key for the current user."""
    async with async_session() as session:
        # Check if user already has too many API keys
        existing_keys = await session.execute(
            select(ApiKey).where(
                ApiKey.user_id == current_user.id,
                ApiKey.is_active == True
            )
        )
        key_count = len(existing_keys.scalars().all())
        
        if key_count >= 5:  # Limit to 5 active keys per user
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum number of API keys reached"
            )
        
        # Generate new API key
        api_key = ApiKey(
            user_id=current_user.id,
            name=name,
            key=generate_api_key()
        )
        
        session.add(api_key)
        await session.commit()
        await session.refresh(api_key)
        
        # Track API key creation
        await metrics_tracker.track_event("api_key_created", {
            "user_id": current_user.id,
            "api_key_id": api_key.id
        })
        
        return {
            "id": api_key.id,
            "name": api_key.name,
            "key": api_key.key,  # Only shown once
            "created_at": api_key.created_at
        }


@router.get("/api-keys", response_model=list)
async def list_api_keys(current_user: User = Depends(get_current_user)):
    """List all API keys for the current user."""
    async with async_session() as session:
        result = await session.execute(
            select(ApiKey).where(
                ApiKey.user_id == current_user.id,
                ApiKey.is_active == True
            ).order_by(ApiKey.created_at.desc())
        )
        keys = result.scalars().all()
        
        return [
            {
                "id": key.id,
                "name": key.name,
                "created_at": key.created_at,
                "last_used_at": key.last_used_at,
                "key_preview": key.key[:8] + "..." + key.key[-4:]  # Show partial key
            }
            for key in keys
        ]


@router.delete("/api-keys/{key_id}")
async def delete_api_key(
    key_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete (deactivate) an API key."""
    async with async_session() as session:
        result = await session.execute(
            select(ApiKey).where(
                ApiKey.id == key_id,
                ApiKey.user_id == current_user.id
            )
        )
        api_key = result.scalar_one_or_none()
        
        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="API key not found"
            )
        
        # Soft delete
        api_key.is_active = False
        await session.commit()
        
        # Track API key deletion
        await metrics_tracker.track_event("api_key_deleted", {
            "user_id": current_user.id,
            "api_key_id": api_key.id
        })
        
        return {"message": "API key deleted successfully"}