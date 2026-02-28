"""
API response caching middleware for FastAPI.
"""
import hashlib
import json
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.services.cache_service import cache_service


class ResponseCacheMiddleware(BaseHTTPMiddleware):
    """
    Middleware to cache API responses based on request path and query parameters.
    
    Only caches GET requests with 200 status codes.
    """
    
    # Routes to cache with their TTL in seconds
    CACHEABLE_ROUTES = {
        "/api/v1/issues": 300,  # 5 minutes
        "/api/v1/repositories": 3600,  # 1 hour
        "/api/v1/users/me/stats": 900,  # 15 minutes
        "/api/v1/users/me/achievements": 3600,  # 1 hour
    }
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and cache response if applicable.
        
        Args:
            request: Incoming request
            call_next: Next middleware/handler
            
        Returns:
            Response (cached or fresh)
        """
        # Only cache GET requests
        if request.method != "GET":
            return await call_next(request)
        
        # Check if route is cacheable
        route_path = request.url.path
        ttl = None
        
        for cacheable_route, route_ttl in self.CACHEABLE_ROUTES.items():
            if route_path.startswith(cacheable_route):
                ttl = route_ttl
                break
        
        # If route is not cacheable, proceed without caching
        if ttl is None:
            return await call_next(request)
        
        # Generate cache key from request
        cache_key = self._generate_cache_key(request)
        
        # Try to get cached response
        cached_response = cache_service.get(cache_key)
        if cached_response:
            return JSONResponse(
                content=cached_response["content"],
                status_code=cached_response["status_code"],
                headers={"X-Cache": "HIT"}
            )
        
        # Process request
        response = await call_next(request)
        
        # Only cache successful responses
        if response.status_code == 200:
            # Read response body
            response_body = b""
            async for chunk in response.body_iterator:
                response_body += chunk
            
            try:
                # Parse JSON response
                content = json.loads(response_body.decode())
                
                # Cache the response
                cache_data = {
                    "content": content,
                    "status_code": response.status_code
                }
                cache_service.set(cache_key, cache_data, ttl)
                
                # Return new response with cached data
                return JSONResponse(
                    content=content,
                    status_code=response.status_code,
                    headers={"X-Cache": "MISS"}
                )
            except (json.JSONDecodeError, UnicodeDecodeError):
                # If response is not JSON, return as-is
                return Response(
                    content=response_body,
                    status_code=response.status_code,
                    headers=dict(response.headers)
                )
        
        return response
    
    def _generate_cache_key(self, request: Request) -> str:
        """
        Generate cache key from request path and query parameters.
        
        Args:
            request: Incoming request
            
        Returns:
            Cache key string
        """
        # Include path and sorted query parameters
        path = request.url.path
        query_params = sorted(request.query_params.items())
        
        # Include user ID if authenticated (from headers or session)
        user_id = request.headers.get("X-User-ID", "anonymous")
        
        # Create cache key
        key_parts = [path, str(query_params), user_id]
        key_string = "|".join(key_parts)
        
        # Hash for consistent key length
        key_hash = hashlib.md5(key_string.encode()).hexdigest()
        
        return f"api:response:{key_hash}"


def invalidate_cache_for_user(user_id: int):
    """
    Invalidate all cached responses for a specific user.
    
    Args:
        user_id: User ID to invalidate cache for
    """
    # This is a helper function that can be called when user data changes
    cache_service.delete_pattern(f"api:response:*")


def invalidate_cache_for_route(route_path: str):
    """
    Invalidate all cached responses for a specific route.
    
    Args:
        route_path: Route path to invalidate cache for
    """
    cache_service.delete_pattern(f"api:response:*")
