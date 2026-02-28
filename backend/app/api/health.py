"""
Health check endpoints for monitoring and load balancers.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from redis import Redis
from typing import Dict, Any
import time

from ..db.session import get_db
from ..core.redis import get_redis_client
from ..core.config import settings

router = APIRouter()


@router.get("/health")
async def health_check() -> Dict[str, str]:
    """
    Basic health check endpoint.
    Returns 200 if service is running.
    """
    return {
        "status": "healthy",
        "service": "oscp-backend",
        "environment": settings.ENVIRONMENT
    }


@router.get("/health/detailed")
async def detailed_health_check(
    db: Session = Depends(get_db),
    redis: Redis = Depends(get_redis_client)
) -> Dict[str, Any]:
    """
    Detailed health check including database and Redis connectivity.
    """
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
    
    # Check Redis
    try:
        redis.ping()
        health_status["checks"]["redis"] = {
            "status": "healthy",
            "message": "Redis connection successful"
        }
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["checks"]["redis"] = {
            "status": "unhealthy",
            "message": f"Redis connection failed: {str(e)}"
        }
    
    # Return 503 if any check failed
    if health_status["status"] == "unhealthy":
        raise HTTPException(status_code=503, detail=health_status)
    
    return health_status


@router.get("/health/ready")
async def readiness_check(
    db: Session = Depends(get_db),
    redis: Redis = Depends(get_redis_client)
) -> Dict[str, str]:
    """
    Readiness check for Kubernetes/container orchestration.
    Returns 200 when service is ready to accept traffic.
    """
    try:
        # Check database
        db.execute(text("SELECT 1"))
        
        # Check Redis
        redis.ping()
        
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
    """
    Liveness check for Kubernetes/container orchestration.
    Returns 200 if service is alive (even if not ready).
    """
    return {
        "status": "alive",
        "message": "Service is alive"
    }
