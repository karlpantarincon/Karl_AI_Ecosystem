"""
Tests for the cache service.
"""

import pytest
import time
from datetime import datetime, timedelta
from unittest.mock import patch

from corehub.services.cache import CacheService, cached, invalidate_cache, get_cache_stats, clear_cache


class TestCacheService:
    """Tests for the CacheService."""
    
    def test_init(self):
        """Test initialization of CacheService."""
        cache = CacheService()
        assert cache.default_ttl == 300
        assert cache.cache == {}
        assert cache.stats["size"] == 0
        assert cache.stats["hits"] == 0
        assert cache.stats["misses"] == 0
        assert cache.stats["evictions"] == 0
    
    def test_set_and_get(self):
        """Test setting and getting a value."""
        cache = CacheService()
        cache.set("test_key", "test_value")
        assert cache.get("test_key") == "test_value"
        assert cache.stats["hits"] == 1
        assert cache.stats["size"] == 1
    
    def test_get_missing_key(self):
        """Test getting a non-existent key."""
        cache = CacheService()
        assert cache.get("missing_key") is None
        assert cache.stats["misses"] == 1
    
    def test_set_with_custom_ttl(self):
        """Test setting a value with a custom TTL."""
        cache = CacheService()
        cache.set("test_key", "test_value", ttl=1)
        assert cache.get("test_key") == "test_value"
    
    def test_expired_entry(self):
        """Test expired cache entry."""
        cache = CacheService()
        cache.set("test_key", "test_value", ttl=1)
        
        # Manually set expired timestamp
        cache.cache["test_key"]["expires_at"] = datetime.utcnow() - timedelta(seconds=1)
        
        # Should be expired
        result = cache.get("test_key")
        assert result is None
        assert cache.stats["misses"] == 1
        assert cache.stats["evictions"] == 1
    
    def test_delete_existing_key(self):
        """Test deleting existing key."""
        cache = CacheService()
        cache.set("test_key", "test_value")
        assert cache.delete("test_key") is True
        assert cache.get("test_key") is None
        assert cache.stats["size"] == 0
    
    def test_delete_missing_key(self):
        """Test deleting missing key."""
        cache = CacheService()
        assert cache.delete("missing_key") is False
    
    def test_clear(self):
        """Test clearing the entire cache."""
        cache = CacheService()
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.clear()
        assert cache.cache == {}
        assert cache.stats["size"] == 0
        assert cache.stats["hits"] == 0
        assert cache.stats["misses"] == 0
        assert cache.stats["evictions"] == 0
    
    def test_cleanup_expired(self):
        """Test cleanup of expired entries."""
        cache = CacheService()
        cache.set("key1", "value1", ttl=1)
        cache.set("key2", "value2", ttl=300)
        
        # Manually expire key1
        cache.cache["key1"]["expires_at"] = datetime.utcnow() - timedelta(seconds=1)
        
        removed_count = cache.cleanup_expired()
        assert removed_count == 1
        assert cache.get("key1") is None
        assert cache.get("key2") == "value2"
        assert cache.stats["size"] == 1
        assert cache.stats["evictions"] == 1
    
    def test_get_stats(self):
        """Test getting cache statistics."""
        cache = CacheService()
        cache.set("key1", "value1")
        cache.get("key1")
        cache.get("key2")
        stats = cache.get_stats()
        assert stats["current_size"] == 1
        assert stats["hits"] == 1
        assert stats["misses"] == 1
        assert stats["total_accesses"] == 2
        assert stats["hit_ratio"] == 0.5
    
    def test_invalidate_pattern(self):
        """Test invalidating entries by pattern."""
        cache = CacheService()
        cache.set("user:1:profile", {"name": "Alice"})
        cache.set("user:2:profile", {"name": "Bob"})
        cache.set("product:101:details", {"price": 100})
        
        invalidated_count = cache.invalidate_pattern(r"user:\d+:profile")
        assert invalidated_count == 2
        assert cache.get("user:1:profile") is None
        assert cache.get("user:2:profile") is None
        assert cache.get("product:101:details") is not None
        assert cache.stats["size"] == 1


# Tests for decorator and global functions
def test_cached_decorator():
    """Test the cached decorator."""
    clear_cache()
    
    @cached(ttl=1)
    def test_function(arg1: str):
        return f"result_{arg1}"
    
    result1 = test_function("a")
    result2 = test_function("a")
    assert result1 == "result_a"
    assert result2 == "result_a"
    assert get_cache_stats()["hits"] == 1
    assert get_cache_stats()["misses"] == 1


def test_invalidate_cache_function():
    """Test invalidate_cache global function."""
    from corehub.services.cache import _cache_service
    clear_cache()
    _cache_service.set("prefix:key1", "value1")
    _cache_service.set("prefix:key2", "value2")
    _cache_service.set("other:key3", "value3")
    
    invalidated = invalidate_cache(r"prefix:.*")
    assert invalidated == 2
    assert _cache_service.get("prefix:key1") is None
    assert _cache_service.get("prefix:key2") is None
    assert _cache_service.get("other:key3") == "value3"


def test_get_cache_stats_function():
    """Test get_cache_stats global function."""
    from corehub.services.cache import _cache_service
    clear_cache()
    _cache_service.set("key1", "value1")
    _cache_service.get("key1")
    stats = get_cache_stats()
    assert stats["current_size"] == 1
    assert stats["hits"] == 1


def test_clear_cache_function():
    """Test clear_cache global function."""
    from corehub.services.cache import _cache_service
    _cache_service.set("key1", "value1")
    clear_cache()
    assert _cache_service.get("key1") is None
    assert get_cache_stats()["current_size"] == 0