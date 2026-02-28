from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings
from app.api.v1 import api_router
from app.core.cache_middleware import ResponseCacheMiddleware
from app.core.rate_limiter import RateLimitMiddleware
from app.core.request_logging import RequestLoggingMiddleware
from app.core.security_headers import SecurityHeadersMiddleware
from app.core.ddos_protection import DDoSProtectionMiddleware
from app.core.exceptions import AppException
from app.core.error_handlers import (
    app_exception_handler,
    validation_exception_handler,
    sqlalchemy_exception_handler,
    generic_exception_handler,
)
from app.core.logging import logger

app = FastAPI(
    title="Open Source Contribution Platform API",
    description="API for managing open source contributions",
    version="1.0.0"
)

# Configure CORS with enhanced security
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
    max_age=settings.CORS_MAX_AGE,
)

# Add security headers middleware (first for all responses)
if settings.ENABLE_SECURITY_HEADERS:
    app.add_middleware(SecurityHeadersMiddleware)

# Add request logging middleware
app.add_middleware(RequestLoggingMiddleware)

# Add DDoS protection middleware (before rate limiting)
if settings.ENABLE_DDOS_PROTECTION:
    app.add_middleware(DDoSProtectionMiddleware)

# Add rate limiting middleware
app.add_middleware(RateLimitMiddleware)

# Add response caching middleware
app.add_middleware(ResponseCacheMiddleware)

# Register exception handlers
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Include API routes
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Open Source Contribution Platform API"}

@app.get("/health")
async def health_check():
    logger.info("Health check requested")
    return {"status": "healthy"}

@app.on_event("startup")
async def startup_event():
    """Log application startup."""
    logger.info(
        "Application starting",
        extra={
            "environment": settings.ENVIRONMENT,
            "version": "1.0.0",
        }
    )

@app.on_event("shutdown")
async def shutdown_event():
    """Log application shutdown."""
    logger.info("Application shutting down")