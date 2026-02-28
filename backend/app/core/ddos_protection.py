"""
DDoS protection middleware with IP-based rate limiting and blacklisting.
"""
import time
from typing import Callable, Optional, Set
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.services.cache_service import cache_service
from app.core.config import settings
from app.core.logging import logger


class DDoSProtectionMiddleware(BaseHTTPMiddleware):
    """
    Advanced DDoS protection with IP tracking and automatic blacklisting.
    """
    
    # In-memory set for quick blacklist checks (synced with Redis)
    _blacklisted_ips: Set[str] = set()
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Check request against DDoS protection rules.
        
        Args:
            request: Incoming request
            call_next: Next middleware/handler
            
        Returns:
            Response or blocked response
        """
        if not settings.ENABLE_DDOS_PROTECTION:
            return await call_next(request)
        
        # Skip protection for health check
        if request.url.path in ["/health", "/"]:
            return await call_next(request)
        
        # Get client IP
        client_ip = self._get_client_ip(request)
        
        # Check if IP is blacklisted
        if self._is_blacklisted(client_ip):
            logger.warning(
                f"Blocked request from blacklisted IP: {client_ip}",
                extra={"ip": client_ip, "path": request.url.path}
            )
            return self._blocked_response("IP address is temporarily blocked")
        
        # Check rate limits
        is_allowed, reason = self._check_rate_limits(client_ip)
        if not is_allowed:
            logger.warning(
                f"Rate limit exceeded for IP: {client_ip}",
                extra={"ip": client_ip, "reason": reason, "path": request.url.path}
            )
            
            # Check if IP should be blacklisted
            if self._should_blacklist(client_ip):
                self._blacklist_ip(client_ip)
                logger.error(
                    f"IP blacklisted due to excessive requests: {client_ip}",
                    extra={"ip": client_ip}
                )
                return self._blocked_response("IP address has been temporarily blocked due to excessive requests")
            
            return self._rate_limit_response(reason)
        
        # Track request
        self._track_request(client_ip)
        
        # Process request
        response = await call_next(request)
        
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """
        Get client IP address, considering proxy headers.
        
        Args:
            request: Incoming request
            
        Returns:
            Client IP address
        """
        # Check X-Forwarded-For header (for proxies/load balancers)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Take the first IP in the chain
            return forwarded_for.split(",")[0].strip()
        
        # Check X-Real-IP header
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip.strip()
        
        # Fall back to direct client IP
        return request.client.host if request.client else "unknown"
    
    def _is_blacklisted(self, ip: str) -> bool:
        """
        Check if IP is blacklisted.
        
        Args:
            ip: IP address
            
        Returns:
            True if blacklisted
        """
        # Check in-memory cache first
        if ip in self._blacklisted_ips:
            return True
        
        # Check Redis
        blacklist_key = f"blacklist:{ip}"
        is_blacklisted = cache_service.get(blacklist_key)
        
        if is_blacklisted:
            self._blacklisted_ips.add(ip)
            return True
        
        return False
    
    def _check_rate_limits(self, ip: str) -> tuple[bool, Optional[str]]:
        """
        Check if IP is within rate limits.
        
        Args:
            ip: IP address
            
        Returns:
            Tuple of (is_allowed, reason)
        """
        # Check per-minute limit
        minute_key = f"ddos:minute:{ip}"
        minute_count = cache_service.get(minute_key) or 0
        
        if minute_count >= settings.MAX_REQUESTS_PER_IP_PER_MINUTE:
            return False, "Too many requests per minute"
        
        # Check per-hour limit
        hour_key = f"ddos:hour:{ip}"
        hour_count = cache_service.get(hour_key) or 0
        
        if hour_count >= settings.MAX_REQUESTS_PER_IP_PER_HOUR:
            return False, "Too many requests per hour"
        
        return True, None
    
    def _track_request(self, ip: str) -> None:
        """
        Track request for rate limiting.
        
        Args:
            ip: IP address
        """
        # Track per-minute
        minute_key = f"ddos:minute:{ip}"
        current = cache_service.get(minute_key)
        if current is None:
            cache_service.set(minute_key, 1, 60)
        else:
            cache_service.increment(minute_key)
        
        # Track per-hour
        hour_key = f"ddos:hour:{ip}"
        current = cache_service.get(hour_key)
        if current is None:
            cache_service.set(hour_key, 1, 3600)
        else:
            cache_service.increment(hour_key)
    
    def _should_blacklist(self, ip: str) -> bool:
        """
        Determine if IP should be blacklisted based on behavior.
        
        Args:
            ip: IP address
            
        Returns:
            True if IP should be blacklisted
        """
        minute_key = f"ddos:minute:{ip}"
        minute_count = cache_service.get(minute_key) or 0
        
        # Blacklist if exceeding suspicious threshold
        return minute_count >= settings.SUSPICIOUS_IP_THRESHOLD
    
    def _blacklist_ip(self, ip: str) -> None:
        """
        Add IP to blacklist.
        
        Args:
            ip: IP address
        """
        blacklist_key = f"blacklist:{ip}"
        cache_service.set(blacklist_key, 1, settings.IP_BLACKLIST_DURATION)
        self._blacklisted_ips.add(ip)
        
        logger.error(
            f"IP blacklisted: {ip}",
            extra={
                "ip": ip,
                "duration": settings.IP_BLACKLIST_DURATION,
            }
        )
    
    def _rate_limit_response(self, reason: str) -> JSONResponse:
        """
        Create rate limit error response.
        
        Args:
            reason: Reason for rate limiting
            
        Returns:
            JSON response with rate limit error
        """
        return JSONResponse(
            status_code=429,
            content={
                "error_code": "RATE_LIMIT_EXCEEDED",
                "message": reason,
                "timestamp": time.time(),
            }
        )
    
    def _blocked_response(self, reason: str) -> JSONResponse:
        """
        Create blocked response.
        
        Args:
            reason: Reason for blocking
            
        Returns:
            JSON response with blocked error
        """
        return JSONResponse(
            status_code=403,
            content={
                "error_code": "ACCESS_BLOCKED",
                "message": reason,
                "timestamp": time.time(),
            }
        )
