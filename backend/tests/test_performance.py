"""
Performance tests for caching and optimization features.
"""
import pytest
import time
from app.services.cache_service import cache_service, CacheKeys, CacheTTL
from app.core.performance import timer, measure_time, performance_monitor


class TestCacheService:
    """Test Redis caching service."""
    
    def test_cache_set_and_get(self):
        """Test basic cache set and get operations."""
        key = "test:key"
        value = {"data": "test_value", "number": 123}
        
        # Set cache
        result = cache_service.set(key, value, ttl=60)
        assert result is True
        
        # Get cache
        cached_value = cache_service.get(key)
        assert cached_value == value
        
        # Cleanup
        cache_service.delete(key)
    
    def test_cache_expiration(self):
        """Test cache TTL expiration."""
        key = "test:expiring"
        value = {"data": "expires"}
        
        # Set with 1 second TTL
        cache_service.set(key, value, ttl=1)
        
        # Should exist immediately
        assert cache_service.exists(key) is True
        
        # Wait for expiration
        time.sleep(1.1)
        
        # Should be expired
        assert cache_service.get(key) is None
    
    def test_cache_delete(self):
        """Test cache deletion."""
        key = "test:delete"
        value = {"data": "to_delete"}
        
        cache_service.set(key, value)
        assert cache_service.exists(key) is True
        
        cache_service.delete(key)
        assert cache_service.exists(key) is False
    
    def test_cache_delete_pattern(self):
        """Test pattern-based cache deletion."""
        # Set multiple keys
        cache_service.set("user:1:stats", {"count": 1})
        cache_service.set("user:2:stats", {"count": 2})
        cache_service.set("user:3:stats", {"count": 3})
        
        # Delete all user stats
        deleted = cache_service.delete_pattern("user:*:stats")
        assert deleted >= 3
        
        # Verify deletion
        assert cache_service.get("user:1:stats") is None
        assert cache_service.get("user:2:stats") is None
    
    def test_cache_get_many(self):
        """Test getting multiple cache values."""
        keys = ["test:multi:1", "test:multi:2", "test:multi:3"]
        values = [{"id": 1}, {"id": 2}, {"id": 3}]
        
        # Set multiple values
        for key, value in zip(keys, values):
            cache_service.set(key, value)
        
        # Get multiple values
        cached_values = cache_service.get_many(keys)
        assert cached_values == values
        
        # Cleanup
        for key in keys:
            cache_service.delete(key)
    
    def test_cache_set_many(self):
        """Test setting multiple cache values."""
        mapping = {
            "test:batch:1": {"id": 1},
            "test:batch:2": {"id": 2},
            "test:batch:3": {"id": 3},
        }
        
        # Set multiple values
        result = cache_service.set_many(mapping, ttl=60)
        assert result is True
        
        # Verify all values
        for key, value in mapping.items():
            assert cache_service.get(key) == value
            cache_service.delete(key)
    
    def test_cache_increment(self):
        """Test cache counter increment."""
        key = "test:counter"
        
        # Increment from 0
        result = cache_service.increment(key, 1)
        assert result == 1
        
        # Increment by 5
        result = cache_service.increment(key, 5)
        assert result == 6
        
        # Cleanup
        cache_service.delete(key)
    
    def test_cache_keys_generation(self):
        """Test cache key generators."""
        user_id = 123
        issue_id = 456
        
        # Test key generation
        assert CacheKeys.user_stats(user_id) == "user:stats:123"
        assert CacheKeys.user_profile(user_id) == "user:profile:123"
        assert CacheKeys.issue_detail(issue_id) == "issue:detail:456"
        assert CacheKeys.user_achievements(user_id) == "user:achievements:123"
    
    def test_cache_ttl_constants(self):
        """Test cache TTL constants."""
        assert CacheTTL.MINUTE == 60
        assert CacheTTL.FIVE_MINUTES == 300
        assert CacheTTL.FIFTEEN_MINUTES == 900
        assert CacheTTL.HOUR == 3600
        assert CacheTTL.DAY == 86400


class TestPerformanceMonitoring:
    """Test performance monitoring utilities."""
    
    def test_timer_context_manager(self):
        """Test timer context manager."""
        with timer("test_operation"):
            time.sleep(0.1)
        # Should log timing without errors
    
    def test_measure_time_decorator(self):
        """Test measure_time decorator."""
        @measure_time
        def slow_function():
            time.sleep(0.1)
            return "done"
        
        result = slow_function()
        assert result == "done"
    
    def test_performance_monitor_record(self):
        """Test recording performance metrics."""
        performance_monitor.clear_metrics()
        
        performance_monitor.record_metric("api_response", 150.5, "ms")
        performance_monitor.record_metric("api_response", 200.0, "ms")
        performance_monitor.record_metric("api_response", 175.5, "ms")
        
        avg = performance_monitor.get_average("api_response")
        assert 170 < avg < 180
    
    def test_performance_monitor_percentile(self):
        """Test percentile calculation."""
        performance_monitor.clear_metrics()
        
        # Record 100 metrics
        for i in range(100):
            performance_monitor.record_metric("test_metric", float(i), "ms")
        
        p95 = performance_monitor.get_percentile("test_metric", 95)
        assert 90 < p95 < 100
        
        p99 = performance_monitor.get_percentile("test_metric", 99)
        assert 95 < p99 < 100
    
    def test_performance_monitor_summary(self):
        """Test performance summary."""
        performance_monitor.clear_metrics()
        
        for i in range(10):
            performance_monitor.record_metric("test_summary", float(i * 10), "ms")
        
        summary = performance_monitor.get_summary()
        assert "test_summary" in summary
        assert summary["test_summary"]["count"] == 10
        assert summary["test_summary"]["average"] == 45.0


class TestCacheIntegration:
    """Integration tests for caching with services."""
    
    def test_user_stats_caching(self, db_session, test_user):
        """Test user stats caching."""
        from app.services.user_service import UserService
        
        service = UserService(db_session)
        
        # First call - should cache
        stats1 = service.get_user_stats(test_user.id, use_cache=True)
        
        # Second call - should use cache
        start_time = time.time()
        stats2 = service.get_user_stats(test_user.id, use_cache=True)
        duration = time.time() - start_time
        
        # Cached call should be very fast
        assert duration < 0.1
        assert stats1 == stats2
    
    def test_cache_invalidation_on_update(self, db_session, test_user):
        """Test cache invalidation when user data changes."""
        from app.services.user_service import UserService
        
        service = UserService(db_session)
        
        # Get stats to cache them
        stats1 = service.get_user_stats(test_user.id, use_cache=True)
        
        # Update user contribution count
        service.increment_contribution_count(test_user.id)
        
        # Get stats again - should be fresh (cache invalidated)
        stats2 = service.get_user_stats(test_user.id, use_cache=True)
        
        # Stats should be different
        assert stats2["total_contributions"] == stats1["total_contributions"] + 1


@pytest.mark.benchmark
class TestPerformanceBenchmarks:
    """Performance benchmark tests."""
    
    def test_cache_read_performance(self, benchmark):
        """Benchmark cache read performance."""
        key = "benchmark:read"
        value = {"data": "test" * 100}
        cache_service.set(key, value)
        
        def read_cache():
            return cache_service.get(key)
        
        result = benchmark(read_cache)
        assert result == value
        
        cache_service.delete(key)
    
    def test_cache_write_performance(self, benchmark):
        """Benchmark cache write performance."""
        key = "benchmark:write"
        value = {"data": "test" * 100}
        
        def write_cache():
            return cache_service.set(key, value, ttl=60)
        
        result = benchmark(write_cache)
        assert result is True
        
        cache_service.delete(key)
    
    def test_database_query_with_cache(self, benchmark, db_session, test_user):
        """Benchmark database query with caching."""
        from app.services.user_service import UserService
        
        service = UserService(db_session)
        
        def get_stats():
            return service.get_user_stats(test_user.id, use_cache=True)
        
        # First call to populate cache
        get_stats()
        
        # Benchmark cached calls
        result = benchmark(get_stats)
        assert result is not None
