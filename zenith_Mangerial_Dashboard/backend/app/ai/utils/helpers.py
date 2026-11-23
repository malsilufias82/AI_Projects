import hashlib
import re
from typing import Any, Dict, List, Optional
from uuid import uuid4


def generate_chunk_id(artifact_id: str, index: int) -> str:
    """Generate a deterministic chunk ID from artifact ID and position."""
    return f"{artifact_id}_chunk_{index:06d}"


def generate_collection_name(artifact_id: str, prefix: str = "zenith") -> str:
    """Build a sanitized vector store collection name."""
    safe = re.sub(r"[^a-zA-Z0-9_\-]", "_", artifact_id)
    return f"{prefix}_{safe}"


def hash_text(text: str) -> str:
    """Return a stable SHA-256 hex digest for a text string."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def estimate_tokens(text: str, chars_per_token: int = 4) -> int:
    """
    Fast approximate token count for pre-flight budget checks.
    For precise counts use tiktoken.
    """
    return max(1, len(text) // chars_per_token)


def truncate_text(text: str, max_chars: int, suffix: str = "…") -> str:
    """Truncate text to max_chars, appending suffix if trimmed."""
    if len(text) <= max_chars:
        return text
    return text[: max_chars - len(suffix)] + suffix


def flatten_findings(evaluator_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Flatten findings from a list of evaluator result dicts."""
    return [f for r in evaluator_results for f in r.get("findings", [])]


def build_metadata(
    artifact_id: str,
    evaluator_id: Optional[str] = None,
    extra: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Construct a standardised metadata dict for vector store documents."""
    meta: Dict[str, Any] = {"artifact_id": artifact_id}
    if evaluator_id:
        meta["evaluator_id"] = evaluator_id
    if extra:
        meta.update(extra)
    return meta


def new_execution_id() -> str:
    """Generate a new UUID string for workflow/task execution IDs."""
    return str(uuid4())
