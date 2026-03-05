"""
Health check endpoints for monitoring and load balancers.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Dict, Any
import time

from ..db.base import get_db
from ..core.config import settings

router = APIRouter()


@router.get("/health")
async def health_check() -> Dict[str, str]:
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "service": "oscp-backend",
        "environment": settings.ENVIRONMENT
    }


@router.get("/health/detailed")
async def detailed_health_check(
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Detailed health check including database connectivity."""
    health_status = {
        "status": "healthy",
        "service": "oscp-backend",
        "environment": settings.ENVIRONMENT,
        "timestamp": int(time.time()),
        "checks": {}
    }

    # Check database
    try:
        db.execute(text("SELECT 1"))
        health_status["checks"]["database"] = {
            "status": "healthy",
            "message": "Database connection successful"
        }
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["checks"]["database"] = {
            "status": "unhealthy",
            "message": f"Database connection failed: {str(e)}"
        }

    if health_status["status"] == "unhealthy":
        raise HTTPException(status_code=503, detail=health_status)

    return health_status


@router.get("/health/ready")
async def readiness_check(
    db: Session = Depends(get_db),
) -> Dict[str, str]:
    """Readiness check for container orchestration."""
    try:
        db.execute(text("SELECT 1"))
        return {
            "status": "ready",
            "message": "Service is ready to accept traffic"
        }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail={
                "status": "not_ready",
                "message": f"Service is not ready: {str(e)}"
            }
        )


@router.get("/health/live")
async def liveness_check() -> Dict[str, str]:
    """Liveness check."""
    return {
        "status": "alive",
        "message": "Service is alive"
    }
