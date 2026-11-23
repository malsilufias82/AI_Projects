from enum import Enum
from typing import Dict, List, Optional, Type

from app.core.logging import get_logger

logger = get_logger(__name__)


class ProviderType(str, Enum):
    LLM = "llm"
    EMBEDDING = "embedding"
    VECTOR_DB = "vector_db"


class ProviderRegistry:
    """
    Central registry for all provider classes (LLM, embedding, vector DB).
    Supports per-type namespaced registration.
    """

    _registry: Dict[ProviderType, Dict[str, Type]] = {
        ProviderType.LLM: {},
        ProviderType.EMBEDDING: {},
        ProviderType.VECTOR_DB: {},
    }

    @classmethod
    def register(cls, provider_type: ProviderType, provider_id: str, provider_class: Type) -> None:
        cls._registry[provider_type][provider_id] = provider_class
        logger.info("provider_registered", provider_type=provider_type, provider_id=provider_id)

    @classmethod
    def get(cls, provider_type: ProviderType, provider_id: str) -> Optional[Type]:
        return cls._registry.get(provider_type, {}).get(provider_id)

    @classmethod
    def get_or_raise(cls, provider_type: ProviderType, provider_id: str) -> Type:
        provider = cls.get(provider_type, provider_id)
        if provider is None:
            raise KeyError(f"Provider '{provider_id}' of type '{provider_type}' is not registered.")
        return provider

    @classmethod
    def list_registered(cls, provider_type: ProviderType) -> List[str]:
        return list(cls._registry.get(provider_type, {}).keys())

    @classmethod
    def clear(cls) -> None:
        for key in cls._registry:
            cls._registry[key].clear()


def register_provider(provider_type: ProviderType, provider_id: str):
    """Class decorator for automatic provider registration."""

    def decorator(cls: Type) -> Type:
        ProviderRegistry.register(provider_type, provider_id, cls)
        return cls

    return decorator
