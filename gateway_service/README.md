# ReqArchitect API Gateway

A FastAPI-based API Gateway for the ReqArchitect platform. It provides a unified entry point for all microservices, JWT validation, per-user rate limiting, CORS, and service discovery.

## Features
- Accepts all incoming client requests and routes based on path prefix
- Validates JWT tokens (RS256) using a public key or auth_service
- Extracts `user_id` and `tenant_id` from JWT and injects into downstream headers
- Forwards requests to the correct microservice, preserving method, headers, and body
- Per-user rate limiting (configurable, in-memory)
- Request and response logging
- Health check endpoints: `/health`, `/status`
- CORS support for known frontend origins
- Service discovery/configuration via environment variables
- OpenAPI/Swagger documentation at `/docs`

## Environment Variables (.env example)
```
CANVAS_SERVICE_URL=http://localhost:8001
STRATEGY_SERVICE_URL=http://localhost:8002
BUSINESS_LAYER_SERVICE_URL=http://localhost:8003
APPLICATION_LAYER_SERVICE_URL=http://localhost:8004
TECHNOLOGY_LAYER_SERVICE_URL=http://localhost:8005
MOTIVATION_SERVICE_URL=http://localhost:8006
IMPLEMENTATION_MIGRATION_SERVICE_URL=http://localhost:8007
FILE_SERVICE_URL=http://localhost:8008
NOTIFICATION_SERVICE_URL=http://localhost:8009
BILLING_SERVICE_URL=http://localhost:8010
AUTH_PUBLIC_KEY_URL=http://auth-service:5001/public_key
AUTH_SERVICE_URL=http://auth-service:5001
CORS_ORIGINS=http://localhost:3000
RATE_LIMIT_PER_MINUTE=60
```

## Usage
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Set environment variables (or use a `.env` file).
3. Run the gateway:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8080
   ```
4. Access docs at [http://localhost:8080/docs](http://localhost:8080/docs)

## Endpoints
- `/health` and `/status`: Health checks
- `/canvas/*`, `/strategy/*`, etc.: Proxy to downstream services

## Rate Limiting
- Default: 60 requests per minute per user (configurable via `RATE_LIMIT_PER_MINUTE`)
- Returns HTTP 429 if exceeded

## CORS
- Allowed origins set via `CORS_ORIGINS` (comma-separated)

## Service Discovery
- All downstream service URLs are set via environment variables

## Logging
- All requests, responses, and errors are logged

---

For more details, see the code and OpenAPI docs. 