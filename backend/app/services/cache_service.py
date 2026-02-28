"""
Redis caching service for frequently accessed data.
"""
import json
import redis
from typing import Optional, Any, List
from datetime import timedelta
from app.core.config import settings


class CacheService:
    """Service for managing Redis cache operations."""
    
    def __init__(self):
        """Initialize Redis connection."""
        self.redis_client = redis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5
        )
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found
        """
        try:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except (redis.RedisError, json.JSONDecodeError):
            return None
    
    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Set value in cache with optional TTL.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
            
        Returns:
            True if successful, False otherwise
        """
        try:
            serialized = json.dumps(value)
            if ttl:
                return self.redis_client.setex(key, ttl, serialized)
            return self.redis_client.set(key, serialized)
        except (redis.RedisError, TypeError):
            return False
    
    def delete(self, key: str) -> bool:
        """
        Delete key from cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if successful, False otherwise
        """
        try:
            return bool(self.redis_client.delete(key))
        except redis.RedisError:
            return False
    
    def delete_pattern(self, pattern: str) -> int:
        """
        Delete all keys matching pattern.
        
        Args:
            pattern: Key pattern (e.g., "user:*")
            
        Returns:
            Number of keys deleted
        """
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except redis.RedisError:
            return 0
    
    def exists(self, key: str) -> bool:
        """
        Check if key exists in cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if key exists, False otherwise
        """
        try:
            return bool(self.redis_client.exists(key))
        except redis.RedisError:
            return False
    
    def get_many(self, keys: List[str]) -> List[Optional[Any]]:
        """
        Get multiple values from cache.
        
        Args:
            keys: List of cache keys
            
        Returns:
            List of cached values (None for missing keys)
        """
        try:
            values = self.redis_client.mget(keys)
            return [json.loads(v) if v else None for v in values]
        except (redis.RedisError, json.JSONDecodeError):
            return [None] * len(keys)
    
    def set_many(
        self,
        mapping: dict,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Set multiple key-value pairs in cache.
        
        Args:
            mapping: Dictionary of key-value pairs
            ttl: Time to live in seconds
            
        Returns:
            True if successful, False otherwise
        """
        try:
            serialized = {k: json.dumps(v) for k, v in mapping.items()}
            pipeline = self.redis_client.pipeline()
            pipeline.mset(serialized)
            if ttl:
                for key in serialized.keys():
                    pipeline.expire(key, ttl)
            pipeline.execute()
            return True
        except (redis.RedisError, TypeError):
            return False
    
    def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """
        Increment a counter in cache.
        
        Args:
            key: Cache key
            amount: Amount to increment by
            
        Returns:
            New value or None if error
        """
        try:
            return self.redis_client.incrby(key, amount)
        except redis.RedisError:
            return None
    
    def get_ttl(self, key: str) -> Optional[int]:
        """
        Get remaining TTL for a key.
        
        Args:
            key: Cache key
            
        Returns:
            TTL in seconds or None if key doesn't exist
        """
        try:
            ttl = self.redis_client.ttl(key)
            return ttl if ttl >= 0 else None
        except redis.RedisError:
            return None
    
    def ttl(self, key: str) -> int:
        """
        Get remaining TTL for a key (alias for get_ttl).
        
        Args:
            key: Cache key
            
        Returns:
            TTL in seconds or -1 if key doesn't exist
        """
        try:
            return self.redis_client.ttl(key)
        except redis.RedisError:
            return -1


# Cache key generators
class CacheKeys:
    """Cache key generators for consistent naming."""
    
    @staticmethod
    def user_stats(user_id: int) -> str:
        """Generate cache key for user statistics."""
        return f"user:stats:{user_id}"
    
    @staticmethod
    def user_profile(user_id: int) -> str:
        """Generate cache key for user profile."""
        return f"user:profile:{user_id}"
    
    @staticmethod
    def issue_list(filters_hash: str) -> str:
        """Generate cache key for filtered issue list."""
        return f"issues:list:{filters_hash}"
    
    @staticmethod
    def issue_detail(issue_id: int) -> str:
        """Generate cache key for issue details."""
        return f"issue:detail:{issue_id}"
    
    @staticmethod
    def repository_info(repo_id: int) -> str:
        """Generate cache key for repository information."""
        return f"repo:info:{repo_id}"
    
    @staticmethod
    def ai_explanation(content_hash: str) -> str:
        """Generate cache key for AI explanations."""
        return f"ai:explanation:{content_hash}"
    
    @staticmethod
    def user_achievements(user_id: int) -> str:
        """Generate cache key for user achievements."""
        return f"user:achievements:{user_id}"
    
    @staticmethod
    def contribution_timeline(user_id: int) -> str:
        """Generate cache key for contribution timeline."""
        return f"user:timeline:{user_id}"


# Cache TTL constants (in seconds)
class CacheTTL:
    """Cache TTL values for different data types."""
    
    MINUTE = 60
    FIVE_MINUTES = 300
    FIFTEEN_MINUTES = 900
    HOUR = 3600
    DAY = 86400
    WEEK = 604800
    
    # Specific TTLs
    USER_STATS = FIFTEEN_MINUTES
    USER_PROFILE = HOUR
    ISSUE_LIST = FIVE_MINUTES
    ISSUE_DETAIL = FIFTEEN_MINUTES
    REPOSITORY_INFO = HOUR
    AI_EXPLANATION = DAY
    USER_ACHIEVEMENTS = HOUR
    CONTRIBUTION_TIMELINE = FIFTEEN_MINUTES


# Global cache service instance
cache_service = CacheService()
