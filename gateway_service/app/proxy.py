from fastapi import APIRouter, Request, Response, HTTPException
from fastapi.responses import StreamingResponse
import httpx
from starlette.status import HTTP_502_BAD_GATEWAY
from .auth import validate_jwt_and_extract
from .config import settings
import logging
from .rate_limit import check_rate_limit

logger = logging.getLogger("gateway.proxy")

proxy_router = APIRouter()

SERVICE_MAP = {
    'canvas': settings.CANVAS_SERVICE_URL,
    'strategy': settings.STRATEGY_SERVICE_URL,
    'business': settings.BUSINESS_LAYER_SERVICE_URL,
    'application': settings.APPLICATION_LAYER_SERVICE_URL,
    'technology': settings.TECHNOLOGY_LAYER_SERVICE_URL,
    'motivation': settings.MOTIVATION_SERVICE_URL,
    'implementation': settings.IMPLEMENTATION_MIGRATION_SERVICE_URL,
    'files': settings.FILE_SERVICE_URL,
    'notifications': settings.NOTIFICATION_SERVICE_URL,
    'billing': settings.BILLING_SERVICE_URL,
}

@proxy_router.api_route("/{service}/{full_path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
async def proxy(service: str, full_path: str, request: Request):
    if service not in SERVICE_MAP:
        raise HTTPException(status_code=404, detail=f"Unknown service: {service}")
    downstream_url = f"{SERVICE_MAP[service]}/{full_path}"
    user_id, tenant_id = await validate_jwt_and_extract(request)
    # Rate limiting
    try:
        check_rate_limit(user_id)
    except HTTPException as e:
        logger.warning(f"Rate limit exceeded for user {user_id}")
        raise
    # Prepare headers
    headers = dict(request.headers)
    headers["X-User-ID"] = str(user_id)
    headers["X-Tenant-ID"] = str(tenant_id)
    # Remove host header to avoid issues
    headers.pop("host", None)
    # Prepare request body
    body = await request.body()
    # Log request
    logger.info(f"Proxying {request.method} {request.url.path} to {downstream_url} for user {user_id} tenant {tenant_id}")
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.request(
                method=request.method,
                url=downstream_url,
                headers=headers,
                content=body if body else None,
                params=request.query_params
            )
        # Log response
        logger.info(f"Downstream {downstream_url} responded {resp.status_code}")
        # Stream response back
        return Response(
            content=resp.content,
            status_code=resp.status_code,
            headers={k: v for k, v in resp.headers.items() if k.lower() not in {"content-encoding", "transfer-encoding", "connection"}}
        )
    except httpx.RequestError as e:
        logger.error(f"Error proxying to {downstream_url}: {e}")
        raise HTTPException(status_code=HTTP_502_BAD_GATEWAY, detail=f"Service unavailable: {service}") 