from typing import Any, AsyncIterator, List, Type

from pydantic import BaseModel

from app.ai.providers.llm.base import BaseLLMProvider, LLMMessage, LLMResponse
from app.ai.registry.provider_registry import ProviderType, register_provider
from app.core.logging import get_logger

logger = get_logger(__name__)


@register_provider(ProviderType.LLM, "openai")
class OpenAIProvider(BaseLLMProvider):
    """
    OpenAI-compatible LLM provider placeholder.
    Supports GPT-4o and any OpenAI-compatible API endpoint.
    """

    provider_id: str = "openai"

    def __init__(self, model: str = "gpt-4o", temperature: float = 0.0, max_tokens: int = 4096, **kwargs: Any) -> None:
        super().__init__(model=model, temperature=temperature, max_tokens=max_tokens, **kwargs)
        self._client = None

    def _get_client(self) -> Any:
        """Lazily initialise the OpenAI async client."""
        if self._client is None:
            from openai import AsyncOpenAI
            from app.ai.config import ai_settings

            self._client = AsyncOpenAI(
                api_key=ai_settings.OPENAI_API_KEY,
                base_url=ai_settings.OPENAI_API_BASE,
            )
        return self._client

    async def generate(self, messages: List[LLMMessage], **kwargs: Any) -> LLMResponse:
        """Generate a completion using the OpenAI chat endpoint."""
        client = self._get_client()
        payload = [{"role": m.role, "content": m.content} for m in messages]
        response = await client.chat.completions.create(
            model=self.model,
            messages=payload,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            **kwargs,
        )
        choice = response.choices[0]
        return LLMResponse(
            content=choice.message.content or "",
            model=response.model,
            prompt_tokens=response.usage.prompt_tokens if response.usage else 0,
            completion_tokens=response.usage.completion_tokens if response.usage else 0,
            finish_reason=choice.finish_reason,
        )

    async def generate_structured(
        self,
        messages: List[LLMMessage],
        response_schema: Type[BaseModel],
        **kwargs: Any,
    ) -> BaseModel:
        """Generate a JSON-mode response and parse it into response_schema."""
        client = self._get_client()
        payload = [{"role": m.role, "content": m.content} for m in messages]
        response = await client.chat.completions.create(
            model=self.model,
            messages=payload,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            response_format={"type": "json_object"},
            **kwargs,
        )
        raw_content = response.choices[0].message.content or "{}"
        return response_schema.model_validate_json(raw_content)

    async def stream(self, messages: List[LLMMessage], **kwargs: Any) -> AsyncIterator[str]:
        """Stream tokens from the OpenAI chat endpoint."""
        client = self._get_client()
        payload = [{"role": m.role, "content": m.content} for m in messages]
        async with await client.chat.completions.create(
            model=self.model,
            messages=payload,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            stream=True,
            **kwargs,
        ) as stream:
            async for chunk in stream:
                delta = chunk.choices[0].delta.content
                if delta:
                    yield delta

    async def health_check(self) -> bool:
        """Verify OpenAI API connectivity."""
        try:
            client = self._get_client()
            await client.models.list()
            return True
        except Exception as exc:
            logger.warning("openai_health_check_failed", error=str(exc))
            return False
