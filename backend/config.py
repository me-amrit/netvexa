from pydantic_settings import BaseSettings
from typing import Optional
from enum import Enum

class LLMProvider(str, Enum):
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    OPENAI = "openai"

class EmbeddingProvider(str, Enum):
    GOOGLE = "google"
    OPENAI = "openai"
    COHERE = "cohere"

class Settings(BaseSettings):
    # LLM Provider Configuration
    LLM_PROVIDER: LLMProvider = LLMProvider.ANTHROPIC
    
    # API Keys
    ANTHROPIC_API_KEY: Optional[str] = None
    GOOGLE_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://netvexa:netvexa_password@localhost:5432/netvexa_db"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # Security
    SECRET_KEY: str = "development-secret-key-change-in-production"
    JWT_SECRET_KEY: str = "jwt-development-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    ENVIRONMENT: str = "development"
    
    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:8080,http://localhost:8000"
    
    # LLM Model Configuration
    ANTHROPIC_MODEL: str = "claude-3-haiku-20240307"
    GOOGLE_MODEL: str = "gemini-pro"
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    
    # Embedding Configuration
    EMBEDDING_PROVIDER: EmbeddingProvider = EmbeddingProvider.GOOGLE
    GOOGLE_EMBEDDING_MODEL: str = "models/embedding-001"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-ada-002"
    
    # RAG Settings
    CHUNK_SIZE: int = 512
    CHUNK_OVERLAP: int = 50
    TOP_K_RETRIEVAL: int = 3
    
    # Feature Flags
    ENABLE_CACHE: bool = True
    ENABLE_FALLBACK: bool = True
    
    # Stripe Configuration
    STRIPE_API_KEY: Optional[str] = None
    STRIPE_WEBHOOK_SECRET: Optional[str] = None
    STRIPE_STARTER_PRICE_ID: Optional[str] = None
    STRIPE_GROWTH_PRICE_ID: Optional[str] = None
    STRIPE_PRO_PRICE_ID: Optional[str] = None
    STRIPE_BUSINESS_PRICE_ID: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra environment variables
    
    def validate_provider_keys(self) -> bool:
        """Validate that the selected provider has an API key"""
        if self.LLM_PROVIDER == LLMProvider.ANTHROPIC and not self.ANTHROPIC_API_KEY:
            return False
        elif self.LLM_PROVIDER == LLMProvider.GOOGLE and not self.GOOGLE_API_KEY:
            return False
        elif self.LLM_PROVIDER == LLMProvider.OPENAI and not self.OPENAI_API_KEY:
            return False
        return True
    
    def get_active_llm_model(self) -> str:
        """Get the model name for the active provider"""
        if self.LLM_PROVIDER == LLMProvider.ANTHROPIC:
            return self.ANTHROPIC_MODEL
        elif self.LLM_PROVIDER == LLMProvider.GOOGLE:
            return self.GOOGLE_MODEL
        else:
            return self.OPENAI_MODEL

settings = Settings()