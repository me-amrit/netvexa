from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy import Column, String, DateTime, JSON, Float, Integer, Text, ARRAY, Boolean, ForeignKey
from pgvector.sqlalchemy import Vector
from datetime import datetime
import uuid
import logging

from config import settings

logger = logging.getLogger(__name__)

# Create async engine with PostgreSQL
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

# Create async session factory
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Create base class for models
Base = declarative_base()

# Define database models
class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    company_name = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    agents = relationship("Agent", back_populates="user", cascade="all, delete-orphan")
    api_keys = relationship("ApiKey", back_populates="user", cascade="all, delete-orphan")
    subscription = relationship("Subscription", back_populates="user", uselist=False)
    usage_records = relationship("UsageRecord", back_populates="user")
    payments = relationship("Payment", back_populates="user")

class ApiKey(Base):
    __tablename__ = "api_keys"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    key = Column(String, unique=True, nullable=False, index=True)
    is_active = Column(Boolean, default=True)
    usage_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="api_keys")

class Agent(Base):
    __tablename__ = "agents"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    config = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="agents")
    conversations = relationship("Conversation", back_populates="agent", cascade="all, delete-orphan")

class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    agent_id = Column(String, ForeignKey("agents.id"), nullable=False)
    visitor_id = Column(String, nullable=True)
    lead_id = Column(String, nullable=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    meta_data = Column(JSON, default={})  # Renamed from metadata to avoid conflict
    
    # Relationships
    agent = relationship("Agent", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column(String, ForeignKey("conversations.id"), nullable=False)
    sender = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    meta_data = Column(JSON, default={})  # Renamed from metadata to avoid conflict
    
    # Relationships
    conversation = relationship("Conversation", back_populates="messages")

class KnowledgeDocument(Base):
    __tablename__ = "knowledge_documents"
    
    id = Column(String, primary_key=True)
    agent_id = Column(String, nullable=False)
    title = Column(String, nullable=True)
    content = Column(Text, nullable=False)
    url = Column(String, nullable=True)
    meta_data = Column(JSON, default={})  # Keep original name to avoid SQLAlchemy conflict
    embedding = Column(Vector())  # Dynamic dimension based on provider
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Helper property for easier access
    def get_metadata(self):
        return self.meta_data
    
    def set_metadata(self, value):
        self.meta_data = value

async def init_db():
    """Initialize database tables"""
    # Import billing models to ensure they're registered with SQLAlchemy
    from billing_models import Subscription, UsageRecord, Payment, PricingPlan
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database initialized successfully")

async def get_session() -> AsyncSession:
    """Get database session"""
    async with async_session() as session:
        yield session

# Alias for compatibility
get_db = get_session