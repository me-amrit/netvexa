"""
Lead management API routes.

Handles lead capture, retrieval, and human handoff requests.
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

from database import get_db
from auth import get_current_user
from lead_models import Lead, HandoffRequest, LeadForm, LeadStatus, LeadSource, HandoffStatus
from models import User
from email_service import send_lead_notification_email, send_handoff_notification_email

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/leads", tags=["leads"])


# Pydantic models
class LeadCreate(BaseModel):
    """Lead creation request"""
    conversation_id: Optional[str] = None
    agent_id: str
    email: EmailStr
    name: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    custom_fields: Optional[Dict[str, Any]] = {}
    source: Optional[LeadSource] = LeadSource.CHAT_WIDGET


class LeadUpdate(BaseModel):
    """Lead update request"""
    name: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    status: Optional[LeadStatus] = None
    score: Optional[float] = None
    notes: Optional[str] = None
    tags: Optional[List[str]] = None
    custom_fields: Optional[Dict[str, Any]] = None


class LeadResponse(BaseModel):
    """Lead response model"""
    id: str
    conversation_id: Optional[str]
    agent_id: str
    email: str
    name: Optional[str]
    phone: Optional[str]
    company: Optional[str]
    status: LeadStatus
    source: LeadSource
    score: float
    created_at: datetime
    updated_at: datetime
    custom_fields: Dict[str, Any]
    notes: Optional[str]
    tags: List[str]


class HandoffRequestCreate(BaseModel):
    """Human handoff request"""
    lead_id: str
    conversation_id: str
    agent_id: str
    priority: str = "normal"
    reason: Optional[str] = None


class HandoffRequestResponse(BaseModel):
    """Handoff request response"""
    id: str
    lead_id: str
    conversation_id: str
    agent_id: str
    status: HandoffStatus
    priority: str
    reason: Optional[str]
    assigned_to: Optional[str]
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]


class LeadFormConfig(BaseModel):
    """Lead form configuration"""
    name: str
    fields: List[Dict[str, Any]]
    trigger_conditions: Optional[Dict[str, Any]] = {}
    custom_styles: Optional[Dict[str, Any]] = {}


# Lead CRUD operations
@router.post("/", response_model=LeadResponse)
async def create_lead(
    lead_data: LeadCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Create a new lead from chat conversation"""
    try:
        # Check if lead already exists for this email
        existing_lead = await db.execute(
            select(Lead).where(
                and_(
                    Lead.email == lead_data.email,
                    Lead.agent_id == lead_data.agent_id
                )
            )
        )
        existing = existing_lead.scalar_one_or_none()
        
        if existing:
            # Update existing lead
            for key, value in lead_data.dict(exclude_unset=True).items():
                if hasattr(existing, key) and value is not None:
                    setattr(existing, key, value)
            existing.updated_at = datetime.utcnow()
            lead = existing
        else:
            # Create new lead
            lead = Lead(**lead_data.dict())
            db.add(lead)
        
        await db.commit()
        await db.refresh(lead)
        
        # Get agent owner's email for notification
        from database import Agent
        agent = await db.get(Agent, lead.agent_id)
        if agent:
            user = await db.get(User, agent.user_id)
            if user:
                # Send email notification in background
                background_tasks.add_task(send_lead_notification_email, lead, user.email)
        
        return lead
    except Exception as e:
        logger.error(f"Error creating lead: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[LeadResponse])
async def get_leads(
    agent_id: Optional[str] = None,
    status: Optional[LeadStatus] = None,
    limit: int = 100,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get leads with optional filtering"""
    try:
        query = select(Lead)
        
        # Filter by user's agents
        from database import Agent
        user_agents = await db.execute(
            select(Agent.id).where(Agent.user_id == current_user.id)
        )
        agent_ids = [a[0] for a in user_agents]
        query = query.where(Lead.agent_id.in_(agent_ids))
        
        # Additional filters
        if agent_id:
            query = query.where(Lead.agent_id == agent_id)
        if status:
            query = query.where(Lead.status == status)
        
        query = query.order_by(Lead.created_at.desc()).limit(limit).offset(offset)
        
        result = await db.execute(query)
        leads = result.scalars().all()
        
        return leads
    except Exception as e:
        logger.error(f"Error fetching leads: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{lead_id}", response_model=LeadResponse)
async def get_lead(
    lead_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific lead"""
    try:
        lead = await db.get(Lead, lead_id)
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")
        
        # Verify user owns the agent
        from database import Agent
        agent = await db.get(Agent, lead.agent_id)
        if not agent or agent.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        return lead
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching lead: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{lead_id}", response_model=LeadResponse)
async def update_lead(
    lead_id: str,
    lead_update: LeadUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update lead information"""
    try:
        lead = await db.get(Lead, lead_id)
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")
        
        # Verify user owns the agent
        from database import Agent
        agent = await db.get(Agent, lead.agent_id)
        if not agent or agent.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Update fields
        for key, value in lead_update.dict(exclude_unset=True).items():
            if value is not None:
                setattr(lead, key, value)
        
        lead.updated_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(lead)
        
        return lead
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating lead: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Human handoff operations
@router.post("/handoff", response_model=HandoffRequestResponse)
async def create_handoff_request(
    handoff_data: HandoffRequestCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Create a human handoff request"""
    try:
        # Verify lead exists
        lead = await db.get(Lead, handoff_data.lead_id)
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")
        
        # Create handoff request
        handoff = HandoffRequest(**handoff_data.dict())
        db.add(handoff)
        
        await db.commit()
        await db.refresh(handoff)
        
        # Get lead and user email for notification
        from database import Agent
        agent = await db.get(Agent, handoff.agent_id)
        if agent:
            user = await db.get(User, agent.user_id)
            if user:
                # Notify human agents in background
                background_tasks.add_task(send_handoff_notification_email, handoff, user.email, lead)
        
        return handoff
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating handoff request: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/handoff/pending", response_model=List[HandoffRequestResponse])
async def get_pending_handoffs(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get pending handoff requests for user's agents"""
    try:
        # Get user's agents
        from database import Agent
        user_agents = await db.execute(
            select(Agent.id).where(Agent.user_id == current_user.id)
        )
        agent_ids = [a[0] for a in user_agents]
        
        # Get pending handoffs
        result = await db.execute(
            select(HandoffRequest)
            .where(
                and_(
                    HandoffRequest.agent_id.in_(agent_ids),
                    HandoffRequest.status == HandoffStatus.PENDING
                )
            )
            .order_by(HandoffRequest.created_at)
        )
        
        handoffs = result.scalars().all()
        return handoffs
    except Exception as e:
        logger.error(f"Error fetching handoff requests: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Lead form configuration
@router.post("/forms", response_model=Dict[str, str])
async def create_lead_form(
    agent_id: str,
    form_config: LeadFormConfig,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create or update lead capture form for an agent"""
    try:
        # Verify user owns the agent
        from database import Agent
        agent = await db.get(Agent, agent_id)
        if not agent or agent.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Check if form exists
        existing_form = await db.execute(
            select(LeadForm).where(
                and_(
                    LeadForm.agent_id == agent_id,
                    LeadForm.name == form_config.name
                )
            )
        )
        form = existing_form.scalar_one_or_none()
        
        if form:
            # Update existing form
            form.fields = form_config.fields
            form.trigger_conditions = form_config.trigger_conditions
            form.custom_styles = form_config.custom_styles
            form.updated_at = datetime.utcnow()
        else:
            # Create new form
            form = LeadForm(
                agent_id=agent_id,
                **form_config.dict()
            )
            db.add(form)
        
        await db.commit()
        await db.refresh(form)
        
        return {"message": "Lead form configured successfully", "form_id": form.id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating lead form: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/forms/{agent_id}")
async def get_agent_lead_forms(
    agent_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get lead forms for an agent (public endpoint for widget)"""
    try:
        result = await db.execute(
            select(LeadForm)
            .where(
                and_(
                    LeadForm.agent_id == agent_id,
                    LeadForm.is_active == True
                )
            )
        )
        forms = result.scalars().all()
        
        return {
            "forms": [
                {
                    "id": form.id,
                    "name": form.name,
                    "fields": form.fields,
                    "trigger_conditions": form.trigger_conditions,
                    "custom_styles": form.custom_styles
                }
                for form in forms
            ]
        }
    except Exception as e:
        logger.error(f"Error fetching lead forms: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Analytics endpoints
@router.get("/analytics/summary")
async def get_lead_analytics(
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get lead analytics summary"""
    try:
        from datetime import timedelta
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Get user's agents
        from database import Agent
        user_agents = await db.execute(
            select(Agent.id).where(Agent.user_id == current_user.id)
        )
        agent_ids = [a[0] for a in user_agents]
        
        # Get lead statistics
        total_leads = await db.execute(
            select(func.count(Lead.id))
            .where(
                and_(
                    Lead.agent_id.in_(agent_ids),
                    Lead.created_at >= start_date
                )
            )
        )
        
        leads_by_status = await db.execute(
            select(Lead.status, func.count(Lead.id))
            .where(
                and_(
                    Lead.agent_id.in_(agent_ids),
                    Lead.created_at >= start_date
                )
            )
            .group_by(Lead.status)
        )
        
        avg_score = await db.execute(
            select(func.avg(Lead.score))
            .where(
                and_(
                    Lead.agent_id.in_(agent_ids),
                    Lead.created_at >= start_date
                )
            )
        )
        
        return {
            "total_leads": total_leads.scalar() or 0,
            "leads_by_status": {
                status.value: count for status, count in leads_by_status
            },
            "average_score": float(avg_score.scalar() or 0),
            "period_days": days
        }
    except Exception as e:
        logger.error(f"Error fetching lead analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Note: Email notification functions are now handled by email_service.py