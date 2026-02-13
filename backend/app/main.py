"""
FastAPI Main Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.core.logging import setup_logging
import sentry_sdk

# Setup logging
logger = setup_logging()

# Sentry initialization (optional)
if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        traces_sample_rate=1.0,
        environment=settings.ENVIRONMENT
    )
    logger.info("Sentry initialized")

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and include routers
from app.api.v1.endpoints import analyze, files, chat, threats, recovery
from app.services.ml_service import ml_service

# Initialize ML service
ml_service.load_model()

# Include routers
app.include_router(analyze.router, prefix=f"{settings.API_V1_PREFIX}/analyze", tags=["analyze"])
app.include_router(files.router, prefix=f"{settings.API_V1_PREFIX}/files", tags=["files"])
app.include_router(chat.router, prefix=f"{settings.API_V1_PREFIX}/chat", tags=["chat"])
app.include_router(threats.router, prefix=f"{settings.API_V1_PREFIX}/threats", tags=["threats"])
app.include_router(recovery.router, prefix=f"{settings.API_V1_PREFIX}/recovery", tags=["recovery"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "version": settings.VERSION,
        "docs": "/api/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "environment": settings.ENVIRONMENT}

logger.info(f"🚀 {settings.PROJECT_NAME} v{settings.VERSION} started")
