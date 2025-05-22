from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
import logging
from .config import settings
from .proxy import proxy_router

app = FastAPI(title="ReqArchitect API Gateway", description="Unified API Gateway for ReqArchitect platform.")

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("gateway")

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok"}

@app.get("/status", tags=["Health"])
async def status():
    return {"service": "gateway", "status": "running"}

# Placeholder for proxy route
app.include_router(proxy_router) 