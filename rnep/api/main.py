"""
FastAPI application entry point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from typing import Dict

from rnep.config.settings import settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    # Startup
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Debug mode: {settings.debug}")
    
    # Initialize database connection pool
    # TODO: Initialize database when SQLAlchemy models are ready
    
    # Initialize Redis connection
    # TODO: Initialize Redis when caching is implemented
    
    yield
    
    # Shutdown
    logger.info("Shutting down application")
    # TODO: Close database connections
    # TODO: Close Redis connections


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Risk and Noise Evaluation Platform for UAM",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Root endpoint
@app.get("/", tags=["Health"])
async def root() -> Dict[str, str]:
    """Root endpoint"""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "healthy"
    }


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check() -> Dict[str, str]:
    """Health check endpoint"""
    # TODO: Add database and Redis health checks
    return {
        "status": "healthy",
        "database": "pending",  # Will be updated when DB is connected
        "redis": "pending"      # Will be updated when Redis is connected
    }


# API version endpoint
@app.get("/api/version", tags=["Health"])
async def get_version() -> Dict[str, str]:
    """Get API version information"""
    return {
        "version": settings.app_version,
        "api_prefix": settings.api_prefix
    }


# Include routers
# TODO: Include routers when they are implemented
# from rnep.api.routes import scenarios, evaluations, flight_paths
# app.include_router(scenarios.router, prefix=f"{settings.api_prefix}/scenarios", tags=["Scenarios"])
# app.include_router(evaluations.router, prefix=f"{settings.api_prefix}/evaluations", tags=["Evaluations"])
# app.include_router(flight_paths.router, prefix=f"{settings.api_prefix}/flight-paths", tags=["Flight Paths"])


# Exception handlers
@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    """Handle validation errors"""
    return {
        "error": {
            "code": "VALIDATION_ERROR",
            "message": str(exc)
        }
    }


@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Handle 404 errors"""
    return {
        "error": {
            "code": "NOT_FOUND",
            "message": "The requested resource was not found"
        }
    }


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Handle internal server errors"""
    logger.error(f"Internal server error: {exc}")
    return {
        "error": {
            "code": "INTERNAL_ERROR",
            "message": "An internal server error occurred"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "rnep.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug
    )