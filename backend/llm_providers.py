"""
Multi-LLM Provider Support for NETVEXA
Supports: Anthropic (Claude), Google (Gemini), OpenAI (GPT)
"""

import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, AsyncGenerator
import asyncio

# Provider specific imports
import anthropic
import google.generativeai as genai
from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from config import settings, LLMProvider

logger = logging.getLogger(__name__)

class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
    @abstractmethod
    async def complete(self, prompt: str, **kwargs) -> str:
        """Generate a completion for the given prompt"""
        pass
    
    @abstractmethod
    async def stream_complete(self, prompt: str, **kwargs) -> AsyncGenerator[str, None]:
        """Stream a completion for the given prompt"""
        pass
    
    @abstractmethod
    def get_context_window(self) -> int:
        """Get the maximum context window size for the model"""
        pass

class AnthropicProvider(BaseLLMProvider):
    """Anthropic Claude provider"""
    
    def __init__(self, api_key: str, model: str):
        self.client = anthropic.AsyncAnthropic(api_key=api_key)
        self.model = model
        
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    async def complete(self, prompt: str, **kwargs) -> str:
        try:
            # Create the client method correctly
            message = await self.client.messages.create(
                model=self.model,
                max_tokens=kwargs.get('max_tokens', 1024),
                messages=[{
                    "role": "user",
                    "content": prompt
                }],
                temperature=kwargs.get('temperature', 0.7)
            )
            return message.content[0].text
        except Exception as e:
            logger.error(f"Anthropic completion error: {e}")
            raise
    
    async def stream_complete(self, prompt: str, **kwargs) -> AsyncGenerator[str, None]:
        try:
            stream = await self.client.messages.create(
                model=self.model,
                max_tokens=kwargs.get('max_tokens', 1024),
                messages=[{
                    "role": "user",
                    "content": prompt
                }],
                temperature=kwargs.get('temperature', 0.7),
                stream=True
            )
            
            async for chunk in stream:
                if chunk.type == 'content_block_delta':
                    yield chunk.delta.text
                    
        except Exception as e:
            logger.error(f"Anthropic streaming error: {e}")
            raise
    
    def get_context_window(self) -> int:
        # Context windows for different Claude models
        context_windows = {
            "claude-3-opus-20240229": 200000,
            "claude-3-sonnet-20240229": 200000,
            "claude-3-haiku-20240307": 200000,
            "claude-2.1": 200000,
            "claude-2.0": 100000,
        }
        return context_windows.get(self.model, 100000)

class GoogleProvider(BaseLLMProvider):
    """Google Gemini provider"""
    
    def __init__(self, api_key: str, model: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model)
        self.model_name = model
        
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    async def complete(self, prompt: str, **kwargs) -> str:
        try:
            # Google's API is synchronous, so we run it in an executor
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        max_output_tokens=kwargs.get('max_tokens', 1024),
                        temperature=kwargs.get('temperature', 0.7),
                    )
                )
            )
            return response.text
        except Exception as e:
            logger.error(f"Google completion error: {e}")
            raise
    
    async def stream_complete(self, prompt: str, **kwargs) -> AsyncGenerator[str, None]:
        try:
            # Google's streaming is synchronous, so we handle it differently
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        max_output_tokens=kwargs.get('max_tokens', 1024),
                        temperature=kwargs.get('temperature', 0.7),
                    ),
                    stream=True
                )
            )
            
            for chunk in response:
                if chunk.text:
                    yield chunk.text
                    
        except Exception as e:
            logger.error(f"Google streaming error: {e}")
            raise
    
    def get_context_window(self) -> int:
        # Context windows for Gemini models
        context_windows = {
            "gemini-1.5-flash": 1048576,  # 1M tokens
            "gemini-1.5-pro": 1048576,  # 1M tokens
            "gemini-pro": 32768,
            "gemini-pro-vision": 16384,
        }
        return context_windows.get(self.model_name, 32768)

class OpenAIProvider(BaseLLMProvider):
    """OpenAI GPT provider"""
    
    def __init__(self, api_key: str, model: str):
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model
        
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    async def complete(self, prompt: str, **kwargs) -> str:
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{
                    "role": "user",
                    "content": prompt
                }],
                max_tokens=kwargs.get('max_tokens', 1024),
                temperature=kwargs.get('temperature', 0.7)
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI completion error: {e}")
            raise
    
    async def stream_complete(self, prompt: str, **kwargs) -> AsyncGenerator[str, None]:
        try:
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=[{
                    "role": "user",
                    "content": prompt
                }],
                max_tokens=kwargs.get('max_tokens', 1024),
                temperature=kwargs.get('temperature', 0.7),
                stream=True
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            logger.error(f"OpenAI streaming error: {e}")
            raise
    
    def get_context_window(self) -> int:
        # Context windows for OpenAI models
        context_windows = {
            "gpt-4": 8192,
            "gpt-4-32k": 32768,
            "gpt-4-turbo-preview": 128000,
            "gpt-3.5-turbo": 16384,
            "gpt-3.5-turbo-16k": 16384,
        }
        return context_windows.get(self.model, 4096)

class LLMProviderFactory:
    """Factory class to create LLM providers"""
    
    @staticmethod
    def create_provider(
        provider_type: Optional[LLMProvider] = None,
        api_key: Optional[str] = None,
        model: Optional[str] = None
    ) -> BaseLLMProvider:
        """Create an LLM provider instance"""
        
        # Use settings if not provided
        if provider_type is None:
            provider_type = settings.LLM_PROVIDER
        
        # Get the appropriate API key and model
        if provider_type == LLMProvider.ANTHROPIC:
            api_key = api_key or settings.ANTHROPIC_API_KEY
            model = model or settings.ANTHROPIC_MODEL
            if not api_key:
                raise ValueError("Anthropic API key not provided")
            return AnthropicProvider(api_key, model)
            
        elif provider_type == LLMProvider.GOOGLE:
            api_key = api_key or settings.GOOGLE_API_KEY
            model = model or settings.GOOGLE_MODEL
            if not api_key:
                raise ValueError("Google API key not provided")
            return GoogleProvider(api_key, model)
            
        elif provider_type == LLMProvider.OPENAI:
            api_key = api_key or settings.OPENAI_API_KEY
            model = model or settings.OPENAI_MODEL
            if not api_key:
                raise ValueError("OpenAI API key not provided")
            return OpenAIProvider(api_key, model)
            
        elif provider_type == LLMProvider.MOCK:
            from test_llm_provider import MockLLMProvider
            return MockLLMProvider()
            
        else:
            raise ValueError(f"Unknown provider type: {provider_type}")
    
    @staticmethod
    def get_available_providers() -> List[LLMProvider]:
        """Get list of providers that have API keys configured"""
        available = []
        
        if settings.ANTHROPIC_API_KEY:
            available.append(LLMProvider.ANTHROPIC)
        if settings.GOOGLE_API_KEY:
            available.append(LLMProvider.GOOGLE)
        if settings.OPENAI_API_KEY:
            available.append(LLMProvider.OPENAI)
        # Mock provider is always available
        available.append(LLMProvider.MOCK)
            
        return available

class LLMProviderWithFallback:
    """Wrapper that provides automatic fallback between providers"""
    
    def __init__(self):
        self.primary_provider = None
        self.fallback_providers = []
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize primary and fallback providers"""
        available = LLMProviderFactory.get_available_providers()
        
        if not available:
            raise ValueError("No LLM providers configured. Please provide at least one API key.")
        
        # Set primary provider
        if settings.LLM_PROVIDER in available:
            self.primary_provider = LLMProviderFactory.create_provider(settings.LLM_PROVIDER)
        else:
            # Use first available as primary
            self.primary_provider = LLMProviderFactory.create_provider(available[0])
            logger.warning(f"Configured provider {settings.LLM_PROVIDER} not available. Using {available[0]}")
        
        # Set fallback providers
        for provider in available:
            if provider != settings.LLM_PROVIDER:
                try:
                    fallback = LLMProviderFactory.create_provider(provider)
                    self.fallback_providers.append(fallback)
                except Exception as e:
                    logger.error(f"Failed to initialize fallback provider {provider}: {e}")
    
    async def complete(self, prompt: str, **kwargs) -> str:
        """Complete with automatic fallback"""
        # Try primary provider
        try:
            return await self.primary_provider.complete(prompt, **kwargs)
        except Exception as e:
            logger.error(f"Primary provider failed: {e}")
            
            if not settings.ENABLE_FALLBACK:
                raise
            
            # Try fallback providers
            for provider in self.fallback_providers:
                try:
                    logger.info(f"Attempting fallback to {provider.__class__.__name__}")
                    return await provider.complete(prompt, **kwargs)
                except Exception as fallback_error:
                    logger.error(f"Fallback provider failed: {fallback_error}")
                    continue
            
            # All providers failed
            raise Exception("All LLM providers failed")
    
    async def stream_complete(self, prompt: str, **kwargs) -> AsyncGenerator[str, None]:
        """Stream complete with automatic fallback"""
        # For streaming, we don't do fallback mid-stream
        try:
            async for chunk in self.primary_provider.stream_complete(prompt, **kwargs):
                yield chunk
        except Exception as e:
            logger.error(f"Primary provider streaming failed: {e}")
            raise