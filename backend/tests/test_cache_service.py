"""
Unit tests for cache service
"""

import pytest
from unittest.mock import Mock, patch
from app.services.cache_service import CacheService
import json


@pytest.fixture
def cache_service():
    """Create cache service instance"""
    with patch('app.services.cache_service.redis_client') as mock_redis:
        service = CacheService()
        service.redis = mock_redis
        yield service


class TestCacheService:
    """Test cache service operations"""
    
    def test_set_and_get_string(self, cache_service):
        """Test setting and getting string values"""
        cache_service.redis.get.return_value = b"test_value"
        
        # Set value
        cache_service.set("test_key", "test_value", ttl=300)
        cache_service.redis.setex.assert_called_once()
        
        # Get value
        result = cache_service.get("test_key")
        assert result == "test_value"
    
    def test_set_and_get_dict(self, cache_service):
        """Test setting and getting dictionary values"""
        test_dict = {"name": "test", "value": 123}
        cache_service.redis.get.return_value = json.dumps(test_dict).encode()
        
        # Set value
        cache_service.set("test_key", test_dict, ttl=300)
        
        # Get value
        result = cache_service.get("test_key")
        assert result == test_dict
    
    def test_delete_key(self, cache_service):
        """Test deleting cache key"""
        cache_service.delete("test_key")
        cache_service.redis.delete.assert_called_once_with("test_key")
    
    def test_exists(self, cache_service):
        """Test checking if key exists"""
        cache_service.redis.exists.return_value = 1
        
        result = cache_service.exists("test_key")
        assert result is True
        
        cache_service.redis.exists.return_value = 0
        result = cache_service.exists("test_key")
        assert result is False
    
    def test_get_nonexistent_key(self, cache_service):
        """Test getting non-existent key returns None"""
        cache_service.redis.get.return_value = None
        
        result = cache_service.get("nonexistent_key")
        assert result is None
    
    def test_clear_pattern(self, cache_service):
        """Test clearing keys by pattern"""
        cache_service.redis.keys.return_value = [b"test:1", b"test:2", b"test:3"]
        
        cache_service.clear_pattern("test:*")
        
        cache_service.redis.keys.assert_called_once_with("test:*")
        assert cache_service.redis.delete.call_count == 3
    
    def test_increment(self, cache_service):
        """Test incrementing counter"""
        cache_service.redis.incr.return_value = 5
        
        result = cache_service.increment("counter_key")
        assert result == 5
        cache_service.redis.incr.assert_called_once_with("counter_key")
    
    def test_decrement(self, cache_service):
        """Test decrementing counter"""
        cache_service.redis.decr.return_value = 3
        
        result = cache_service.decrement("counter_key")
        assert result == 3
        cache_service.redis.decr.assert_called_once_with("counter_key")
    
    def test_set_with_default_ttl(self, cache_service):
        """Test setting value with default TTL"""
        cache_service.set("test_key", "test_value")
        # Should use default TTL
        cache_service.redis.setex.assert_called_once()
    
    def test_cache_decorator(self, cache_service):
        """Test cache decorator functionality"""
        # This would test the @cache decorator if implemented
        pass
