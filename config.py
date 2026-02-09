"""Centralized project configurations."""

import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv

load_dotenv()


@dataclass
class AzureOpenAIConfig:
    """Azure OpenAI configuration."""
    
    endpoint: str
    api_key: str
    deployment: str
    api_version: str = "2023-05-15"
    
    @classmethod
    def from_env(cls) -> "AzureOpenAIConfig":
        """Loads configuration from environment variables."""
        return cls(
            endpoint=os.getenv("AZURE_API_BASE", ""),
            api_key=os.getenv("AZURE_API_KEY", ""),
            deployment=os.getenv("AZURE_DEPLOYMENT", "gpt-4o"),
            api_version=os.getenv("AZURE_API_VERSION", "2023-05-15"),
        )
    
    def validate(self) -> None:
        """Validates that all required configurations are present."""
        if not self.endpoint:
            raise ValueError("AZURE_API_BASE not configured")
        if not self.api_key:
            raise ValueError("AZURE_API_KEY not configured")
        if not self.deployment:
            raise ValueError("AZURE_DEPLOYMENT not configured")


@dataclass
class AzureEmbeddingsConfig:
    """Configuration for Azure OpenAI Embeddings."""
    
    endpoint: str
    api_key: str
    deployment: str
    api_version: str = "2024-02-01"
    
    @classmethod
    def from_env(cls) -> "AzureEmbeddingsConfig":
        """Loads configuration from environment variables."""
        return cls(
            endpoint=os.getenv("AZURE_EMBEDDINGS_ENDPOINT", ""),
            api_key=os.getenv("AZURE_EMBEDDINGS_API_KEY", ""),
            deployment=os.getenv("AZURE_EMBEDDINGS_DEPLOYMENT", "text-embedding-3-large"),
            api_version=os.getenv("AZURE_EMBEDDINGS_API_VERSION", "2024-02-01"),
        )
    
    def validate(self) -> None:
        """Validates that all required configurations are present."""
        if not self.endpoint:
            raise ValueError("AZURE_EMBEDDINGS_ENDPOINT not configured")
        if not self.api_key:
            raise ValueError("AZURE_EMBEDDINGS_API_KEY not configured")


@dataclass
class TemporalConfig:
    """Temporal configuration."""
    
    address: str = "localhost:7233"
    namespace: str = "default"
    task_queue: str = "agent-mcp-queue"
    
    @classmethod
    def from_env(cls) -> "TemporalConfig":
        """Loads configuration from environment variables."""
        return cls(
            address=os.getenv("TEMPORAL_ADDRESS", "localhost:7233"),
            namespace=os.getenv("TEMPORAL_NAMESPACE", "default"),
            task_queue=os.getenv("TEMPORAL_TASK_QUEUE", "agent-mcp-queue"),
        )


@dataclass
class SearchConfig:
    """Search index configuration."""
    
    filename: str = "database/search_index.json"
    
    @classmethod
    def from_env(cls) -> "SearchConfig":
        """Loads configuration from environment variables."""
        return cls(
            filename=os.getenv("SEARCH_FILENAME", "database/search_index.json"),
        )


@dataclass
class APIConfig:
    """API configuration."""
    
    port: int = 8000
    host: str = "0.0.0.0"
    base_url: str = "http://localhost:8000"
    
    @classmethod
    def from_env(cls) -> "APIConfig":
        """Loads configuration from environment variables."""
        return cls(
            port=int(os.getenv("PORT", "8000")),
            host=os.getenv("HOST", "0.0.0.0"),
            base_url=os.getenv("API_BASE_URL", "http://localhost:8000"),
        )


class Config:
    """Global application configuration."""
    
    def __init__(self):
        self.azure_openai = AzureOpenAIConfig.from_env()
        self.azure_embeddings = AzureEmbeddingsConfig.from_env()
        self.temporal = TemporalConfig.from_env()
        self.search = SearchConfig.from_env()
        self.api = APIConfig.from_env()
    
    def validate(self) -> None:
        """Validates all configurations."""
        self.azure_openai.validate()
        self.azure_embeddings.validate()


# Global configuration instance
config = Config()
