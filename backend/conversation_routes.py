"""
Conversation management API routes for NETVEXA platform.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List
from pydantic import BaseModel
import logging

from database import async_session, Conversation, Message, Agent
from auth import get_current_user_or_api_key

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/conversations", tags=["conversations"])


class MessageResponse(BaseModel):
    id: int
    conversation_id: str
    sender: str
    content: str
    timestamp: str


@router.get("/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_conversation_messages(
    conversation_id: str,
    auth_info: dict = Depends(get_current_user_or_api_key)
):
    """Get all messages for a conversation."""
    user = auth_info["user"]
    
    async with async_session() as session:
        # Verify conversation exists and user has access
        result = await session.execute(
            select(Conversation)
            .join(Agent, Conversation.agent_id == Agent.id)
            .where(
                and_(
                    Conversation.id == conversation_id,
                    Agent.user_id == user.id
                )
            )
        )
        conversation = result.scalar_one_or_none()
        
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        
        # Get messages
        result = await session.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.timestamp)
        )
        messages = result.scalars().all()
        
        return [
            MessageResponse(
                id=msg.id,
                conversation_id=msg.conversation_id,
                sender=msg.sender,
                content=msg.content,
                timestamp=msg.timestamp.isoformat() if msg.timestamp else ""
            )
            for msg in messages
        ]


@router.get("/{conversation_id}", response_model=dict)
async def get_conversation_detail(
    conversation_id: str,
    auth_info: dict = Depends(get_current_user_or_api_key)
):
    """Get conversation details with messages."""
    user = auth_info["user"]
    
    async with async_session() as session:
        # Verify conversation exists and user has access
        result = await session.execute(
            select(Conversation)
            .join(Agent, Conversation.agent_id == Agent.id)
            .where(
                and_(
                    Conversation.id == conversation_id,
                    Agent.user_id == user.id
                )
            )
        )
        conversation = result.scalar_one_or_none()
        
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )
        
        # Get messages
        result = await session.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.timestamp)
        )
        messages = result.scalars().all()
        
        return {
            "id": conversation.id,
            "agent_id": conversation.agent_id,
            "started_at": conversation.started_at.isoformat() if conversation.started_at else None,
            "ended_at": conversation.ended_at.isoformat() if conversation.ended_at else None,
            "visitor_id": conversation.visitor_id,
            "lead_captured": bool(conversation.lead_id),
            "messages": [
                {
                    "id": msg.id,
                    "sender": msg.sender,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat() if msg.timestamp else ""
                }
                for msg in messages
            ]
        }