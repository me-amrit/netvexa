from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
import json
import asyncio
from datetime import datetime
import logging

from config import settings
from rag_engine import RAGEngine
from models import ChatMessage, ChatResponse, AgentConfig
from database import init_db
from websocket_manager import ConnectionManager
from metrics import metrics_tracker, track_conversation_started, track_lead_captured
from auth_routes import router as auth_router
from agent_routes import router as agent_router
from billing_routes import router as billing_router
from billing_middleware import billing_middleware

# Configure logging
from logging_config import setup_logging
logger = setup_logging("netvexa-backend")

# Initialize FastAPI app
app = FastAPI(title="NETVEXA MVP", version="0.1.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add billing middleware
app.add_middleware(BaseHTTPMiddleware, dispatch=billing_middleware)

# Initialize connection manager
manager = ConnectionManager()

# Initialize RAG engine
rag_engine = RAGEngine()

# Include routers
app.include_router(auth_router)
app.include_router(agent_router)
app.include_router(billing_router)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.on_event("startup")
async def startup_event():
    """Initialize database and other resources on startup"""
    await init_db()
    logger.info("NETVEXA MVP started successfully")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "healthy", "service": "NETVEXA MVP", "version": "0.1.0"}

@app.post("/api/knowledge/ingest-url")
async def ingest_url(url: str):
    """Ingest content from a URL"""
    try:
        result = await rag_engine.ingest_url(url)
        return {"status": "processing", "job_id": result["job_id"]}
    except Exception as e:
        logger.error(f"Error ingesting URL: {e}")
        raise HTTPException(status_code=500, detail=str(e))

class IngestTextRequest(BaseModel):
    text: str
    metadata: Optional[Dict] = None

@app.post("/api/knowledge/ingest-text")
async def ingest_text(request: IngestTextRequest):
    """Ingest raw text content"""
    try:
        result = await rag_engine.ingest_text(request.text, request.metadata)
        return {"status": "success", "documents_created": result["documents_created"]}
    except Exception as e:
        logger.error(f"Error ingesting text: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws/{agent_id}")
async def websocket_endpoint(websocket: WebSocket, agent_id: str):
    """WebSocket endpoint for real-time chat"""
    await manager.connect(websocket, agent_id)
    
    # Track conversation start
    visitor_id = f"visitor_{datetime.utcnow().timestamp()}"
    await track_conversation_started(agent_id, visitor_id)
    
    # Get agent's user_id for billing
    from database import get_db, Agent
    from sqlalchemy import select
    user_id = None
    async for db in get_db():
        result = await db.execute(
            select(Agent).where(Agent.id == agent_id)
        )
        agent = result.scalar_one_or_none()
        if agent:
            user_id = agent.user_id
        break
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Create chat message
            chat_message = ChatMessage(
                content=message["content"],
                conversation_id=message.get("conversation_id", f"conv_{agent_id}_{datetime.now().timestamp()}"),
                sender="user",
                timestamp=datetime.now()
            )
            
            # Check message limits if we have user_id
            if user_id:
                from billing_service import BillingService
                async for db in get_db():
                    can_send = await BillingService.check_usage_limits(
                        user_id, "message", db
                    )
                    if not can_send:
                        await websocket.send_json({
                            "type": "error",
                            "content": "Message limit reached. Please upgrade your subscription.",
                            "timestamp": datetime.now().isoformat()
                        })
                        break
                    break
            
            # Process message through RAG engine
            response = await rag_engine.process_message(agent_id, chat_message)
            
            # Track message usage
            if user_id:
                async for db in get_db():
                    await BillingService.track_usage(
                        user_id, "message", 1, db
                    )
                    break
            
            # Send response back to client
            await websocket.send_json({
                "type": "message",
                "content": response.content,
                "timestamp": response.timestamp.isoformat(),
                "sender": "agent"
            })
            
    except WebSocketDisconnect:
        manager.disconnect(websocket, agent_id)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket, agent_id)

@app.post("/api/chat/message")
async def send_message(agent_id: str, message: ChatMessage):
    """REST endpoint for sending chat messages (fallback for non-WebSocket clients)"""
    try:
        response = await rag_engine.process_message(agent_id, message)
        return response
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/agents/{agent_id}/config")
async def get_agent_config(agent_id: str):
    """Get agent configuration"""
    # For MVP, return default config
    return AgentConfig(
        id=agent_id,
        name="NETVEXA Assistant",
        personality={
            "tone": "professional",
            "language": "en",
            "response_style": "concise"
        }
    )

@app.get("/api/metrics/dashboard")
async def get_dashboard_metrics():
    """Get comprehensive dashboard metrics"""
    try:
        metrics = await metrics_tracker.get_dashboard_metrics()
        return metrics
    except Exception as e:
        logger.error(f"Error fetching metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch metrics")

@app.get("/api/metrics/agents/{agent_id}/time-to-value")
async def get_agent_time_to_value(agent_id: str):
    """Get time to first value for a specific agent"""
    try:
        ttfv = await metrics_tracker.get_time_to_first_value(agent_id)
        if ttfv:
            return {
                "agent_id": agent_id,
                "time_to_first_value_seconds": ttfv.total_seconds(),
                "time_to_first_value_readable": str(ttfv)
            }
        return {"agent_id": agent_id, "time_to_first_value": None}
    except Exception as e:
        logger.error(f"Error calculating time to value: {e}")
        raise HTTPException(status_code=500, detail="Failed to calculate metric")

@app.get("/api/metrics/conversations/{conversation_id}/quality")
async def get_conversation_quality(conversation_id: str):
    """Get quality score for a specific conversation"""
    try:
        score = await metrics_tracker.calculate_conversation_quality_score(conversation_id)
        return {
            "conversation_id": conversation_id,
            "quality_score": score,
            "max_score": 100
        }
    except Exception as e:
        logger.error(f"Error calculating quality score: {e}")
        raise HTTPException(status_code=500, detail="Failed to calculate score")

@app.get("/api/metrics/weekly-active")
async def get_weekly_active_agents():
    """Get weekly active agents metrics"""
    try:
        metrics = await metrics_tracker.get_weekly_active_agents()
        return metrics
    except Exception as e:
        logger.error(f"Error fetching weekly active agents: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch metrics")

@app.get("/api/metrics/revenue")
async def get_revenue_metrics():
    """Get revenue and growth metrics"""
    try:
        metrics = await metrics_tracker.get_revenue_metrics()
        return metrics
    except Exception as e:
        logger.error(f"Error fetching revenue metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch metrics")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.HOST, port=settings.PORT, reload=True)