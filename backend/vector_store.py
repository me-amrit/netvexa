"""
PostgreSQL pgvector implementation for NETVEXA
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from datetime import datetime
import uuid
import json

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
from pgvector.sqlalchemy import Vector

from database import KnowledgeDocument, get_session
from embedding_providers import BaseEmbeddingProvider

logger = logging.getLogger(__name__)

class PgVectorStore:
    """PostgreSQL vector store using pgvector extension"""
    
    def __init__(self, embedding_provider: BaseEmbeddingProvider, embedding_dim: int = 768):
        self.embedding_provider = embedding_provider
        self.embedding_dim = embedding_dim
        
    async def add_documents(
        self, 
        agent_id: str,
        documents: List[Dict[str, Any]]
    ) -> List[str]:
        """Add documents with embeddings to the database"""
        document_ids = []
        
        async for session in get_session():
            try:
                for doc in documents:
                    # Generate embedding
                    embedding = await self.embedding_provider.embed_text(doc['content'])
                    
                    # Create document
                    doc_id = doc.get('id', str(uuid.uuid4()))
                    knowledge_doc = KnowledgeDocument(
                        id=doc_id,
                        agent_id=agent_id,
                        title=doc.get('title', ''),
                        content=doc['content'],
                        url=doc.get('url'),
                        meta_data=doc.get('metadata', {}),
                        embedding=embedding
                    )
                    
                    session.add(knowledge_doc)
                    document_ids.append(doc_id)
                
                await session.commit()
                logger.info(f"Added {len(documents)} documents to database for agent {agent_id}")
                
            except Exception as e:
                await session.rollback()
                logger.error(f"Error adding documents: {e}")
                raise
                
        return document_ids
    
    async def similarity_search(
        self,
        agent_id: str,
        query: str,
        k: int = 3,
        threshold: float = 0.7
    ) -> List[Tuple[KnowledgeDocument, float]]:
        """Search for similar documents using cosine similarity"""
        
        # Generate query embedding
        query_embedding = await self.embedding_provider.embed_text(query)
        
        async for session in get_session():
            try:
                # Use pgvector's cosine distance operator (<=>)
                # Note: pgvector returns distance, not similarity, so we need to convert
                # Format embedding as PostgreSQL array string
                embedding_str = '[' + ','.join(map(str, query_embedding)) + ']'
                
                stmt = text("""
                    SELECT 
                        id, agent_id, title, content, url, meta_data, 
                        created_at, updated_at,
                        1 - (embedding <=> :query_embedding ::vector) as similarity
                    FROM knowledge_documents
                    WHERE agent_id = :agent_id
                        AND 1 - (embedding <=> :query_embedding ::vector) > :threshold
                    ORDER BY similarity DESC
                    LIMIT :k
                """)
                
                result = await session.execute(
                    stmt,
                    {
                        "query_embedding": embedding_str,
                        "agent_id": agent_id,
                        "threshold": threshold,
                        "k": k
                    }
                )
                
                documents = []
                for row in result:
                    doc = KnowledgeDocument(
                        id=row.id,
                        agent_id=row.agent_id,
                        title=row.title,
                        content=row.content,
                        url=row.url,
                        meta_data=row.meta_data,
                        created_at=row.created_at,
                        updated_at=row.updated_at
                    )
                    similarity = row.similarity
                    documents.append((doc, similarity))
                
                logger.info(f"Found {len(documents)} similar documents for query")
                return documents
                
            except Exception as e:
                logger.error(f"Error searching documents: {e}")
                raise
    
    async def get_all_documents(self, agent_id: str) -> List[KnowledgeDocument]:
        """Get all documents for an agent"""
        async for session in get_session():
            try:
                stmt = select(KnowledgeDocument).where(
                    KnowledgeDocument.agent_id == agent_id
                )
                result = await session.execute(stmt)
                documents = result.scalars().all()
                return documents
            except Exception as e:
                logger.error(f"Error getting documents: {e}")
                raise
    
    async def delete_document(self, document_id: str) -> bool:
        """Delete a document by ID"""
        async for session in get_session():
            try:
                stmt = select(KnowledgeDocument).where(
                    KnowledgeDocument.id == document_id
                )
                result = await session.execute(stmt)
                document = result.scalar_one_or_none()
                
                if document:
                    await session.delete(document)
                    await session.commit()
                    logger.info(f"Deleted document {document_id}")
                    return True
                else:
                    logger.warning(f"Document {document_id} not found")
                    return False
                    
            except Exception as e:
                await session.rollback()
                logger.error(f"Error deleting document: {e}")
                raise
    
    async def clear_agent_documents(self, agent_id: str) -> int:
        """Clear all documents for an agent"""
        async for session in get_session():
            try:
                stmt = select(KnowledgeDocument).where(
                    KnowledgeDocument.agent_id == agent_id
                )
                result = await session.execute(stmt)
                documents = result.scalars().all()
                
                count = len(documents)
                for doc in documents:
                    await session.delete(doc)
                
                await session.commit()
                logger.info(f"Cleared {count} documents for agent {agent_id}")
                return count
                
            except Exception as e:
                await session.rollback()
                logger.error(f"Error clearing documents: {e}")
                raise