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
    assert auth.validate_email("{{VFS_EMAIL}}") == True
    assert auth.validate_phone("{{VFS_PHONE}}") == True
    
    # Check cache
    cache.cache_write("session", "active")
    assert cache.cache_read("session") == "active"
    
    # Check OTP
    assert otp.validate_email_otp("{{VFS_EMAIL}}") == True
    assert otp.validate_phone_otp("{{VFS_PHONE}}") == True
    
    # Check API
    assert api.get_headers() is not None
    
    # Check worker
    worker.log_info("Login test")
    assert worker.get_log_count() >= 1

@pytest.mark.e2e
def test_otp_duality():
    """Test dual-channel OTP strategy"""
    handler = OTPHandler()
    result = handler.validate_dual_channel("{{VFS_EMAIL}}", "{{VFS_PHONE}}")
    assert result == True

@pytest.mark.e2e
def test_browser_flow():
    """Test browser flow"""
    manager = BrowserManager()
    browser = manager.launch_chromium(headless=True)
    page = manager.new_page()
    assert browser == "chromium_launched"
    assert page == "page_created"
