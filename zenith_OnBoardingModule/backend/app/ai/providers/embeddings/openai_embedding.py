from typing import Any, List

from app.ai.providers.embeddings.base import BaseEmbeddingProvider, EmbeddingResponse
from app.ai.registry.provider_registry import ProviderType, register_provider
from app.core.logging import get_logger

logger = get_logger(__name__)


@register_provider(ProviderType.EMBEDDING, "openai")
class OpenAIEmbeddingProvider(BaseEmbeddingProvider):
    """
    OpenAI embedding provider placeholder.
    Supports text-embedding-3-small / text-embedding-3-large.
    """

    provider_id: str = "openai"

    def __init__(
        self,
        model: str = "text-embedding-3-small",
        dimension: int = 1536,
        batch_size: int = 100,
        **kwargs: Any,
    ) -> None:
        super().__init__(model=model, dimension=dimension, batch_size=batch_size, **kwargs)
        self._client = None

    def _get_client(self) -> Any:
        if self._client is None:
            from openai import AsyncOpenAI
            from app.ai.config import ai_settings

            self._client = AsyncOpenAI(api_key=ai_settings.OPENAI_API_KEY)
        return self._client

    async def embed_text(self, text: str, **kwargs: Any) -> EmbeddingResponse:
        """Embed a single text string."""
        client = self._get_client()
        response = await client.embeddings.create(
            input=[text],
            model=self.model,
            **kwargs,
        )
        data = response.data[0]
        return EmbeddingResponse(
            vector=data.embedding,
            model=response.model,
            tokens=response.usage.total_tokens if response.usage else 0,
        )

    async def embed_batch(self, texts: List[str], **kwargs: Any) -> List[EmbeddingResponse]:
        """Embed texts in batches respecting self.batch_size."""
        client = self._get_client()
        results: List[EmbeddingResponse] = []
        for i in range(0, len(texts), self.batch_size):
            batch = texts[i : i + self.batch_size]
            response = await client.embeddings.create(input=batch, model=self.model, **kwargs)
            for item in response.data:
                results.append(
                    EmbeddingResponse(
                        vector=item.embedding,
                        model=response.model,
                        tokens=response.usage.total_tokens if response.usage else 0,
                    )
                )
        return results

    async def health_check(self) -> bool:
        try:
            await self.embed_text("ping")
            return True
        except Exception as exc:
            logger.warning("openai_embedding_health_check_failed", error=str(exc))
            return False
