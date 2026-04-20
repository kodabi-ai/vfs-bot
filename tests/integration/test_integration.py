import pytest
from src.modules.auth import AuthenticationManager
from src.modules.browser import BrowserManager
from src.modules.cache import CacheManager
from src.modules.otp import OTPHandler
from src.modules.api import APIClient
from src.modules.worker import AutomationWorker

@pytest.mark.integration
def test_module_integration():
    """Test module integration"""
    auth = AuthenticationManager()
    browser = BrowserManager()
    cache = CacheManager()
    otp = OTPHandler()
    api = APIClient()
    worker = AutomationWorker()
    
    # Integration: Auth + Browser
    assert auth.validate_email("mustafa.eke@live.com") == True
    assert browser.launch_chromium(headless=True) == "chromium_launched"
    
    # Integration: Cache + API
    cache.cache_write("test", "data")
    assert api.get_headers() is not None
    
    # Integration: OTP + Worker
    assert otp.validate_email_otp("mustafa.eke@live.com") == True
    assert worker.get_status() == "ready"

@pytest.mark.integration
def test_multi_module_workflow():
    """Test multi-module workflow"""
    auth = AuthenticationManager()
    cache = CacheManager()
    otp = OTPHandler()
    
    # Auth -> Cache -> OTP workflow
    auth.validate_credentials({
        'email': 'mustafa.eke@live.com',
        'password': 'Vfsglobal!5561!'
    })
    cache.cache_write("credentials", auth.generate_token("test"))
    otp.validate_dual_channel("mustafa.eke@live.com", "5468224662")
    
    # Verify cache
    assert cache.cache_read("credentials") is not None

@pytest.mark.integration
def test_api_cache_workflow():
    """Test API and Cache workflow"""
    cache = CacheManager()
    api = APIClient()
    
    # Cache session
    cache.cache_write("api_session", api.get_session())
    assert cache.cache_read("api_session") is not None
    
    # Verify API
    assert api.get_headers()['Content-Type'] == 'application/json'
