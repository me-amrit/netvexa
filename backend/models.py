from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, List, Any
from enum import Enum

class SenderType(str, Enum):
    USER = "user"
    AGENT = "agent"
    SYSTEM = "system"

class ChatMessage(BaseModel):
    content: str
    conversation_id: str
    sender: SenderType
    timestamp: datetime = datetime.now()
    metadata: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    content: str
    timestamp: datetime = datetime.now()
    suggestions: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None

class AgentConfig(BaseModel):
    id: str
    name: str
    personality: Dict[str, Any]
    appearance: Optional[Dict[str, Any]] = None
    is_active: bool = True

class KnowledgeDocument(BaseModel):
    id: Optional[str] = None
    agent_id: str
    title: str
    content: str
    url: Optional[str] = None
    metadata: Dict[str, Any] = {}
    embedding: Optional[List[float]] = None
    created_at: datetime = datetime.now()

class IngestionJob(BaseModel):
    id: str
    agent_id: str
    status: str = "pending"
    progress: float = 0.0
    documents_processed: int = 0
    total_documents: int = 0
    error: Optional[str] = None
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()