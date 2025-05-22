import os
import httpx
import jwt
from fastapi import HTTPException, status, Request
from typing import Optional, Tuple
from .config import settings

_public_key_cache = None

async def get_public_key() -> str:
    global _public_key_cache
    if _public_key_cache:
        return _public_key_cache
    if settings.AUTH_PUBLIC_KEY_URL:
        async with httpx.AsyncClient() as client:
            resp = await client.get(settings.AUTH_PUBLIC_KEY_URL)
            resp.raise_for_status()
            _public_key_cache = resp.text.strip()
            return _public_key_cache
    raise RuntimeError("No AUTH_PUBLIC_KEY_URL configured")

async def validate_jwt_and_extract(request: Request) -> Tuple[int, int]:
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing or invalid Authorization header")
    token = auth_header.split(" ", 1)[1]
    public_key = await get_public_key()
    try:
        payload = jwt.decode(token, public_key, algorithms=["RS256"])
        user_id = payload.get("user_id")
        tenant_id = payload.get("tenant_id")
        if not user_id or not tenant_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="user_id or tenant_id missing in token")
        return user_id, tenant_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") 