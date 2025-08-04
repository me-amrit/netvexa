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
from rag import ProductionRAGEngine
from models import ChatMessage, ChatResponse, AgentConfig
from database import init_db, get_db, Agent, Conversation as DBConversation, Message as DBMessage
from websocket_manager import ConnectionManager
from metrics import metrics_tracker, track_conversation_started, track_lead_captured
from auth_routes import router as auth_router
from agent_routes import router as agent_router
from billing_routes import router as billing_router
from knowledge_routes import router as knowledge_router
from conversation_routes import router as conversation_router
from lead_routes import router as lead_router
from billing_middleware import billing_middleware
from quick_reply_engine import QuickReplyEngine, ConversationStage

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
rag_engine = ProductionRAGEngine()

# Initialize Quick Reply engine
quick_reply_engine = QuickReplyEngine()

# Include routers
app.include_router(auth_router)
app.include_router(agent_router)
app.include_router(billing_router)
app.include_router(knowledge_router)
app.include_router(conversation_router)
app.include_router(lead_router)

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


@app.get("/api/quick-replies/{agent_id}")
async def get_quick_replies(
    agent_id: str,
    conversation_id: Optional[str] = None,
    stage: Optional[str] = None
):
    """Get intelligent quick replies for conversation"""
    try:
        # Get conversation history if conversation_id provided
        conversation_history = []
        if conversation_id:
            async for db in get_db():
                from sqlalchemy import select, and_
                result = await db.execute(
                    select(DBMessage)
                    .where(DBMessage.conversation_id == conversation_id)
                    .order_by(DBMessage.timestamp)
                    .limit(10)  # Last 10 messages
                )
                messages = result.scalars().all()
                conversation_history = [
                    {
                        "sender": msg.sender,
                        "content": msg.content,
                        "timestamp": msg.timestamp.isoformat()
                    }
                    for msg in messages
                ]
                break
        
        # User context (basic for now)
        user_context = {
            "is_new_user": len(conversation_history) == 0,
            "source": "website",
            "previous_conversations": 0
        }
        
        # Convert stage string to enum if provided
        conversation_stage = None
        if stage:
            try:
                conversation_stage = ConversationStage(stage)
            except ValueError:
                pass
        
        # Generate quick replies
        quick_replies = quick_reply_engine.generate_quick_replies(
            conversation_history=conversation_history,
            user_context=user_context,
            stage=conversation_stage
        )
        
        return {
            "quick_replies": quick_replies,
            "stage": conversation_stage.value if conversation_stage else "unknown",
            "context": user_context
        }
        
    except Exception as e:
        logger.error(f"Error generating quick replies: {e}")
        # Fallback to basic replies
        return {
            "quick_replies": [
                {"text": "Tell me more", "payload": "tell_more"},
                {"text": "Get pricing", "payload": "pricing_info"},
                {"text": "Contact sales", "payload": "contact_sales"}
            ],
            "stage": "fallback",
            "context": {}
        }

@app.websocket("/ws/{agent_id}")
async def websocket_endpoint(websocket: WebSocket, agent_id: str):
    """WebSocket endpoint for real-time chat"""
    await manager.connect(websocket, agent_id)
    
    # Create conversation in database
    visitor_id = f"visitor_{datetime.utcnow().timestamp()}"
    conversation_id = None
    
    async for db in get_db():
        conversation = DBConversation(
            agent_id=agent_id,
            visitor_id=visitor_id,
            started_at=datetime.utcnow(),
            meta_data={"source": "websocket"}
        )
        db.add(conversation)
        await db.commit()
        await db.refresh(conversation)
        conversation_id = conversation.id
        break
    
    await track_conversation_started(agent_id, visitor_id)
    
    # Get agent's user_id for billing
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
                conversation_id=conversation_id or message.get("conversation_id", f"conv_{agent_id}_{datetime.now().timestamp()}"),
                sender="user",
                timestamp=datetime.now()
            )
            
            # Store message in database
            async for db in get_db():
                db_message = DBMessage(
                    conversation_id=conversation_id,
                    sender="user",
                    content=message["content"],
                    timestamp=datetime.utcnow()
                )
                db.add(db_message)
                await db.commit()
                break
            
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
            
            # Get conversation history
            conversation_history = await rag_engine.get_conversation_history(
                agent_id, chat_message.conversation_id
            )
            
            # Process message through production RAG engine
            response = await rag_engine.generate_response(
                message=chat_message,
                agent_id=agent_id,
                conversation_history=conversation_history
            )
            
            # Track message usage
            if user_id:
                async for db in get_db():
                    await BillingService.track_usage(
                        user_id, "message", db, 1
                    )
                    break
            
            # Store agent response in database
            async for db in get_db():
                # Handle rich content - serialize to JSON string for storage
                content_to_store = response.content
                if isinstance(response.content, dict):
                    content_to_store = json.dumps(response.content)
                
                agent_message = DBMessage(
                    conversation_id=conversation_id,
                    sender="agent",
                    content=content_to_store,
                    timestamp=datetime.utcnow()
                )
                db.add(agent_message)
                await db.commit()
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
        # Mark conversation as ended
        if conversation_id:
            async for db in get_db():
                result = await db.execute(
                    select(DBConversation).where(DBConversation.id == conversation_id)
                )
                conv = result.scalar_one_or_none()
                if conv:
                    conv.ended_at = datetime.utcnow()
                    await db.commit()
                break
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket, agent_id)

@app.post("/api/chat/message")
async def send_message(agent_id: str, message: ChatMessage):
    """REST endpoint for sending chat messages (fallback for non-WebSocket clients)"""
    try:
        # Get conversation history
        conversation_history = await rag_engine.get_conversation_history(
            agent_id, message.conversation_id
        )
        
        # Process message through production RAG engine
        response = await rag_engine.generate_response(
            message=message,
            agent_id=agent_id,
            conversation_history=conversation_history
        )
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

@app.get("/api/metrics/conversations/trends")
async def get_conversation_trends(days: int = 7):
    """Get conversation trends over specified days"""
    try:
        trends = await metrics_tracker.get_conversation_trends(days)
        return trends
    except Exception as e:
        logger.error(f"Error fetching conversation trends: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch trends")

@app.get("/api/metrics/agents/{agent_id}/performance")
async def get_agent_performance(agent_id: str, days: int = 30):
    """Get detailed performance metrics for a specific agent"""
    try:
        performance = await metrics_tracker.get_agent_performance(agent_id, days)
        return performance
    except Exception as e:
        logger.error(f"Error fetching agent performance: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch performance")

@app.get("/api/metrics/engagement/patterns")
async def get_engagement_patterns():
    """Get user engagement patterns and peak usage times"""
    try:
        patterns = await metrics_tracker.get_engagement_patterns()
        return patterns
    except Exception as e:
        logger.error(f"Error fetching engagement patterns: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch patterns")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.HOST, port=settings.PORT, reload=True)