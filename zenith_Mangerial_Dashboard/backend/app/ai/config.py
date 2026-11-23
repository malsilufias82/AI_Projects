from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AISettings(BaseSettings):
    """Centralized AI configuration loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # ─── LLM ─────────────────────────────────────────────────────────────────
    LLM_PROVIDER: str = "openai"
    LLM_MODEL: str = "gpt-4o"
    LLM_TEMPERATURE: float = 0.0
    LLM_MAX_TOKENS: int = 4096
    LLM_TIMEOUT_SECONDS: int = 60
    LLM_MAX_RETRIES: int = 3

    OPENAI_API_KEY: Optional[str] = None
    OPENAI_API_BASE: Optional[str] = None

    AZURE_OPENAI_API_KEY: Optional[str] = None
    AZURE_OPENAI_ENDPOINT: Optional[str] = None
    AZURE_OPENAI_DEPLOYMENT: Optional[str] = None
    AZURE_OPENAI_API_VERSION: str = "2024-02-01"

    # ─── Embeddings ──────────────────────────────────────────────────────────
    EMBEDDING_PROVIDER: str = "openai"
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    EMBEDDING_DIMENSION: int = 1536
    EMBEDDING_BATCH_SIZE: int = 100

    # ─── Vector DB ───────────────────────────────────────────────────────────
    VECTOR_DB_PROVIDER: str = "chroma"
    CHROMA_HOST: str = "localhost"
    CHROMA_PORT: int = 8001
    CHROMA_COLLECTION_PREFIX: str = "zenith"

    # ─── Chunking ────────────────────────────────────────────────────────────
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    CHUNK_MIN_SIZE: int = 100
    CHUNK_STRATEGY: str = "semantic"

    # ─── AI Job ──────────────────────────────────────────────────────────────
    AI_JOB_MAX_RETRIES: int = 3
    AI_JOB_RETRY_DELAY_SECONDS: int = 60
    AI_JOB_TIMEOUT_SECONDS: int = 3600
    AI_JOB_PROGRESS_INTERVAL_SECONDS: int = 5

    # ─── Celery AI Queues ────────────────────────────────────────────────────
    AI_EVALUATION_QUEUE: str = "ai.evaluation"
    AI_EMBEDDING_QUEUE: str = "ai.embedding"
    AI_INGESTION_QUEUE: str = "ai.ingestion"
    AI_ORCHESTRATION_QUEUE: str = "ai.orchestration"

    # ─── Context & Retrieval ─────────────────────────────────────────────────
    MAX_CONTEXT_TOKENS: int = 8192
    RETRIEVAL_TOP_K: int = 10
    RETRIEVAL_SCORE_THRESHOLD: float = 0.7


ai_settings = AISettings()
