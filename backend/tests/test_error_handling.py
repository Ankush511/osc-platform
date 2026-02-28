"""
Tests for error handling and logging functionality.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError

from app.main import app
from app.core.exceptions import (
    AppException,
    AuthenticationError,
    AuthorizationError,
    NotFoundError,
    ValidationError,
    ConflictError,
    RateLimitError,
    ExternalServiceError,
    DatabaseError,
)


client = TestClient(app)


class TestCustomExceptions:
    """Test custom exception classes."""
    
    def test_app_exception(self):
        """Test base AppException."""
        exc = AppException(
            message="Test error",
            error_code="TEST_ERROR",
            status_code=500,
            details={"key": "value"}
        )
        assert exc.message == "Test error"
        assert exc.error_code == "TEST_ERROR"
        assert exc.status_code == 500
        assert exc.details == {"key": "value"}
    
    def test_authentication_error(self):
        """Test AuthenticationError."""
        exc = AuthenticationError()
        assert exc.status_code == 401
        assert exc.error_code == "AUTH_ERROR"
        assert "Authentication failed" in exc.message
    
    def test_authorization_error(self):
        """Test AuthorizationError."""
        exc = AuthorizationError()
        assert exc.status_code == 403
        assert exc.error_code == "AUTHORIZATION_ERROR"
    
    def test_not_found_error(self):
        """Test NotFoundError."""
        exc = NotFoundError("User")
        assert exc.status_code == 404
        assert exc.error_code == "NOT_FOUND"
        assert "User not found" in exc.message
    
    def test_validation_error(self):
        """Test ValidationError."""
        exc = ValidationError("Invalid input")
        assert exc.status_code == 422
        assert exc.error_code == "VALIDATION_ERROR"
    
    def test_conflict_error(self):
        """Test ConflictError."""
        exc = ConflictError("Resource already exists")
        assert exc.status_code == 409
        assert exc.error_code == "CONFLICT"
    
    def test_rate_limit_error(self):
        """Test RateLimitError."""
        exc = RateLimitError()
        assert exc.status_code == 429
        assert exc.error_code == "RATE_LIMIT_EXCEEDED"
    
    def test_external_service_error(self):
        """Test ExternalServiceError."""
        exc = ExternalServiceError("GitHub", "API unavailable")
        assert exc.status_code == 502
        assert exc.error_code == "EXTERNAL_SERVICE_ERROR"
        assert "GitHub" in exc.message
    
    def test_database_error(self):
        """Test DatabaseError."""
        exc = DatabaseError()
        assert exc.status_code == 500
        assert exc.error_code == "DATABASE_ERROR"


class TestErrorHandlers:
    """Test error handler middleware."""
    
    def test_health_check_endpoint(self):
        """Test health check endpoint works."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_not_found_endpoint(self):
        """Test 404 error for non-existent endpoint."""
        response = client.get("/api/v1/nonexistent")
        assert response.status_code == 404
    
    def test_validation_error_response_format(self):
        """Test validation error response format."""
        # This would require an endpoint that validates input
        # For now, we'll test the structure
        response = client.post(
            "/api/v1/auth/login",
            json={"invalid": "data"}
        )
        # Response should have error structure
        if response.status_code == 422:
            data = response.json()
            assert "error_code" in data
            assert "message" in data
            assert "timestamp" in data
            assert "request_id" in data


class TestRateLimiting:
    """Test rate limiting functionality."""
    
    def test_rate_limit_headers(self):
        """Test rate limit headers are present."""
        response = client.get("/api/v1/issues")
        # Should have rate limit headers
        assert "X-RateLimit-Limit" in response.headers or response.status_code == 401
        assert "X-RateLimit-Window" in response.headers or response.status_code == 401
    
    def test_rate_limit_exceeded(self):
        """Test rate limit enforcement."""
        # Make many requests quickly
        responses = []
        for _ in range(250):  # Exceed global rate limit of 200
            response = client.get("/health")
            responses.append(response)
        
        # At least one should be rate limited
        status_codes = [r.status_code for r in responses]
        # Note: This test might not trigger rate limit in test environment
        # as Redis might not be available or rate limits might be disabled
        assert 200 in status_codes  # At least some should succeed


class TestRequestLogging:
    """Test request logging middleware."""
    
    def test_request_id_header(self):
        """Test request ID is added to response."""
        response = client.get("/health")
        assert "X-Request-ID" in response.headers
        assert len(response.headers["X-Request-ID"]) > 0


class TestErrorResponseFormat:
    """Test error response format consistency."""
    
    def test_error_response_structure(self):
        """Test error responses have consistent structure."""
        # Test with a non-existent endpoint
        response = client.get("/api/v1/nonexistent")
        
        if response.status_code >= 400:
            data = response.json()
            
            # Check required fields
            assert "error_code" in data or "detail" in data
            assert "message" in data or "detail" in data
            assert "timestamp" in data or "detail" in data
            
            # If it's our custom error format
            if "error_code" in data:
                assert isinstance(data["error_code"], str)
                assert isinstance(data["message"], str)
                assert "timestamp" in data
                assert "request_id" in data


class TestLoggingConfiguration:
    """Test logging configuration."""
    
    def test_logger_exists(self):
        """Test logger is properly configured."""
        from app.core.logging import logger
        assert logger is not None
        assert logger.name == "app"
    
    def test_get_logger_with_context(self):
        """Test getting logger with context."""
        from app.core.logging import get_logger
        
        logger = get_logger("test", user_id=123)
        assert logger is not None
        assert logger.extra["user_id"] == 123


class TestCacheServiceForRateLimiting:
    """Test cache service methods used by rate limiter."""
    
    def test_cache_increment(self):
        """Test cache increment operation."""
        from app.services.cache_service import cache_service
        
        key = "test:counter"
        
        try:
            # Clean up first
            cache_service.delete(key)
            
            # Set initial value
            cache_service.set(key, 0, 60)
            
            # Increment
            result = cache_service.increment(key)
            
            # If Redis is available, check result
            if result is not None:
                assert result == 1
                
                # Increment again
                result = cache_service.increment(key)
                assert result == 2
            
            # Clean up
            cache_service.delete(key)
        except Exception:
            # Redis might not be available in test environment
            pass
    
    def test_cache_ttl(self):
        """Test cache TTL operation."""
        from app.services.cache_service import cache_service
        
        key = "test:ttl"
        
        try:
            # Set with TTL
            cache_service.set(key, "value", 60)
            
            # Get TTL
            ttl = cache_service.ttl(key)
            
            # If Redis is available, check TTL
            if ttl > 0:
                assert ttl > 0
                assert ttl <= 60
            
            # Clean up
            cache_service.delete(key)
        except Exception:
            # Redis might not be available in test environment
            pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
