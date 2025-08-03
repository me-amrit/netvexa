"""
Knowledge management API routes for document ingestion and search
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
import logging
import os
import tempfile

from database import get_db, User
from auth import get_current_user
from rag import ProductionRAGEngine
from billing_service import BillingService

router = APIRouter(prefix="/api/knowledge", tags=["knowledge"])
logger = logging.getLogger(__name__)

# Initialize RAG engine
rag_engine = ProductionRAGEngine()


class IngestURLRequest(BaseModel):
    url: str
    agent_id: str
    metadata: Optional[Dict[str, Any]] = None


class IngestTextRequest(BaseModel):
    text: str
    agent_id: str
    title: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class SearchRequest(BaseModel):
    query: str
    agent_id: str
    k: Optional[int] = 5
    filters: Optional[Dict[str, Any]] = None
    use_reranking: Optional[bool] = True


class SearchResponse(BaseModel):
    results: List[Dict[str, Any]]
    total_results: int
    search_time_ms: float


@router.post("/ingest/file")
async def ingest_file(
    file: UploadFile = File(...),
    agent_id: str = Form(...),
    metadata: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Upload and ingest a document file"""
    try:
        # Check if user owns the agent
        from database import Agent
        from sqlalchemy import select
        
        result = await db.execute(
            select(Agent).where(Agent.id == agent_id, Agent.user_id == current_user.id)
        )
        agent = result.scalar_one_or_none()
        
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Check document processing limits
        can_process = await BillingService.check_usage_limits(
            current_user.id, "document", db
        )
        
        if not can_process:
            raise HTTPException(
                status_code=403,
                detail="Document processing limit reached. Please upgrade your subscription."
            )
        
        # Parse metadata if provided
        parsed_metadata = {}
        if metadata:
            import json
            try:
                parsed_metadata = json.loads(metadata)
            except:
                pass
        
        # Add file info to metadata
        parsed_metadata.update({
            'original_filename': file.filename,
            'content_type': file.content_type,
            'size': file.size
        })
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        try:
            # Ingest document
            result = await rag_engine.ingest_document(
                file_path=tmp_file_path,
                agent_id=agent_id,
                metadata=parsed_metadata
            )
            
            # Track usage
            await BillingService.track_usage(
                current_user.id, "document_processed", 1, db
            )
            
            return {
                "status": "success",
                "message": f"Document ingested successfully",
                "details": result.to_dict()
            }
            
        finally:
            # Clean up temp file
            os.unlink(tmp_file_path)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error ingesting file: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ingest/text")
async def ingest_text(
    request: IngestTextRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Ingest raw text content"""
    try:
        # Check if user owns the agent
        from database import Agent
        from sqlalchemy import select
        
        result = await db.execute(
            select(Agent).where(Agent.id == request.agent_id, Agent.user_id == current_user.id)
        )
        agent = result.scalar_one_or_none()
        
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Create temporary file with text content
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as tmp_file:
            tmp_file.write(request.text)
            tmp_file_path = tmp_file.name
        
        try:
            # Prepare metadata
            metadata = request.metadata or {}
            metadata['title'] = request.title or 'Text Document'
            metadata['source'] = 'text_ingestion'
            
            # Ingest document
            result = await rag_engine.ingest_document(
                file_path=tmp_file_path,
                agent_id=request.agent_id,
                metadata=metadata
            )
            
            # Track usage
            await BillingService.track_usage(
                current_user.id, "document_processed", 1, db
            )
            
            return {
                "status": "success",
                "message": f"Text ingested successfully",
                "details": result.to_dict()
            }
            
        finally:
            # Clean up temp file
            os.unlink(tmp_file_path)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error ingesting text: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ingest/url")
async def ingest_url(
    request: IngestURLRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Ingest content from a URL"""
    try:
        # Check if user owns the agent
        from database import Agent
        from sqlalchemy import select
        
        result = await db.execute(
            select(Agent).where(Agent.id == request.agent_id, Agent.user_id == current_user.id)
        )
        agent = result.scalar_one_or_none()
        
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # For now, return a job ID (full implementation would crawl and process)
        import uuid
        job_id = str(uuid.uuid4())
        
        # In production, this would:
        # 1. Queue a job to crawl the URL
        # 2. Extract and clean the content
        # 3. Process through the RAG pipeline
        
        return {
            "status": "processing",
            "job_id": job_id,
            "message": "URL ingestion job created. Check job status for updates."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating URL ingestion job: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search", response_model=SearchResponse)
async def search_knowledge(
    request: SearchRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Search the knowledge base"""
    try:
        # Check if user owns the agent
        from database import Agent
        from sqlalchemy import select
        
        result = await db.execute(
            select(Agent).where(Agent.id == request.agent_id, Agent.user_id == current_user.id)
        )
        agent = result.scalar_one_or_none()
        
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Perform search
        import time
        start_time = time.time()
        
        search_results = await rag_engine.search(
            query=request.query,
            agent_id=request.agent_id,
            k=request.k,
            filters=request.filters,
            use_reranking=request.use_reranking
        )
        
        search_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        # Format results
        formatted_results = []
        for result in search_results:
            formatted_results.append({
                'document_id': result.document_id,
                'content': result.content,
                'score': result.combined_score,
                'vector_score': result.vector_score,
                'keyword_score': result.keyword_score,
                'highlights': result.highlights,
                'metadata': result.metadata
            })
        
        return SearchResponse(
            results=formatted_results,
            total_results=len(formatted_results),
            search_time_ms=search_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error searching knowledge base: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agents/{agent_id}/documents")
async def list_agent_documents(
    agent_id: str,
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all documents for an agent"""
    try:
        # Check if user owns the agent
        from database import Agent, KnowledgeDocument
        from sqlalchemy import select
        
        result = await db.execute(
            select(Agent).where(Agent.id == agent_id, Agent.user_id == current_user.id)
        )
        agent = result.scalar_one_or_none()
        
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Get documents with unique entries (group by chunk metadata)
        # In a real implementation, we'd have a separate documents table
        result = await db.execute(
            select(KnowledgeDocument)
            .where(KnowledgeDocument.agent_id == agent_id)
            .offset(skip)
            .limit(limit)
        )
        documents = result.scalars().all()
        
        # Group by original document
        unique_docs = {}
        for doc in documents:
            # Extract original document info from metadata
            doc_meta = doc.metadata or {}
            doc_info = doc_meta.get('document_metadata', {})
            custom_meta = doc_meta.get('custom_metadata', {})
            
            # Create a unique key for the document
            doc_key = custom_meta.get('original_filename', doc.title)
            
            if doc_key not in unique_docs:
                unique_docs[doc_key] = {
                    'id': doc.id,
                    'title': doc.title,
                    'filename': custom_meta.get('original_filename'),
                    'type': doc_info.get('type', 'unknown'),
                    'size': doc_info.get('size', 0),
                    'chunks': 1,
                    'created_at': doc.created_at.isoformat() if doc.created_at else None
                }
            else:
                unique_docs[doc_key]['chunks'] += 1
        
        return {
            "documents": list(unique_docs.values()),
            "total": len(unique_docs),
            "skip": skip,
            "limit": limit
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/documents/{document_id}")
async def delete_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a document and all its chunks"""
    try:
        # Get document
        from database import KnowledgeDocument
        from sqlalchemy import select, delete
        
        result = await db.execute(
            select(KnowledgeDocument).where(KnowledgeDocument.id == document_id)
        )
        document = result.scalar_one_or_none()
        
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Check if user owns the agent
        from database import Agent
        result = await db.execute(
            select(Agent).where(
                Agent.id == document.agent_id, 
                Agent.user_id == current_user.id
            )
        )
        agent = result.scalar_one_or_none()
        
        if not agent:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Delete all chunks with same original document
        # In production, we'd have better document tracking
        doc_metadata = document.metadata or {}
        custom_meta = doc_metadata.get('custom_metadata', {})
        original_filename = custom_meta.get('original_filename')
        
        if original_filename:
            # Delete all chunks from the same file
            await db.execute(
                delete(KnowledgeDocument).where(
                    KnowledgeDocument.agent_id == document.agent_id,
                    KnowledgeDocument.metadata['custom_metadata']['original_filename'].astext == original_filename
                )
            )
        else:
            # Just delete this document
            await db.delete(document)
        
        await db.commit()
        
        return {"status": "success", "message": "Document deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting document: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/update-embeddings/{agent_id}")
async def update_embeddings(
    agent_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update embeddings for documents without them"""
    try:
        # Check if user owns the agent
        from database import Agent
        from sqlalchemy import select
        
        result = await db.execute(
            select(Agent).where(Agent.id == agent_id, Agent.user_id == current_user.id)
        )
        agent = result.scalar_one_or_none()
        
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Update embeddings
        stats = await rag_engine.update_document_embeddings(agent_id)
        
        return {
            "status": "success",
            "message": "Embeddings updated",
            "stats": stats
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating embeddings: {e}")
        raise HTTPException(status_code=500, detail=str(e))
