"""
REX FastAPI Application

Production-grade API server for Rex orchestration system.
"""

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
import logging
import time
from typing import Dict, Any

from .api_endpoints import (
    rex_router,
    agent_router,
    domain_router,
    inbox_router,
    webhook_router,
)

# ============================================================================
# LOGGING SETUP
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("rex_api")


# ============================================================================
# LIFESPAN EVENTS
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan events for startup and shutdown.
    """
    # Startup
    logger.info("🚀 Rex API Server starting up...")
    logger.info("📡 Registering routes and middleware...")

    yield

    # Shutdown
    logger.info("🛑 Rex API Server shutting down...")


# ============================================================================
# APP INITIALIZATION
# ============================================================================

app = FastAPI(
    title="REX Orchestration API",
    description=(
        "Production-grade API for Rex autonomous orchestration system. "
        "Manages missions, agents, domain pools, and inbox allocation."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)


# ============================================================================
# MIDDLEWARE
# ============================================================================

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests with timing"""
    start_time = time.time()

    # Process request
    response = await call_next(request)

    # Calculate duration
    duration_ms = int((time.time() - start_time) * 1000)

    # Log request
    logger.info(
        f"{request.method} {request.url.path} - {response.status_code} - {duration_ms}ms"
    )

    # Add timing header
    response.headers["X-Process-Time"] = str(duration_ms)

    return response


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors"""
    logger.error(f"Validation error: {exc}")

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": exc.errors(),
            "body": exc.body,
        },
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """Handle all other exceptions"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error",
            "message": str(exc),
        },
    )


# ============================================================================
# ROUTES
# ============================================================================

@app.get("/", tags=["Health"])
async def root() -> Dict[str, Any]:
    """Root endpoint"""
    return {
        "service": "REX Orchestration API",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
async def health_check() -> Dict[str, str]:
    """Health check endpoint for load balancers"""
    return {"status": "healthy"}


@app.get("/ping", tags=["Health"])
async def ping() -> Dict[str, str]:
    """Simple ping endpoint"""
    return {"ping": "pong"}


# ============================================================================
# REGISTER ROUTERS
# ============================================================================

app.include_router(rex_router)
app.include_router(agent_router)
app.include_router(domain_router)
app.include_router(inbox_router)
app.include_router(webhook_router)


# ============================================================================
# ENTRY POINT (for development)
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.rex.app:app",
        host="0.0.0.0",
        port=8080,
        reload=True,
        log_level="info",
    )
