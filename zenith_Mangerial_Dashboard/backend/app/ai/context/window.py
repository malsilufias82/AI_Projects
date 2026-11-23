from typing import List, Optional

from app.ai.context.models import ChunkReference
from app.core.logging import get_logger

logger = get_logger(__name__)


class ContextWindow:
    """
    Manages a token-budget-aware context window for LLM input construction.

    Chunks are added in descending relevance order and dropped once the
    token budget is exhausted.
    """

    def __init__(self, max_tokens: int = 8192, token_estimator=None) -> None:
        self.max_tokens = max_tokens
        self._chunks: List[ChunkReference] = []
        self._used_tokens: int = 0
        self._token_estimator = token_estimator or self._default_estimate

    @staticmethod
    def _default_estimate(text: str) -> int:
        """Rough token estimate: 1 token ≈ 4 characters."""
        return max(1, len(text) // 4)

    def try_add(self, chunk: ChunkReference) -> bool:
        """
        Attempt to add a chunk to the window.
        Returns True if accepted, False if the budget would be exceeded.
        """
        tokens = self._token_estimator(chunk.content)
        if self._used_tokens + tokens > self.max_tokens:
            logger.debug(
                "context_window_budget_exceeded",
                used=self._used_tokens,
                attempted=tokens,
                max=self.max_tokens,
            )
            return False
        self._chunks.append(chunk)
        self._used_tokens += tokens
        return True

    def get_chunks(self) -> List[ChunkReference]:
        return list(self._chunks)

    def get_text(self, separator: str = "\n\n") -> str:
        """Return concatenated chunk content."""
        return separator.join(c.content for c in self._chunks)

    @property
    def used_tokens(self) -> int:
        return self._used_tokens

    @property
    def remaining_tokens(self) -> int:
        return self.max_tokens - self._used_tokens

    @property
    def is_full(self) -> bool:
        return self._used_tokens >= self.max_tokens

    def clear(self) -> None:
        self._chunks.clear()
        self._used_tokens = 0

    def __len__(self) -> int:
        return len(self._chunks)
