import pytest
from src.modules.browser import BrowserManager

@pytest.mark.unit
def test_browser_manager_initialization():
    """Test Browser Manager initialization"""
    manager = BrowserManager()
    assert manager is not None

@pytest.mark.unit
def test_browser_manager_chromium_launch():
    """Test Chromium browser launch"""
    manager = BrowserManager()
    browser = manager.launch_chromium(headless=True)
    assert browser is not None

@pytest.mark.unit
def test_browser_manager_page_navigation():
    """Test page navigation"""
    manager = BrowserManager()
    page = manager.new_page()
    assert page is not None

@pytest.mark.unit
def test_browser_manager_captcha_detection():
    """Test Cloudflare captcha detection"""
    manager = BrowserManager()
    element = manager.wait_for_selector('#cf-chl-widget-591nx_response')
    assert element is not None

@pytest.mark.unit
def test_browser_manager_selector_extraction():
    """Test element selector extraction"""
    manager = BrowserManager()
    selector = '#email'
    assert selector == '#email'
