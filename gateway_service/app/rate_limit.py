import time
from fastapi import HTTPException, status
from .config import settings
from threading import Lock

# In-memory store: {user_id: (count, reset_timestamp)}
_rate_limit_store = {}
_lock = Lock()

RATE_LIMIT = settings.RATE_LIMIT_PER_MINUTE

def check_rate_limit(user_id: int):
    now = int(time.time())
    window = now // 60  # per minute
    key = (user_id, window)
    with _lock:
        count, last_window = _rate_limit_store.get(key, (0, window))
        if last_window != window:
            count = 0
        count += 1
        _rate_limit_store[key] = (count, window)
        if count > RATE_LIMIT:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded: {RATE_LIMIT} requests per minute"
            ) 