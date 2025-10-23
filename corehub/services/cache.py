"""
Cache service for CoreHub.

This module provides a simple in-memory cache with TTL support
for optimizing database queries and API responses.
"""

import time
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, Optional
import re
from functools import wraps

from loguru import logger


class CacheService:
    """
    A simple in-memory cache service with TTL (Time-To-Live) support.
    """
    
    def __init__(self, default_ttl: int = 300):  # Default TTL of 5 minutes
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.default_ttl = default_ttl
        self.stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "size": 0,
            "last_cleanup": datetime.utcnow(),
        }
        logger.info("CacheService initialized.")
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Sets a value in the cache with an optional TTL.
        If TTL is None, uses the default_ttl.
        """
        actual_ttl = ttl if ttl is not None else self.default_ttl
        expires_at = datetime.utcnow() + timedelta(seconds=actual_ttl)
        
        self.cache[key] = {
            "value": value,
            "expires_at": expires_at,
            "created_at": datetime.utcnow(),
            "ttl": actual_ttl,
        }
        self.stats["size"] = len(self.cache)
        logger.debug(f"Cache set: {key} (TTL: {actual_ttl}s)")
    
    def get(self, key: str) -> Optional[Any]:
        """
        Retrieves a value from the cache. Returns None if key is not found or expired.
        """
        entry = self.cache.get(key)
        if entry:
            if datetime.utcnow() > entry["expires_at"]:
                logger.debug(f"Cache expired: {key}")
                self.delete(key)
                self.stats["evictions"] += 1
                self.stats["misses"] += 1
                return None
            self.stats["hits"] += 1
            logger.debug(f"Cache hit: {key}")
            return entry["value"]
        self.stats["misses"] += 1
        logger.debug(f"Cache miss: {key}")
        return None
    
    def delete(self, key: str) -> bool:
        """
        Deletes a key-value pair from the cache.
        Returns True if the key was found and deleted, False otherwise.
        """
        if key in self.cache:
            del self.cache[key]
            self.stats["size"] = len(self.cache)
            logger.debug(f"Cache deleted: {key}")
            return True
        logger.debug(f"Cache delete failed: {key} not found")
        return False
    
    def clear(self) -> None:
        """
        Clears the entire cache.
        """
        self.cache.clear()
        self.stats["size"] = 0
        self.stats["hits"] = 0
        self.stats["misses"] = 0
        self.stats["evictions"] = 0
        logger.info("Cache cleared.")
    
    def cleanup_expired(self) -> int:
        """
        Removes all expired entries from the cache.
        Returns the number of entries removed.
        """
        removed_count = 0
        now = datetime.utcnow()
        keys_to_delete = [key for key, entry in self.cache.items() if now > entry["expires_at"]]
        for key in keys_to_delete:
            self.delete(key)
            self.stats["evictions"] += 1
            removed_count += 1
        self.stats["last_cleanup"] = now
        logger.info(f"Cache cleanup completed. Removed {removed_count} expired entries.")
        return removed_count
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Returns current cache statistics.
        """
        return {
            "current_size": self.stats["size"],
            "hits": self.stats["hits"],
            "misses": self.stats["misses"],
            "evictions": self.stats["evictions"],
            "total_accesses": self.stats["hits"] + self.stats["misses"],
            "hit_ratio": self.stats["hits"] / (self.stats["hits"] + self.stats["misses"]) if (self.stats["hits"] + self.stats["misses"]) > 0 else 0,
            "last_cleanup": self.stats["last_cleanup"].isoformat(),
        }
    
    def invalidate_pattern(self, pattern: str) -> int:
        """
        Invalidates cache entries whose keys match the given regex pattern.
        Returns the number of entries invalidated.
        """
        removed_count = 0
        keys_to_delete = [key for key in self.cache if re.match(pattern, key)]
        for key in keys_to_delete:
            self.delete(key)
            removed_count += 1
        logger.info(f"Invalidated {removed_count} cache entries matching pattern: {pattern}")
        return removed_count


# Global cache instance
_cache_service = CacheService()


def cached(ttl: Optional[int] = None):
    """
    Decorator to cache function results.
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create a cache key from function name and arguments
            # Simple serialization for demonstration; consider a more robust one for complex args
            key_parts = [func.__name__] + [str(arg) for arg in args] + [f"{k}={v}" for k, v in sorted(kwargs.items())]
            cache_key = ":".join(key_parts)
            
            result = _cache_service.get(cache_key)
            if result is not None:
                return result
            
            # If not in cache, execute function and store result
            result = func(*args, **kwargs)
            _cache_service.set(cache_key, result, ttl)
            return result
        return wrapper
    return decorator


def invalidate_cache(pattern: str) -> int:
    """Invalidates cache entries matching a pattern."""
    return _cache_service.invalidate_pattern(pattern)


def get_cache_stats() -> Dict[str, Any]:
    """Returns global cache statistics."""
    return _cache_service.get_stats()


def clear_cache() -> None:
    """Clears the global cache."""
    _cache_service.clear()