import pytest
from src.modules.auth import AuthenticationManager
from src.modules.browser import BrowserManager
from src.modules.cache import CacheManager
from src.modules.otp import OTPHandler
from src.modules.api import APIClient
from src.modules.worker import AutomationWorker

@pytest.mark.e2e
def test_full_login_flow():
    """Test complete VFS Global login flow"""
    # Initialize all modules
    auth = AuthenticationManager()
    browser = BrowserManager()
    cache = CacheManager()
    otp = OTPHandler()
    api = APIClient()
    worker = AutomationWorker()
    
    # Validate credentials
    assert auth.validate_email("mustafa.eke@live.com") == True
    assert auth.validate_phone("5468224662") == True
    
    # Check cache
    cache.cache_write("session", "active")
    assert cache.cache_read("session") == "active"
    
    # Check OTP
    assert otp.validate_email_otp("mustafa.eke@live.com") == True
    assert otp.validate_phone_otp("5468224662") == True
    
    # Check API
    assert api.get_headers() is not None
    
    # Check worker
    worker.log_info("Login test")
    assert worker.get_log_count() >= 1

@pytest.mark.e2e
def test_otp_duality():
    """Test dual-channel OTP strategy"""
    handler = OTPHandler()
    result = handler.validate_dual_channel("mustafa.eke@live.com", "5468224662")
    assert result == True

@pytest.mark.e2e
def test_browser_flow():
    """Test browser flow"""
    manager = BrowserManager()
    browser = manager.launch_chromium(headless=True)
    page = manager.new_page()
    assert browser == "chromium_launched"
    assert page == "page_created"
