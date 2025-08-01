"""
Multi-Embedding Provider Support for NETVEXA
Supports: Google, OpenAI, and local embeddings
"""

import logging
from abc import ABC, abstractmethod
from typing import List, Optional
import numpy as np
import asyncio

import google.generativeai as genai
from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from config import settings, EmbeddingProvider

logger = logging.getLogger(__name__)

class BaseEmbeddingProvider(ABC):
    """Abstract base class for embedding providers"""
    
    @abstractmethod
    async def embed_text(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        pass
    
    @abstractmethod
    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        pass
    
    @abstractmethod
    def get_embedding_dimension(self) -> int:
        """Get the dimension of the embedding vectors"""
        pass

class GoogleEmbeddingProvider(BaseEmbeddingProvider):
    """Google embedding provider using Generative AI embeddings"""
    
    def __init__(self, api_key: str, model: str = "models/embedding-001"):
        genai.configure(api_key=api_key)
        self.model = model
        
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    async def embed_text(self, text: str) -> List[float]:
        try:
            # Google's API is synchronous, run in executor
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: genai.embed_content(
                    model=self.model,
                    content=text,
                    task_type="retrieval_document"
                )
            )
            return result['embedding']
        except Exception as e:
            logger.error(f"Google embedding error: {e}")
            raise
    
    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Batch embed multiple texts"""
        embeddings = []
        
        # Google doesn't have a batch API, so we process in parallel
        tasks = [self.embed_text(text) for text in texts]
        embeddings = await asyncio.gather(*tasks)
        
        return embeddings
    
    def get_embedding_dimension(self) -> int:
        # Google's embedding-001 model produces 768-dimensional vectors
        return 768

class OpenAIEmbeddingProvider(BaseEmbeddingProvider):
    """OpenAI embedding provider"""
    
    def __init__(self, api_key: str, model: str = "text-embedding-ada-002"):
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model
        
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    async def embed_text(self, text: str) -> List[float]:
        try:
            response = await self.client.embeddings.create(
                model=self.model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"OpenAI embedding error: {e}")
            raise
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Batch embed multiple texts - OpenAI supports batch processing"""
        try:
            response = await self.client.embeddings.create(
                model=self.model,
                input=texts
            )
            return [data.embedding for data in response.data]
        except Exception as e:
            logger.error(f"OpenAI batch embedding error: {e}")
            raise
    
    def get_embedding_dimension(self) -> int:
        # Dimensions for different OpenAI models
        dimensions = {
            "text-embedding-ada-002": 1536,
            "text-embedding-3-small": 1536,
            "text-embedding-3-large": 3072,
        }
        return dimensions.get(self.model, 1536)

class LocalEmbeddingProvider(BaseEmbeddingProvider):
    """Local embedding provider using sentence transformers (fallback option)"""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(model_name)
            self.model_name = model_name
        except ImportError:
            logger.warning("sentence-transformers not installed. Local embeddings unavailable.")
            self.model = None
    
    async def embed_text(self, text: str) -> List[float]:
        if not self.model:
            raise RuntimeError("Local embedding model not available")
        
        # Run in executor since it's CPU-bound
        loop = asyncio.get_event_loop()
        embedding = await loop.run_in_executor(
            None,
            lambda: self.model.encode(text, convert_to_numpy=True)
        )
        return embedding.tolist()
    
    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        if not self.model:
            raise RuntimeError("Local embedding model not available")
        
        # Run in executor since it's CPU-bound
        loop = asyncio.get_event_loop()
        embeddings = await loop.run_in_executor(
            None,
            lambda: self.model.encode(texts, convert_to_numpy=True)
        )
        return embeddings.tolist()
    
    def get_embedding_dimension(self) -> int:
        dimensions = {
            "all-MiniLM-L6-v2": 384,
            "all-mpnet-base-v2": 768,
            "all-distilroberta-v1": 768,
        }
        return dimensions.get(self.model_name, 384)

class EmbeddingProviderFactory:
    """Factory class to create embedding providers"""
    
    @staticmethod
    def create_provider(
        provider_type: Optional[EmbeddingProvider] = None,
        api_key: Optional[str] = None,
        model: Optional[str] = None
    ) -> BaseEmbeddingProvider:
        """Create an embedding provider instance"""
        
        # Use settings if not provided
        if provider_type is None:
            provider_type = settings.EMBEDDING_PROVIDER
        
        if provider_type == EmbeddingProvider.GOOGLE:
            api_key = api_key or settings.GOOGLE_API_KEY
            model = model or settings.GOOGLE_EMBEDDING_MODEL
            if not api_key:
                raise ValueError("Google API key not provided")
            return GoogleEmbeddingProvider(api_key, model)
            
        elif provider_type == EmbeddingProvider.OPENAI:
            api_key = api_key or settings.OPENAI_API_KEY
            model = model or settings.OPENAI_EMBEDDING_MODEL
            if not api_key:
                raise ValueError("OpenAI API key not provided")
            return OpenAIEmbeddingProvider(api_key, model)
            
        else:
            raise ValueError(f"Unknown embedding provider type: {provider_type}")
    
    @staticmethod
    def get_available_providers() -> List[EmbeddingProvider]:
        """Get list of embedding providers that have API keys configured"""
        available = []
        
        if settings.GOOGLE_API_KEY:
            available.append(EmbeddingProvider.GOOGLE)
        if settings.OPENAI_API_KEY:
            available.append(EmbeddingProvider.OPENAI)
            
        return available

class CachedEmbeddingProvider:
    """Wrapper that provides caching for embeddings"""
    
    def __init__(self, provider: BaseEmbeddingProvider, cache_client=None):
        self.provider = provider
        self.cache_client = cache_client
        self.cache_ttl = 86400 * 7  # 7 days
    
    def _get_cache_key(self, text: str) -> str:
        """Generate cache key for text"""
        import hashlib
        text_hash = hashlib.md5(text.encode()).hexdigest()
        return f"embedding:{self.provider.__class__.__name__}:{text_hash}"
    
    async def embed_text(self, text: str) -> List[float]:
        """Embed text with caching"""
        if not self.cache_client or not settings.ENABLE_CACHE:
            return await self.provider.embed_text(text)
        
        # Try to get from cache
        cache_key = self._get_cache_key(text)
        try:
            cached = await self.cache_client.get(cache_key)
            if cached:
                import json
                return json.loads(cached)
        except Exception as e:
            logger.warning(f"Cache retrieval error: {e}")
        
        # Generate embedding
        embedding = await self.provider.embed_text(text)
        
        # Store in cache
        try:
            import json
            await self.cache_client.setex(
                cache_key,
                self.cache_ttl,
                json.dumps(embedding)
            )
        except Exception as e:
            logger.warning(f"Cache storage error: {e}")
        
        return embedding
    
    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Batch embed with caching"""
        if not self.cache_client or not settings.ENABLE_CACHE:
            return await self.provider.embed_texts(texts)
        
        # Check cache for each text
        embeddings = []
        uncached_texts = []
        uncached_indices = []
        
        for i, text in enumerate(texts):
            cache_key = self._get_cache_key(text)
            try:
                cached = await self.cache_client.get(cache_key)
                if cached:
                    import json
                    embeddings.append(json.loads(cached))
                else:
                    embeddings.append(None)
                    uncached_texts.append(text)
                    uncached_indices.append(i)
            except Exception as e:
                logger.warning(f"Cache retrieval error: {e}")
                embeddings.append(None)
                uncached_texts.append(text)
                uncached_indices.append(i)
        
        # Generate embeddings for uncached texts
        if uncached_texts:
            new_embeddings = await self.provider.embed_texts(uncached_texts)
            
            # Update results and cache
            for i, embedding in zip(uncached_indices, new_embeddings):
                embeddings[i] = embedding
                
                # Store in cache
                try:
                    import json
                    cache_key = self._get_cache_key(texts[i])
                    await self.cache_client.setex(
                        cache_key,
                        self.cache_ttl,
                        json.dumps(embedding)
                    )
                except Exception as e:
                    logger.warning(f"Cache storage error: {e}")
        
        return embeddings
    
    def get_embedding_dimension(self) -> int:
        return self.provider.get_embedding_dimension()