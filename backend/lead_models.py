"""
Lead management models for NETVEXA.

Handles lead capture, human handoff requests, and lead scoring.
"""

from sqlalchemy import Column, String, DateTime, JSON, Float, Integer, Text, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from database import Base


class LeadStatus(enum.Enum):
    """Lead lifecycle status"""
    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    CONVERTED = "converted"
    LOST = "lost"


class LeadSource(enum.Enum):
    """Lead source tracking"""
    CHAT_WIDGET = "chat_widget"
    CONTACT_FORM = "contact_form"
    API = "api"
    MANUAL = "manual"
    IMPORT = "import"


class HandoffStatus(enum.Enum):
    """Human handoff request status"""
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Lead(Base):
    __tablename__ = "leads"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = Column(String, ForeignKey("conversations.id"), nullable=True)
    agent_id = Column(String, ForeignKey("agents.id"), nullable=False)
    
    # Contact Information
    email = Column(String, nullable=False, index=True)
    name = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    company = Column(String, nullable=True)
    
    # Lead Details
    status = Column(Enum(LeadStatus), default=LeadStatus.NEW)
    source = Column(Enum(LeadSource), default=LeadSource.CHAT_WIDGET)
    score = Column(Float, default=0.0)  # Lead quality score 0-100
    
    # Tracking
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    contacted_at = Column(DateTime, nullable=True)
    
    # Additional Data
    custom_fields = Column(JSON, default={})  # Flexible field storage
    notes = Column(Text, nullable=True)
    tags = Column(JSON, default=[])
    
    # Relationships
    conversation = relationship("Conversation", backref="lead_info")
    agent = relationship("Agent", backref="captured_leads")
    handoff_requests = relationship("HandoffRequest", back_populates="lead")


class HandoffRequest(Base):
    __tablename__ = "handoff_requests"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    lead_id = Column(String, ForeignKey("leads.id"), nullable=False)
    conversation_id = Column(String, ForeignKey("conversations.id"), nullable=False)
    agent_id = Column(String, ForeignKey("agents.id"), nullable=False)
    
    # Request Details
    status = Column(Enum(HandoffStatus), default=HandoffStatus.PENDING)
    priority = Column(String, default="normal")  # low, normal, high, urgent
    reason = Column(Text, nullable=True)
    
    # Assignment
    assigned_to = Column(String, nullable=True)  # Human agent ID
    assigned_at = Column(DateTime, nullable=True)
    
    # Timing
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Context
    conversation_summary = Column(Text, nullable=True)
    sentiment = Column(String, nullable=True)  # positive, neutral, negative
    
    # Relationships
    lead = relationship("Lead", back_populates="handoff_requests")
    conversation = relationship("Conversation", backref="handoff_request")
    agent = relationship("Agent", backref="handoff_requests")


class LeadForm(Base):
    __tablename__ = "lead_forms"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    agent_id = Column(String, ForeignKey("agents.id"), nullable=False)
    
    # Form Configuration
    name = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    
    # Form Fields Configuration
    fields = Column(JSON, nullable=False)
    # Example structure:
    # [
    #   {"name": "email", "type": "email", "required": true, "label": "Email"},
    #   {"name": "name", "type": "text", "required": true, "label": "Full Name"},
    #   {"name": "company", "type": "text", "required": false, "label": "Company"},
    #   {"name": "phone", "type": "tel", "required": false, "label": "Phone"}
    # ]
    
    # Form Triggers
    trigger_conditions = Column(JSON, default={})
    # Example: {"keywords": ["pricing", "demo", "contact"], "message_count": 5}
    
    # Styling
    custom_styles = Column(JSON, default={})
    
    # Tracking
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    submission_count = Column(Integer, default=0)
    
    # Relationships
    agent = relationship("Agent", backref="lead_forms")


# Import uuid at the top of the file
import uuid