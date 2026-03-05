"""
In-memory caching service with TTL support.
Replaces Redis for local development and Supabase-based deployments.
"""
import json
import time
import threading
from typing import Optional, Any, List


class InMemoryCache:
    """Thread-safe in-memory cache with TTL support."""

    def __init__(self):
        self._store: dict = {}
        self._expiry: dict = {}
        self._lock = threading.Lock()

    def _is_expired(self, key: str) -> bool:
        if key in self._expiry and self._expiry[key] < time.time():
            del self._store[key]
            del self._expiry[key]
            return True
        return False

    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            if key not in self._store or self._is_expired(key):
                return None
            return self._store[key]

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        with self._lock:
            self._store[key] = value
            if ttl:
                self._expiry[key] = time.time() + ttl
            elif key in self._expiry:
                del self._expiry[key]
            return True

    def delete(self, key: str) -> bool:
        with self._lock:
            removed = key in self._store
            self._store.pop(key, None)
            self._expiry.pop(key, None)
            return removed

    def delete_pattern(self, pattern: str) -> int:
        """Delete keys matching a simple prefix pattern (supports trailing *)."""
        prefix = pattern.rstrip("*")
        with self._lock:
            keys_to_delete = [k for k in self._store if k.startswith(prefix)]
            for k in keys_to_delete:
                self._store.pop(k, None)
                self._expiry.pop(k, None)
            return len(keys_to_delete)

    def exists(self, key: str) -> bool:
        with self._lock:
            if key not in self._store or self._is_expired(key):
                return False
            return True

    def get_many(self, keys: List[str]) -> List[Optional[Any]]:
        return [self.get(k) for k in keys]

    def set_many(self, mapping: dict, ttl: Optional[int] = None) -> bool:
        for k, v in mapping.items():
            self.set(k, v, ttl)
        return True

    def increment(self, key: str, amount: int = 1) -> Optional[int]:
        with self._lock:
            if key not in self._store or self._is_expired(key):
                self._store[key] = amount
                return amount
            self._store[key] = (self._store[key] or 0) + amount
            return self._store[key]

    def ttl(self, key: str) -> int:
        with self._lock:
            if key not in self._expiry:
                return -1
            remaining = int(self._expiry[key] - time.time())
            return max(remaining, 0)

    def get_ttl(self, key: str) -> Optional[int]:
        val = self.ttl(key)
        return val if val >= 0 else None


class CacheKeys:
    """Cache key generators for consistent naming."""

    @staticmethod
    def user_stats(user_id: int) -> str:
        return f"user:stats:{user_id}"

    @staticmethod
    def user_profile(user_id: int) -> str:
        return f"user:profile:{user_id}"

    @staticmethod
    def issue_list(filters_hash: str) -> str:
        return f"issues:list:{filters_hash}"

    @staticmethod
    def issue_detail(issue_id: int) -> str:
        return f"issue:detail:{issue_id}"

    @staticmethod
    def repository_info(repo_id: int) -> str:
        return f"repo:info:{repo_id}"

    @staticmethod
    def ai_explanation(content_hash: str) -> str:
        return f"ai:explanation:{content_hash}"

    @staticmethod
    def user_achievements(user_id: int) -> str:
        return f"user:achievements:{user_id}"

    @staticmethod
    def contribution_timeline(user_id: int) -> str:
        return f"user:timeline:{user_id}"


class CacheTTL:
    """Cache TTL values in seconds."""
    MINUTE = 60
    FIVE_MINUTES = 300
    FIFTEEN_MINUTES = 900
    HOUR = 3600
    DAY = 86400
    WEEK = 604800

    USER_STATS = FIFTEEN_MINUTES
    USER_PROFILE = HOUR
    ISSUE_LIST = FIVE_MINUTES
    ISSUE_DETAIL = FIFTEEN_MINUTES
    REPOSITORY_INFO = HOUR
    AI_EXPLANATION = DAY
    USER_ACHIEVEMENTS = HOUR
    CONTRIBUTION_TIMELINE = FIFTEEN_MINUTES


# Global cache service instance
cache_service = InMemoryCache()
