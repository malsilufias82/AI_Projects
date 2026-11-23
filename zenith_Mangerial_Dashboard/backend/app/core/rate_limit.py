from slowapi import Limiter
from slowapi.util import get_remote_address

import os

# Use Redis-backed storage when REDIS_URL is set (default in Docker Compose).
# Falls back to in-memory for local development without Docker.
REDIS_URL = os.environ.get("REDIS_URL")

if REDIS_URL:
    limiter = Limiter(
        key_func=get_remote_address,
        storage_uri=REDIS_URL,
        default_limits=["60/minute"],
    )
else:
    limiter = Limiter(key_func=get_remote_address, default_limits=["60/minute"])