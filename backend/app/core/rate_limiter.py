"""
Rate limiting middleware for API endpoints.
"""
import time
from typing import Callable, Optional
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.services.cache_service import cache_service
from app.core.exceptions import RateLimitError
from app.core.logging import logger


class RateLimiter:
    """
    Token bucket rate limiter using Redis.
    """
    
    def __init__(self, requests: int, window: int):
        """
        Initialize rate limiter.
        
        Args:
            requests: Maximum number of requests allowed
            window: Time window in seconds
        """
        self.requests = requests
        self.window = window
    
    def is_allowed(self, key: str) -> tuple[bool, Optional[int]]:
        """
        Check if request is allowed under rate limit.
        
        Args:
            key: Unique identifier for the rate limit (e.g., user ID, IP)
            
        Returns:
            Tuple of (is_allowed, retry_after_seconds)
        """
        cache_key = f"rate_limit:{key}"
        
        # Get current count
        current = cache_service.get(cache_key)
        
        if current is None:
            # First request in window
            cache_service.set(cache_key, 1, self.window)
            return True, None
        
        if current < self.requests:
            # Increment counter
            cache_service.increment(cache_key)
            return True, None
        
        # Rate limit exceeded
        ttl = cache_service.ttl(cache_key)
        return False, ttl if ttl > 0 else self.window


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware to apply rate limiting to API endpoints.
    """
    
    # Rate limits for different endpoint categories
    RATE_LIMITS = {
        "/api/v1/auth": RateLimiter(requests=10, window=60),  # 10 requests per minute
        "/api/v1/issues": RateLimiter(requests=100, window=60),  # 100 requests per minute
        "/api/v1/users": RateLimiter(requests=50, window=60),  # 50 requests per minute
        "/api/v1/contributions": RateLimiter(requests=30, window=60),  # 30 requests per minute
        "/api/v1/ai": RateLimiter(requests=20, window=60),  # 20 requests per minute (AI is expensive)
    }
    
    # Global rate limit for all endpoints
    GLOBAL_RATE_LIMIT = RateLimiter(requests=200, window=60)  # 200 requests per minute
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and apply rate limiting.
        
        Args:
            request: Incoming request
            call_next: Next middleware/handler
            
        Returns:
            Response or rate limit error
        """
        # Check if this is a health check endpoint
        is_health_check = request.url.path in ["/health", "/"]
        
        if not is_health_check:
            # Get identifier for rate limiting (user ID or IP)
            identifier = self._get_identifier(request)
            
            # Check global rate limit
            is_allowed, retry_after = self.GLOBAL_RATE_LIMIT.is_allowed(f"global:{identifier}")
            if not is_allowed:
                logger.warning(
                    f"Global rate limit exceeded for {identifier}",
                    extra={
                        "identifier": identifier,
                        "path": request.url.path,
                        "retry_after": retry_after,
                    }
                )
                return self._rate_limit_response(retry_after)
            
            # Check endpoint-specific rate limit
            for route_prefix, rate_limiter in self.RATE_LIMITS.items():
                if request.url.path.startswith(route_prefix):
                    is_allowed, retry_after = rate_limiter.is_allowed(f"{route_prefix}:{identifier}")
                    if not is_allowed:
                        logger.warning(
                            f"Rate limit exceeded for {route_prefix}",
                            extra={
                                "identifier": identifier,
                                "path": request.url.path,
                                "retry_after": retry_after,
                            }
                        )
                        return self._rate_limit_response(retry_after)
                    break
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers to all responses
        response.headers["X-RateLimit-Limit"] = str(self.GLOBAL_RATE_LIMIT.requests)
        response.headers["X-RateLimit-Window"] = str(self.GLOBAL_RATE_LIMIT.window)
        
        return response
    
    def _get_identifier(self, request: Request) -> str:
        """
        Get unique identifier for rate limiting.
        
        Args:
            request: Incoming request
            
        Returns:
            Identifier string (user ID or IP address)
        """
        # Try to get user ID from headers (set by auth middleware)
        user_id = request.headers.get("X-User-ID")
        if user_id:
            return f"user:{user_id}"
        
        # Fall back to IP address
        client_ip = request.client.host if request.client else "unknown"
        return f"ip:{client_ip}"
    
    def _rate_limit_response(self, retry_after: Optional[int]) -> JSONResponse:
        """
        Create rate limit error response.
        
        Args:
            retry_after: Seconds until rate limit resets
            
        Returns:
            JSON response with rate limit error
        """
        return JSONResponse(
            status_code=429,
            content={
                "error_code": "RATE_LIMIT_EXCEEDED",
                "message": "Too many requests. Please try again later.",
                "details": {"retry_after": retry_after},
                "timestamp": time.time(),
            },
            headers={"Retry-After": str(retry_after)} if retry_after else {}
        )
