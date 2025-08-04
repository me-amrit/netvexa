"""
Production-grade RAG engine with advanced features
"""
import os
import asyncio
import uuid
import hashlib
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import logging
import json
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
import redis.asyncio as redis

from config import settings
from models import ChatMessage, ChatResponse
from database import KnowledgeDocument, Agent, async_session, get_db
from llm_providers import LLMProviderFactory, LLMProviderWithFallback
from embedding_providers import EmbeddingProviderFactory, CachedEmbeddingProvider

from .chunking_strategies import get_chunker, ChunkMetadata
from .document_parsers import parse_document, ParsedDocument
from .hybrid_search import HybridSearchEngine, ReRanker, SearchResult
from rich_content_generator import RichContentGenerator

logger = logging.getLogger(__name__)


class DocumentIngestionResult:
    """Result of document ingestion"""
    
    def __init__(self):
        self.total_documents = 0
        self.total_chunks = 0
        self.successful_chunks = 0
        self.failed_chunks = 0
        self.errors = []
        self.document_ids = []
        self.processing_time = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'total_documents': self.total_documents,
            'total_chunks': self.total_chunks,
            'successful_chunks': self.successful_chunks,
            'failed_chunks': self.failed_chunks,
            'success_rate': self.successful_chunks / self.total_chunks if self.total_chunks > 0 else 0,
            'errors': self.errors,
            'document_ids': self.document_ids,
            'processing_time': self.processing_time
        }


class ProductionRAGEngine:
    """Production-grade RAG engine with advanced features"""
    
    def __init__(self):
        """Initialize the production RAG engine"""
        # Initialize Redis client
        self.redis_client = None
        if settings.REDIS_URL:
            try:
                self.redis_client = redis.from_url(settings.REDIS_URL)
                logger.info("Redis client initialized for caching")
            except Exception as e:
                logger.warning(f"Failed to initialize Redis: {e}")
        
        # Initialize LLM provider with fallback
        self.llm_provider = LLMProviderWithFallback()
        
        # Initialize embedding provider with caching
        embedding_provider = EmbeddingProviderFactory.create_provider()
        if self.redis_client:
            self.embedding_provider = CachedEmbeddingProvider(
                embedding_provider,
                self.redis_client
            )
        else:
            self.embedding_provider = embedding_provider
        
        # Initialize search components
        self.search_engine = HybridSearchEngine(
            vector_weight=0.7,
            keyword_weight=0.3,
            use_bm25=True
        )
        self.reranker = ReRanker(use_cross_encoder=False)
        
        # Initialize rich content generator
        self.rich_content_generator = RichContentGenerator()
        
        # Configuration
        self.chunk_size = settings.CHUNK_SIZE
        self.chunk_overlap = settings.CHUNK_OVERLAP
        self.top_k = settings.TOP_K_RETRIEVAL
        
        logger.info("Production RAG Engine initialized")
    
    async def ingest_document(self,
                            file_path: str = None,
                            file_content: bytes = None,
                            agent_id: str = None,
                            metadata: Optional[Dict[str, Any]] = None) -> DocumentIngestionResult:
        """
        Ingest a document into the knowledge base
        
        Args:
            file_path: Path to the document file
            file_content: Raw document content
            agent_id: Agent ID to associate with document
            metadata: Additional metadata for the document
        
        Returns:
            DocumentIngestionResult with ingestion details
        """
        start_time = datetime.now()
        result = DocumentIngestionResult()
        
        try:
            # Parse document
            logger.info(f"Parsing document: {file_path or 'raw content'}")
            parsed_doc = parse_document(file_path, file_content)
            result.total_documents = 1
            
            # Determine content type for chunking
            content_type = self._determine_content_type(parsed_doc, file_path)
            
            # Get appropriate chunker
            chunker = get_chunker(
                content_type=content_type,
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap
            )
            
            # Chunk the document
            chunks = chunker.chunk(parsed_doc.content, parsed_doc.metadata)
            result.total_chunks = len(chunks)
            logger.info(f"Created {len(chunks)} chunks from document")
            
            # Process chunks in batches
            batch_size = 10
            for i in range(0, len(chunks), batch_size):
                batch = chunks[i:i + batch_size]
                await self._process_chunk_batch(
                    batch, agent_id, parsed_doc, metadata, result
                )
            
            # Store document metadata
            if self.redis_client and agent_id:
                await self._store_document_metadata(
                    agent_id, file_path, parsed_doc, result
                )
            
        except Exception as e:
            logger.error(f"Error ingesting document: {e}")
            result.errors.append(str(e))
        
        result.processing_time = (datetime.now() - start_time).total_seconds()
        return result
    
    async def _process_chunk_batch(self,
                                 chunks: List[Tuple[str, ChunkMetadata]],
                                 agent_id: str,
                                 parsed_doc: ParsedDocument,
                                 metadata: Optional[Dict[str, Any]],
                                 result: DocumentIngestionResult):
        """Process a batch of chunks"""
        # Extract texts for embedding
        texts = [chunk_text for chunk_text, _ in chunks]
        
        try:
            # Generate embeddings for batch
            embeddings = await self.embedding_provider.embed_texts(texts)
            
            # Create documents
            async for db in get_db():
                for i, ((chunk_text, chunk_meta), embedding) in enumerate(zip(chunks, embeddings)):
                    try:
                        # Create document metadata
                        doc_metadata = {
                            'chunk_metadata': {
                                'chunk_id': chunk_meta.chunk_id,
                                'chunk_index': chunk_meta.chunk_index,
                                'total_chunks': result.total_chunks,
                                'start_char': chunk_meta.start_char,
                                'end_char': chunk_meta.end_char,
                                'word_count': chunk_meta.word_count,
                                'token_count': chunk_meta.token_count,
                                'has_code': chunk_meta.has_code,
                                'section_title': chunk_meta.section_title,
                                'page_number': chunk_meta.page_number
                            },
                            'document_metadata': parsed_doc.metadata,
                            'custom_metadata': metadata or {}
                        }
                        
                        # Create knowledge document
                        doc = KnowledgeDocument(
                            id=str(uuid.uuid4()),
                            agent_id=agent_id,
                            title=doc_metadata.get('document_metadata', {}).get('title', f'Chunk {chunk_meta.chunk_index}'),
                            content=chunk_text,
                            url=doc_metadata.get('custom_metadata', {}).get('url'),
                            embedding=embedding,
                            meta_data=doc_metadata
                        )
                        
                        db.add(doc)
                        result.document_ids.append(doc.id)
                        result.successful_chunks += 1
                        
                    except Exception as e:
                        logger.error(f"Error processing chunk {i}: {e}")
                        result.failed_chunks += 1
                        result.errors.append(f"Chunk {i}: {str(e)}")
                
                await db.commit()
                break
                
        except Exception as e:
            logger.error(f"Error processing chunk batch: {e}")
            result.failed_chunks += len(chunks)
            result.errors.append(f"Batch processing error: {str(e)}")
    
    def _determine_content_type(self, 
                              parsed_doc: ParsedDocument,
                              file_path: Optional[str]) -> str:
        """Determine content type for chunking strategy"""
        doc_type = parsed_doc.metadata.get('type', 'text')
        
        if doc_type == 'code':
            return 'code'
        elif doc_type == 'markdown':
            return 'markdown'
        elif doc_type in ['pdf', 'docx'] and parsed_doc.sections:
            return 'text'  # Use semantic chunking for structured docs
        else:
            return 'text'
    
    async def _store_document_metadata(self,
                                     agent_id: str,
                                     file_path: Optional[str],
                                     parsed_doc: ParsedDocument,
                                     result: DocumentIngestionResult):
        """Store document metadata in Redis for tracking"""
        try:
            doc_id = hashlib.md5(
                (file_path or str(uuid.uuid4())).encode()
            ).hexdigest()
            
            metadata = {
                'document_id': doc_id,
                'agent_id': agent_id,
                'file_path': file_path,
                'ingestion_time': datetime.now().isoformat(),
                'total_chunks': result.total_chunks,
                'successful_chunks': result.successful_chunks,
                'document_type': parsed_doc.metadata.get('type'),
                'document_metadata': parsed_doc.metadata
            }
            
            # Store with 30-day TTL
            await self.redis_client.setex(
                f"document:{agent_id}:{doc_id}",
                30 * 24 * 3600,
                json.dumps(metadata)
            )
            
        except Exception as e:
            logger.warning(f"Failed to store document metadata: {e}")
    
    async def search(self,
                   query: str,
                   agent_id: str,
                   k: int = None,
                   filters: Optional[Dict[str, Any]] = None,
                   use_reranking: bool = True) -> List[SearchResult]:
        """
        Search for relevant documents using hybrid search
        
        Args:
            query: Search query
            agent_id: Agent ID to search within
            k: Number of results to return
            filters: Additional filters
            use_reranking: Whether to use re-ranking
        
        Returns:
            List of search results
        """
        k = k or self.top_k
        
        try:
            # Generate query embedding
            query_embedding = await self.embedding_provider.embed_text(query)
            
            # Perform hybrid search
            async for db in get_db():
                results = await self.search_engine.search(
                    query=query,
                    query_embedding=query_embedding,
                    agent_id=agent_id,
                    k=k * 2 if use_reranking else k,
                    keyword_k=k * 3,
                    db=db,
                    filters=filters
                )
                break
            
            # Apply re-ranking if enabled
            if use_reranking and results:
                results = await self.reranker.rerank(query, results, k)
            
            return results[:k]
            
        except Exception as e:
            logger.error(f"Search error: {e}")
            return []
    
    async def generate_response(self,
                              message: ChatMessage,
                              agent_id: str,
                              conversation_history: Optional[List[Dict[str, str]]] = None,
                              max_context_length: int = 3000) -> ChatResponse:
        """
        Generate response using RAG
        
        Args:
            message: User message
            agent_id: Agent ID
            conversation_history: Previous conversation messages
            max_context_length: Maximum context length in tokens
        
        Returns:
            ChatResponse with generated answer
        """
        try:
            # Search for relevant documents
            search_results = await self.search(
                query=message.content,
                agent_id=agent_id,
                use_reranking=True
            )
            
            # Build context from search results
            context = self._build_context(search_results, max_context_length)
            
            # Get agent configuration
            agent_config = await self._get_agent_config(agent_id)
            
            # Build prompt
            prompt = self._build_prompt(
                query=message.content,
                context=context,
                conversation_history=conversation_history,
                agent_config=agent_config
            )
            
            # Generate response
            response_text = await self.llm_provider.complete(prompt)
            
            # Generate rich content if appropriate
            try:
                # Convert conversation history to proper format
                formatted_history = []
                if conversation_history:
                    for msg in conversation_history:
                        formatted_history.append({
                            'role': msg.get('role', 'user'),
                            'content': msg.get('content', ''),
                            'timestamp': msg.get('timestamp', datetime.now().isoformat())
                        })
                
                # Generate rich content
                rich_content = self.rich_content_generator.process_ai_response(
                    user_message=message.content,
                    ai_response=response_text,
                    conversation_history=formatted_history
                )
                
                # Use rich content if generated successfully
                final_response = rich_content
                
            except Exception as e:
                logger.warning(f"Failed to generate rich content, falling back to plain text: {e}")
                # Fallback to plain text wrapped in rich message format
                final_response = {
                    "type": "rich_message", 
                    "version": "1.0",
                    "content": [{"type": "text", "text": response_text}]
                }
            
            # Create response metadata
            metadata = {
                'agent_id': agent_id,
                'source_documents': len(search_results),
                'llm_provider': settings.LLM_PROVIDER,
                'search_method': 'hybrid',
                'used_reranking': True,
                'context_length': len(context),
                'source_ids': [r.document_id for r in search_results[:3]],
                'rich_content_generated': True
            }
            
            # Store conversation in cache
            if self.redis_client and conversation_history is not None:
                await self._update_conversation_cache(
                    agent_id, message, response_text, conversation_history
                )
            
            return ChatResponse(
                content=final_response,  # Now returns rich content object
                timestamp=datetime.now(),
                metadata=metadata
            )
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return ChatResponse(
                content="I apologize, but I encountered an error processing your request. Please try again.",
                timestamp=datetime.now(),
                metadata={'error': str(e)}
            )
    
    def _build_context(self, 
                      search_results: List[SearchResult],
                      max_length: int) -> str:
        """Build context from search results within token limit"""
        if not search_results:
            return ""
        
        context_parts = []
        current_length = 0
        
        for i, result in enumerate(search_results):
            # Format result with metadata
            source_info = ""
            if result.metadata.get('chunk_metadata', {}).get('section_title'):
                source_info = f" (Section: {result.metadata['chunk_metadata']['section_title']})"
            elif result.metadata.get('document_metadata', {}).get('title'):
                source_info = f" (Document: {result.metadata['document_metadata']['title']})"
            
            # Add result content
            result_text = f"[{i+1}] {result.content}{source_info}\n"
            
            # Check if adding this would exceed limit
            # Rough token estimation: 1 token ≈ 4 characters
            estimated_tokens = len(result_text) // 4
            
            if current_length + estimated_tokens > max_length:
                # Try to add a truncated version
                available_tokens = max_length - current_length
                if available_tokens > 50:  # Minimum useful context
                    truncated_length = available_tokens * 4
                    truncated_text = result_text[:truncated_length] + "...\n"
                    context_parts.append(truncated_text)
                break
            
            context_parts.append(result_text)
            current_length += estimated_tokens
        
        return "\n".join(context_parts)
    
    async def _get_agent_config(self, agent_id: str) -> Dict[str, Any]:
        """Get agent configuration"""
        try:
            async for db in get_db():
                result = await db.execute(
                    select(Agent).where(Agent.id == agent_id)
                )
                agent = result.scalar_one_or_none()
                
                if agent:
                    return {
                        'name': agent.name,
                        'description': getattr(agent, 'description', ''),
                        'personality': getattr(agent, 'personality', {}),
                        'instructions': getattr(agent, 'instructions', ''),
                        'capabilities': getattr(agent, 'capabilities', [])
                    }
                break
        except Exception as e:
            logger.warning(f"Failed to get agent config: {e}")
        
        # Return default config
        return {
            'name': 'Assistant',
            'description': 'AI assistant',
            'personality': {'tone': 'professional'},
            'instructions': '',
            'capabilities': []
        }
    
    def _build_prompt(self,
                     query: str,
                     context: str,
                     conversation_history: Optional[List[Dict[str, str]]],
                     agent_config: Dict[str, Any]) -> str:
        """Build prompt for LLM"""
        # Base system prompt
        system_prompt = f"""You are {agent_config['name']}, an AI assistant with the following characteristics:
Description: {agent_config.get('description', 'A helpful AI assistant')}
Personality: {json.dumps(agent_config.get('personality', {'tone': 'professional'}))}

Instructions:
{agent_config.get('instructions', 'Provide helpful, accurate, and professional responses.')}

Your task is to answer questions based on the provided context and your knowledge. 
Always cite your sources when using information from the context by referencing the source number [1], [2], etc."""

        # Add conversation history if available
        history_text = ""
        if conversation_history:
            history_text = "\n\nPrevious conversation:\n"
            for msg in conversation_history[-5:]:  # Last 5 messages
                role = msg.get('role', 'user')
                content = msg.get('content', '')
                history_text += f"{role.capitalize()}: {content}\n"
        
        # Build final prompt
        if context:
            prompt = f"""{system_prompt}

Context information:
{context}

{history_text}

User Question: {query}

Please provide a helpful and accurate response based on the context provided. If the context doesn't contain relevant information, you can provide a general response but mention that it's not from the provided sources."""
        else:
            prompt = f"""{system_prompt}

{history_text}

User Question: {query}

Please provide a helpful response. Note that I don't have specific context information for this query, so I'll provide a general answer based on my knowledge."""
        
        return prompt
    
    async def _update_conversation_cache(self,
                                       agent_id: str,
                                       message: ChatMessage,
                                       response: str,
                                       conversation_history: List[Dict[str, str]]):
        """Update conversation cache in Redis"""
        try:
            # Add new messages to history
            conversation_history.extend([
                {
                    'role': 'user',
                    'content': message.content,
                    'timestamp': message.timestamp.isoformat()
                },
                {
                    'role': 'assistant',
                    'content': response,
                    'timestamp': datetime.now().isoformat()
                }
            ])
            
            # Keep last 20 messages
            if len(conversation_history) > 20:
                conversation_history = conversation_history[-20:]
            
            # Store in Redis with 24-hour TTL
            key = f"conversation:{agent_id}:{message.conversation_id}"
            await self.redis_client.setex(
                key,
                24 * 3600,
                json.dumps(conversation_history)
            )
            
        except Exception as e:
            logger.warning(f"Failed to update conversation cache: {e}")
    
    async def get_conversation_history(self,
                                     agent_id: str,
                                     conversation_id: str) -> List[Dict[str, str]]:
        """Get conversation history from cache"""
        if not self.redis_client:
            return []
        
        try:
            key = f"conversation:{agent_id}:{conversation_id}"
            data = await self.redis_client.get(key)
            
            if data:
                return json.loads(data)
            
        except Exception as e:
            logger.warning(f"Failed to get conversation history: {e}")
        
        return []
    
    async def update_document_embeddings(self,
                                       agent_id: str,
                                       batch_size: int = 50) -> Dict[str, Any]:
        """
        Update embeddings for documents that don't have them
        
        Args:
            agent_id: Agent ID
            batch_size: Number of documents to process at once
        
        Returns:
            Update statistics
        """
        stats = {
            'total_documents': 0,
            'updated_documents': 0,
            'failed_documents': 0,
            'processing_time': 0.0
        }
        
        start_time = datetime.now()
        
        try:
            async for db in get_db():
                # Find documents without embeddings
                result = await db.execute(
                    select(KnowledgeDocument).where(
                        and_(
                            KnowledgeDocument.agent_id == agent_id,
                            KnowledgeDocument.embedding.is_(None)
                        )
                    )
                )
                documents = result.scalars().all()
                stats['total_documents'] = len(documents)
                
                # Process in batches
                for i in range(0, len(documents), batch_size):
                    batch = documents[i:i + batch_size]
                    texts = [doc.content for doc in batch]
                    
                    try:
                        # Generate embeddings
                        embeddings = await self.embedding_provider.embed_texts(texts)
                        
                        # Update documents
                        for doc, embedding in zip(batch, embeddings):
                            doc.embedding = embedding
                            stats['updated_documents'] += 1
                        
                        await db.commit()
                        
                    except Exception as e:
                        logger.error(f"Error updating batch: {e}")
                        stats['failed_documents'] += len(batch)
                        await db.rollback()
                
                break
                
        except Exception as e:
            logger.error(f"Error updating embeddings: {e}")
        
        stats['processing_time'] = (datetime.now() - start_time).total_seconds()
        return stats