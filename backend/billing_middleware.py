"""
Middleware for tracking API usage for billing purposes
"""
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
import logging
import time
from typing import Callable

from database import get_db
from billing_service import BillingService
from auth import get_current_user_optional

logger = logging.getLogger(__name__)

# Endpoints that count as API calls for billing
BILLABLE_ENDPOINTS = {
    "/api/chat/message",
    "/api/agents/{agent_id}/chat",
    "/api/knowledge/search",
    "/api/agents/{agent_id}/test"
}

# Endpoints that should check usage limits
LIMIT_CHECK_ENDPOINTS = {
    "/api/agents": "agent",  # Creating agents
    "/api/chat/message": "message",
    "/api/agents/{agent_id}/chat": "message",
    "/ws/{agent_id}": "message"  # WebSocket connections
}


async def billing_middleware(request: Request, call_next: Callable):
    """Middleware to track API usage and enforce limits"""
    
    # Skip billing for auth endpoints and static files
    if request.url.path.startswith("/api/auth") or request.url.path.startswith("/static"):
        return await call_next(request)
    
    # Skip billing for webhook endpoint
    if request.url.path == "/api/billing/webhook":
        return await call_next(request)
    
    # Try to get current user
    try:
        # For WebSocket connections, we'll handle billing in the WebSocket handler
        if request.url.path.startswith("/ws/"):
            return await call_next(request)
        
        # Get user from request
        user = None
        if "authorization" in request.headers:
            from auth import oauth2_scheme
            token = await oauth2_scheme(request)
            if token:
                async for db in get_db():
                    user = await get_current_user_optional(token, db)
                    break
        
        # If no user, allow request (public endpoints)
        if not user:
            return await call_next(request)
        
        # Check usage limits for certain endpoints
        endpoint_pattern = get_endpoint_pattern(request.url.path)
        if endpoint_pattern in LIMIT_CHECK_ENDPOINTS:
            usage_type = LIMIT_CHECK_ENDPOINTS[endpoint_pattern]
            async for db in get_db():
                allowed = await BillingService.check_usage_limits(
                    user["id"], usage_type, db
                )
                if not allowed:
                    return JSONResponse(
                        status_code=429,
                        content={
                            "detail": f"Usage limit exceeded for {usage_type}. Please upgrade your subscription."
                        }
                    )
                break
        
        # Process request
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # Track usage for billable endpoints
        if endpoint_pattern in BILLABLE_ENDPOINTS and response.status_code < 400:
            async for db in get_db():
                await BillingService.track_usage(
                    user["id"], "api_call", 1, db
                )
                
                # For chat endpoints, also track messages
                if "chat" in endpoint_pattern or "message" in endpoint_pattern:
                    await BillingService.track_usage(
                        user["id"], "message", 1, db
                    )
                break
        
        # Add process time header
        response.headers["X-Process-Time"] = str(process_time)
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in billing middleware: {e}")
        # Don't block requests due to billing errors
        return await call_next(request)


def get_endpoint_pattern(path: str) -> str:
    """Convert actual path to endpoint pattern"""
    # Handle agent-specific endpoints
    if "/agents/" in path and "/chat" in path:
        return "/api/agents/{agent_id}/chat"
    elif "/agents/" in path and "/test" in path:
        return "/api/agents/{agent_id}/test"
    elif path.startswith("/api/agents") and path.count("/") == 2:
        return "/api/agents"
    elif path.startswith("/ws/"):
        return "/ws/{agent_id}"
    
    return path