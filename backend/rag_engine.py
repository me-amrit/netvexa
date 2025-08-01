import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import asyncio
import uuid
import redis.asyncio as redis
from pydantic import Field

from llama_index import (
    Document,
    VectorStoreIndex,
    ServiceContext,
    StorageContext,
    SimpleDirectoryReader
)
from llama_index.llms import LangChainLLM
from llama_index.embeddings import LangchainEmbedding
from langchain.llms.base import LLM
from langchain.embeddings.base import Embeddings

from config import settings
from models import ChatMessage, ChatResponse, KnowledgeDocument
from llm_providers import LLMProviderFactory, LLMProviderWithFallback
from embedding_providers import EmbeddingProviderFactory, CachedEmbeddingProvider
from vector_store import PgVectorStore

logger = logging.getLogger(__name__)

class CustomLLM(LLM):
    """Custom LangChain LLM wrapper for our providers"""
    
    provider: Any = None
    
    def __init__(self, provider, **kwargs):
        super().__init__(**kwargs)
        object.__setattr__(self, 'provider', provider)
    
    @property
    def _llm_type(self) -> str:
        return "custom"
    
    def _call(self, prompt: str, stop: Optional[List[str]] = None, **kwargs) -> str:
        """Synchronous wrapper for async completion"""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # We're in an async context, use threading
                import concurrent.futures
                import threading
                future = concurrent.futures.Future()
                
                def run_in_thread():
                    new_loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(new_loop)
                    try:
                        result = new_loop.run_until_complete(self.provider.complete(prompt, **kwargs))
                        future.set_result(result)
                    except Exception as e:
                        future.set_exception(e)
                    finally:
                        new_loop.close()
                
                thread = threading.Thread(target=run_in_thread)
                thread.start()
                thread.join()
                return future.result()
            else:
                return loop.run_until_complete(self.provider.complete(prompt, **kwargs))
        except RuntimeError:
            # No event loop, create one
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(self.provider.complete(prompt, **kwargs))
            finally:
                loop.close()
    
    async def _acall(self, prompt: str, stop: Optional[List[str]] = None, **kwargs) -> str:
        """Async completion"""
        return await self.provider.complete(prompt, **kwargs)

class CustomEmbeddings(Embeddings):
    """Custom LangChain Embeddings wrapper for our providers"""
    
    provider: Any = None
    
    def __init__(self, provider, **kwargs):
        super().__init__(**kwargs)
        object.__setattr__(self, 'provider', provider)
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Synchronous wrapper for async embeddings"""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # We're in an async context, use run_coroutine_threadsafe
                import concurrent.futures
                import threading
                future = concurrent.futures.Future()
                
                def run_in_thread():
                    new_loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(new_loop)
                    try:
                        result = new_loop.run_until_complete(self.provider.embed_texts(texts))
                        future.set_result(result)
                    except Exception as e:
                        future.set_exception(e)
                    finally:
                        new_loop.close()
                
                thread = threading.Thread(target=run_in_thread)
                thread.start()
                thread.join()
                return future.result()
            else:
                return loop.run_until_complete(self.provider.embed_texts(texts))
        except RuntimeError:
            # No event loop, create one
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(self.provider.embed_texts(texts))
            finally:
                loop.close()
    
    def embed_query(self, text: str) -> List[float]:
        """Synchronous wrapper for single embedding"""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # We're in an async context, use threading
                import concurrent.futures
                import threading
                future = concurrent.futures.Future()
                
                def run_in_thread():
                    new_loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(new_loop)
                    try:
                        result = new_loop.run_until_complete(self.provider.embed_text(text))
                        future.set_result(result)
                    except Exception as e:
                        future.set_exception(e)
                    finally:
                        new_loop.close()
                
                thread = threading.Thread(target=run_in_thread)
                thread.start()
                thread.join()
                return future.result()
            else:
                return loop.run_until_complete(self.provider.embed_text(text))
        except RuntimeError:
            # No event loop, create one
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(self.provider.embed_text(text))
            finally:
                loop.close()
    
    async def aembed_documents(self, texts: List[str]) -> List[List[float]]:
        """Async batch embeddings"""
        return await self.provider.embed_texts(texts)
    
    async def aembed_query(self, text: str) -> List[float]:
        """Async single embedding"""
        return await self.provider.embed_text(text)

class RAGEngine:
    def __init__(self):
        """Initialize the RAG engine with configurable LLM and embedding providers"""
        # Initialize Redis client if available
        self.redis_client = None
        if settings.REDIS_URL:
            try:
                self.redis_client = redis.from_url(settings.REDIS_URL)
                logger.info("Redis client initialized for caching")
            except Exception as e:
                logger.warning(f"Failed to initialize Redis: {e}")
        
        # Initialize LLM provider with fallback
        self.llm_provider = LLMProviderWithFallback()
        self.llm = LangChainLLM(llm=CustomLLM(self.llm_provider))
        
        # Initialize embedding provider with caching
        embedding_provider = EmbeddingProviderFactory.create_provider()
        if self.redis_client:
            self.embedding_provider = CachedEmbeddingProvider(
                embedding_provider,
                self.redis_client
            )
        else:
            self.embedding_provider = embedding_provider
        
        self.embeddings = LangchainEmbedding(
            langchain_embeddings=CustomEmbeddings(self.embedding_provider)
        )
        
        # Initialize service context
        self.service_context = ServiceContext.from_defaults(
            llm=self.llm,
            embed_model=self.embeddings,
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP
        )
        
        # Initialize PostgreSQL vector store
        self.vector_store = PgVectorStore(
            embedding_provider=self.embedding_provider,
            embedding_dim=self.embedding_provider.get_embedding_dimension()
        )
        
        logger.info(f"RAG Engine initialized with {settings.LLM_PROVIDER} LLM and {settings.EMBEDDING_PROVIDER} embeddings using PostgreSQL vector store")
    
    async def _chunk_text(self, text: str, chunk_size: int = None, chunk_overlap: int = None) -> List[str]:
        """Chunk text into smaller pieces"""
        chunk_size = chunk_size or settings.CHUNK_SIZE
        chunk_overlap = chunk_overlap or settings.CHUNK_OVERLAP
        
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            end = start + chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            start = end - chunk_overlap
            
        return chunks
    
    async def ingest_text(self, text: str, metadata: Optional[Dict] = None) -> Dict:
        """Ingest raw text into the knowledge base"""
        try:
            # For MVP, use a default agent
            agent_id = "default_agent"
            
            # Chunk the text if it's too long
            chunks = await self._chunk_text(text)
            
            # Create documents from chunks
            documents = []
            for i, chunk in enumerate(chunks):
                doc_metadata = metadata or {}
                doc_metadata['chunk_index'] = i
                doc_metadata['total_chunks'] = len(chunks)
                
                documents.append({
                    'id': str(uuid.uuid4()),
                    'content': chunk,
                    'title': doc_metadata.get('title', f'Document chunk {i+1}'),
                    'metadata': doc_metadata,
                    'url': doc_metadata.get('url')
                })
            
            # Add documents to vector store
            doc_ids = await self.vector_store.add_documents(agent_id, documents)
            
            logger.info(f"Successfully ingested {len(documents)} document chunks for agent {agent_id}")
            
            return {
                "status": "success",
                "documents_created": len(documents),
                "document_ids": doc_ids,
                "agent_id": agent_id
            }
            
        except Exception as e:
            logger.error(f"Error ingesting text: {e}")
            raise
    
    async def ingest_url(self, url: str) -> Dict:
        """Ingest content from URL (simplified for MVP)"""
        try:
            # For MVP, create a simple job ID
            job_id = str(uuid.uuid4())
            
            # In a real implementation, this would:
            # 1. Crawl the URL
            # 2. Extract text content
            # 3. Process and chunk the content
            # 4. Create embeddings
            # 5. Store in vector database
            
            # For now, return a job ID
            logger.info(f"URL ingestion job created: {job_id}")
            
            return {
                "job_id": job_id,
                "status": "processing"
            }
            
        except Exception as e:
            logger.error(f"Error creating ingestion job: {e}")
            raise
    
    async def process_message(self, agent_id: str, message: ChatMessage) -> ChatResponse:
        """Process a chat message and generate response using RAG"""
        try:
            # Search for relevant documents
            similar_docs = await self.vector_store.similarity_search(
                agent_id=agent_id,
                query=message.content,
                k=settings.TOP_K_RETRIEVAL,
                threshold=0.5  # Adjust threshold as needed
            )
            
            # Build context from retrieved documents
            context = ""
            source_count = 0
            if similar_docs:
                context = "Relevant information from knowledge base:\n\n"
                for doc, similarity in similar_docs:
                    context += f"- {doc.content}\n\n"
                    source_count += 1
                logger.info(f"Found {source_count} relevant documents")
            else:
                logger.info("No relevant documents found in knowledge base")
            
            # Build context-aware prompt
            prompt = self._build_prompt_with_context(message.content, context)
            
            # Generate response using LLM
            response_text = await self.llm_provider.complete(prompt)
            
            # Store conversation in Redis if available
            if self.redis_client:
                await self._store_conversation(agent_id, message, response_text)
            
            # Create response
            chat_response = ChatResponse(
                content=response_text,
                timestamp=datetime.now(),
                metadata={
                    "agent_id": agent_id,
                    "source_documents": source_count,
                    "llm_provider": settings.LLM_PROVIDER,
                    "embedding_provider": settings.EMBEDDING_PROVIDER
                }
            )
            
            return chat_response
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            # Return a fallback response
            return ChatResponse(
                content="I apologize, but I'm having trouble processing your request. Please try again.",
                timestamp=datetime.now(),
                metadata={"error": str(e)}
            )
    
    async def _store_conversation(self, agent_id: str, message: ChatMessage, response: str):
        """Store conversation in Redis for context"""
        try:
            key = f"conversation:{agent_id}:{message.conversation_id}"
            
            # Get existing conversation
            existing = await self.redis_client.get(key)
            if existing:
                import json
                conversation = json.loads(existing)
            else:
                conversation = {"messages": []}
            
            # Add new messages
            conversation["messages"].extend([
                {
                    "role": "user",
                    "content": message.content,
                    "timestamp": message.timestamp.isoformat()
                },
                {
                    "role": "assistant",
                    "content": response,
                    "timestamp": datetime.now().isoformat()
                }
            ])
            
            # Store back in Redis with 24 hour TTL
            import json
            await self.redis_client.setex(
                key,
                86400,
                json.dumps(conversation)
            )
        except Exception as e:
            logger.warning(f"Failed to store conversation: {e}")
    
    def _build_prompt_with_context(self, user_message: str, context: str) -> str:
        """Build a context-aware prompt for the LLM"""
        if context:
            return f"""You are NETVEXA, an AI business assistant. Your role is to help website visitors 
understand products and services, answer questions, and qualify leads.

{context}

User Question: {user_message}

Please provide a helpful, accurate, and professional response based on the information provided above. 
If the information doesn't fully answer the question, acknowledge what you know and offer to help 
further or connect the user with a human representative."""
        else:
            return f"""You are NETVEXA, an AI business assistant. Your role is to help website visitors 
understand products and services, answer questions, and qualify leads.

User Question: {user_message}

Please provide a helpful, accurate, and professional response. Since I don't have specific information 
about this in my knowledge base, I'll provide a general but helpful response and offer to connect 
you with a human representative if needed."""