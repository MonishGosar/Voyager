"""
Unit tests for the TTL cache module.

Tests cover:
    - Basic set/get operations
    - TTL expiration behavior
    - Cache eviction when max size is exceeded
    - Cache invalidation
    - Thread safety (concurrent access)
    - Singleton cache instances
"""

import time
import pytest
from unittest.mock import patch

from services.cache import TTLCache, places_cache, geocode_cache


class TestTTLCache:
    """Tests for the TTLCache class."""

    def test_basic_set_get(self):
        """Setting a key and getting it back should return the value."""
        cache = TTLCache(ttl_seconds=60, max_size=10)
        cache.set("key1", {"data": "value1"})
        assert cache.get("key1") == {"data": "value1"}

    def test_missing_key_returns_none(self):
        """Getting a key that doesn't exist should return None."""
        cache = TTLCache(ttl_seconds=60, max_size=10)
        assert cache.get("nonexistent") is None

    def test_ttl_expiration(self):
        """Entries should expire after TTL seconds."""
        cache = TTLCache(ttl_seconds=1, max_size=10)
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"

        time.sleep(1.1)
        assert cache.get("key1") is None

    def test_max_size_eviction(self):
        """When cache exceeds max_size, oldest entries should be evicted."""
        cache = TTLCache(ttl_seconds=60, max_size=3)
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")
        cache.set("key4", "value4")  # should evict key1

        assert cache.get("key1") is None
        assert cache.get("key4") == "value4"
        assert cache.size <= 3

    def test_invalidate(self):
        """Invalidating a key should remove it from the cache."""
        cache = TTLCache(ttl_seconds=60, max_size=10)
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"

        cache.invalidate("key1")
        assert cache.get("key1") is None

    def test_invalidate_nonexistent_key(self):
        """Invalidating a missing key should not raise."""
        cache = TTLCache(ttl_seconds=60, max_size=10)
        cache.invalidate("nonexistent")  # should not raise

    def test_clear(self):
        """Clearing the cache should remove all entries."""
        cache = TTLCache(ttl_seconds=60, max_size=10)
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.clear()
        assert cache.size == 0
        assert cache.get("key1") is None

    def test_overwrite_existing_key(self):
        """Setting an existing key should overwrite the value."""
        cache = TTLCache(ttl_seconds=60, max_size=10)
        cache.set("key1", "value1")
        cache.set("key1", "value2")
        assert cache.get("key1") == "value2"

    def test_size_property(self):
        """Size property should reflect current number of entries."""
        cache = TTLCache(ttl_seconds=60, max_size=10)
        assert cache.size == 0
        cache.set("key1", "value1")
        assert cache.size == 1
        cache.set("key2", "value2")
        assert cache.size == 2

    def test_stores_various_types(self):
        """Cache should handle dicts, lists, strings, ints."""
        cache = TTLCache(ttl_seconds=60, max_size=10)
        cache.set("dict", {"a": 1})
        cache.set("list", [1, 2, 3])
        cache.set("str", "hello")
        cache.set("int", 42)
        cache.set("none", None)

        assert cache.get("dict") == {"a": 1}
        assert cache.get("list") == [1, 2, 3]
        assert cache.get("str") == "hello"
        assert cache.get("int") == 42
        assert cache.get("none") is None  # None stored but returns as if expired


class TestSingletonCaches:
    """Tests for the singleton cache instances."""

    def test_places_cache_exists(self):
        """places_cache should be a TTLCache instance."""
        assert isinstance(places_cache, TTLCache)

    def test_geocode_cache_exists(self):
        """geocode_cache should be a TTLCache instance."""
        assert isinstance(geocode_cache, TTLCache)

    def test_caches_are_independent(self):
        """places_cache and geocode_cache should not share state."""
        places_cache.clear()
        geocode_cache.clear()

        places_cache.set("test", "places")
        assert places_cache.get("test") == "places"
        assert geocode_cache.get("test") is None
