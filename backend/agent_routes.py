"""
Agent management API routes for NETVEXA platform.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Optional
from pydantic import BaseModel
import uuid
import logging

from database import async_session, Agent, User, Conversation, KnowledgeDocument
from auth import get_current_user, get_current_user_or_api_key
from models import AgentConfig
from metrics import metrics_tracker

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/agents", tags=["agents"])


class AgentCreate(BaseModel):
    name: str
    personality: Optional[dict] = {
        "tone": "professional",
        "language": "en",
        "response_style": "concise"
    }
    welcome_message: Optional[str] = "Hello! How can I help you today?"
    
class AgentUpdate(BaseModel):
    name: Optional[str] = None
    personality: Optional[dict] = None
    welcome_message: Optional[str] = None
    is_active: Optional[bool] = None

class AgentResponse(BaseModel):
    id: str
    name: str
    config: dict
    created_at: str
    updated_at: str
    conversation_count: Optional[int] = 0
    document_count: Optional[int] = 0


@router.post("/", response_model=AgentResponse, status_code=status.HTTP_201_CREATED)
async def create_agent(
    agent_data: AgentCreate,
    auth_info: dict = Depends(get_current_user_or_api_key)
):
    """Create a new agent for the authenticated user."""
    user = auth_info["user"]
    
    async with async_session() as session:
        # Check agent limit (5 agents per user for now)
        existing_agents = await session.execute(
            select(Agent).where(Agent.user_id == user.id)
        )
        agent_count = len(existing_agents.scalars().all())
        
        if agent_count >= 5:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum number of agents reached (5)"
            )
        
        # Create new agent
        agent = Agent(
            user_id=user.id,
            name=agent_data.name,
            config={
                "personality": agent_data.personality,
                "welcome_message": agent_data.welcome_message,
                "is_active": True
            }
        )
        
        session.add(agent)
        await session.commit()
        await session.refresh(agent)
        
        # Track agent creation
        await metrics_tracker.track_event("agent_created", {
            "user_id": user.id,
            "agent_id": agent.id,
            "auth_type": auth_info["auth_type"]
        })
        
        return AgentResponse(
            id=agent.id,
            name=agent.name,
            config=agent.config,
            created_at=agent.created_at.isoformat(),
            updated_at=agent.updated_at.isoformat()
        )


@router.get("/", response_model=List[AgentResponse])
async def list_agents(
    auth_info: dict = Depends(get_current_user_or_api_key)
):
    """List all agents for the authenticated user."""
    user = auth_info["user"]
    
    async with async_session() as session:
        result = await session.execute(
            select(Agent).where(Agent.user_id == user.id).order_by(Agent.created_at.desc())
        )
        agents = result.scalars().all()
        
        # Get counts for each agent
        agent_responses = []
        for agent in agents:
            # Count conversations
            conv_count = await session.execute(
                select(Conversation).where(Conversation.agent_id == agent.id)
            )
            conversation_count = len(conv_count.scalars().all())
            
            # Count documents
            doc_count = await session.execute(
                select(KnowledgeDocument).where(KnowledgeDocument.agent_id == agent.id)
            )
            document_count = len(doc_count.scalars().all())
            
            agent_responses.append(
                AgentResponse(
                    id=agent.id,
                    name=agent.name,
                    config=agent.config,
                    created_at=agent.created_at.isoformat(),
                    updated_at=agent.updated_at.isoformat(),
                    conversation_count=conversation_count,
                    document_count=document_count
                )
            )
        
        return agent_responses


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(
    agent_id: str,
    auth_info: dict = Depends(get_current_user_or_api_key)
):
    """Get a specific agent by ID."""
    user = auth_info["user"]
    
    async with async_session() as session:
        result = await session.execute(
            select(Agent).where(
                and_(Agent.id == agent_id, Agent.user_id == user.id)
            )
        )
        agent = result.scalar_one_or_none()
        
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Agent not found"
            )
        
        # Get counts
        conv_count = await session.execute(
            select(Conversation).where(Conversation.agent_id == agent.id)
        )
        conversation_count = len(conv_count.scalars().all())
        
        doc_count = await session.execute(
            select(KnowledgeDocument).where(KnowledgeDocument.agent_id == agent.id)
        )
        document_count = len(doc_count.scalars().all())
        
        return AgentResponse(
            id=agent.id,
            name=agent.name,
            config=agent.config,
            created_at=agent.created_at.isoformat(),
            updated_at=agent.updated_at.isoformat(),
            conversation_count=conversation_count,
            document_count=document_count
        )


@router.put("/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: str,
    agent_data: AgentUpdate,
    auth_info: dict = Depends(get_current_user_or_api_key)
):
    """Update an agent."""
    user = auth_info["user"]
    
    async with async_session() as session:
        result = await session.execute(
            select(Agent).where(
                and_(Agent.id == agent_id, Agent.user_id == user.id)
            )
        )
        agent = result.scalar_one_or_none()
        
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Agent not found"
            )
        
        # Update fields
        if agent_data.name is not None:
            agent.name = agent_data.name
        
        if agent_data.personality is not None:
            agent.config["personality"] = agent_data.personality
        
        if agent_data.welcome_message is not None:
            agent.config["welcome_message"] = agent_data.welcome_message
        
        if agent_data.is_active is not None:
            agent.config["is_active"] = agent_data.is_active
        
        await session.commit()
        await session.refresh(agent)
        
        # Track agent update
        await metrics_tracker.track_event("agent_updated", {
            "user_id": user.id,
            "agent_id": agent.id
        })
        
        return AgentResponse(
            id=agent.id,
            name=agent.name,
            config=agent.config,
            created_at=agent.created_at.isoformat(),
            updated_at=agent.updated_at.isoformat()
        )


@router.delete("/{agent_id}")
async def delete_agent(
    agent_id: str,
    auth_info: dict = Depends(get_current_user_or_api_key)
):
    """Delete an agent and all associated data."""
    user = auth_info["user"]
    
    async with async_session() as session:
        result = await session.execute(
            select(Agent).where(
                and_(Agent.id == agent_id, Agent.user_id == user.id)
            )
        )
        agent = result.scalar_one_or_none()
        
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Agent not found"
            )
        
        # Delete agent (cascades to conversations, messages, documents)
        await session.delete(agent)
        await session.commit()
        
        # Track agent deletion
        await metrics_tracker.track_event("agent_deleted", {
            "user_id": user.id,
            "agent_id": agent.id
        })
        
        return {"message": "Agent deleted successfully"}


@router.get("/{agent_id}/config")
async def get_agent_config(agent_id: str):
    """Get agent configuration (public endpoint for chat widget)."""
    async with async_session() as session:
        result = await session.execute(
            select(Agent).where(Agent.id == agent_id)
        )
        agent = result.scalar_one_or_none()
        
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Agent not found"
            )
        
        # Check if agent is active
        if not agent.config.get("is_active", True):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Agent is not active"
            )
        
        return AgentConfig(
            id=agent.id,
            name=agent.name,
            personality=agent.config.get("personality", {
                "tone": "professional",
                "language": "en",
                "response_style": "concise"
            }),
            welcome_message=agent.config.get("welcome_message", "Hello! How can I help you today?")
        )


@router.post("/{agent_id}/test-message")
async def test_agent_message(
    agent_id: str,
    message: str,
    auth_info: dict = Depends(get_current_user_or_api_key)
):
    """Test an agent with a sample message."""
    user = auth_info["user"]
    
    # Verify agent ownership
    async with async_session() as session:
        result = await session.execute(
            select(Agent).where(
                and_(Agent.id == agent_id, Agent.user_id == user.id)
            )
        )
        agent = result.scalar_one_or_none()
        
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Agent not found"
            )
    
    # Import RAG engine here to avoid circular import
    from rag_engine import RAGEngine
    rag_engine = RAGEngine()
    
    # Process the test message
    try:
        # Check if agent has any knowledge documents
        response_context = await rag_engine.get_relevant_context(message, agent_id)
        
        # Generate response
        response = await rag_engine.generate_response(
            message=message,
            context=response_context,
            agent_config=agent.config
        )
        
        return {
            "message": message,
            "response": response,
            "context_used": bool(response_context)
        }
        
    except Exception as e:
        logger.error(f"Error testing agent: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing message: {str(e)}"
        )