import pytest
import os
from src.modules.cache import CacheManager

@pytest.mark.unit
def test_cache_manager_initialization():
    """Test Cache Manager initialization"""
    manager = CacheManager()
    assert manager is not None

@pytest.mark.unit
def test_cache_manager_cache_write():
    """Test cache write operation"""
    manager = CacheManager()
    manager.cache_write("test_key", "test_value")
    assert manager.cache_read("test_key") == "test_value"

@pytest.mark.unit
def test_cache_manager_cache_expiry():
    """Test 15-minute cache expiry"""
    manager = CacheManager()
    expiry_time = manager.get_cache_expiry()
    assert expiry_time == 900  # 15 minutes

@pytest.mark.unit
def test_cache_manager_cache_refresh():
    """Test cache refresh mechanism"""
    manager = CacheManager()
    manager.cache_write("refresh_test", "data")
    manager.cache_refresh("refresh_test")
    assert manager.cache_read("refresh_test") == "data"

@pytest.mark.unit
def test_cache_manager_multi_account():
    """Test multi-account cache support"""
    manager = CacheManager()
    accounts = ["account1", "account2", "account3"]
    for account in accounts:
        manager.cache_write(account, "data")
    for account in accounts:
        assert manager.cache_read(account) == "data"
