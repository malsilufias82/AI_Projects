import hashlib
import secrets
import string
from datetime import datetime, timezone
from typing import Any, Optional


def generate_random_string(length: int = 32) -> str:
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def hash_string(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


def sanitize_dict(
    data: dict[str, Any],
    exclude_keys: Optional[list[str]] = None,
) -> dict[str, Any]:
    if exclude_keys is None:
        exclude_keys = ["password", "hashed_password", "secret", "token"]
    return {k: v for k, v in data.items() if k not in exclude_keys}


def chunk_list(items: list[Any], chunk_size: int) -> list[list[Any]]:
    return [items[i : i + chunk_size] for i in range(0, len(items), chunk_size)]
