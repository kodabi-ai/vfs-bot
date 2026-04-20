import pytest
import time
from src.modules.cache import CacheManager
from src.modules.otp import OTPHandler
from src.modules.worker import AutomationWorker

@pytest.mark.performance
def test_cache_performance():
    """Test cache performance with multiple operations"""
    cache = CacheManager()
    start = time.time()
    for i in range(100):
        cache.cache_write(f"key_{i}", f"value_{i}")
        cache.cache_read(f"key_{i}")
    elapsed = time.time() - start
    assert elapsed < 1.0  # Should complete in under 1 second

@pytest.mark.performance
def test_otp_handler_performance():
    """Test OTP handler response time"""
    handler = OTPHandler()
    start = time.time()
    handler.validate_email_otp("mustafa.eke@live.com")
    handler.validate_phone_otp("5468224662")
    elapsed = time.time() - start
    assert elapsed < 0.5  # Should complete in under 0.5 seconds

@pytest.mark.performance
def test_worker_batch_performance():
    """Test worker batch processing performance"""
    worker = AutomationWorker()
    accounts = [{"email": f"user{i}@example.com", "phone": f"546822466{i}"} for i in range(10)]
    start = time.time()
    result = worker.process_batch(accounts)
    elapsed = time.time() - start
    assert result["successful"] == 10
    assert elapsed < 1.0  # Should complete in under 1 second

@pytest.mark.performance
def test_api_performance():
    """Test API client performance"""
    from src.modules.api import APIClient
    client = APIClient()
    start = time.time()
    for _ in range(10):
        client.call_api("https://test.example.com", {"test": "data"})
    elapsed = time.time() - start
    assert elapsed < 1.0  # Should complete in under 1 second
