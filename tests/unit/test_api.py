import pytest
from src.modules.api import APIClient

@pytest.mark.unit
def test_api_client_initialization():
    """Test API Client initialization"""
    client = APIClient()
    assert client is not None

@pytest.mark.unit
def test_api_client_headers():
    """Test API header configuration"""
    client = APIClient()
    headers = client.get_headers()
    assert headers.get('Content-Type') == 'application/json'

@pytest.mark.unit
def test_api_client_retry_mechanism():
    """Test API retry mechanism"""
    client = APIClient()
    client.set_retry_count(3)
    assert client.get_retry_count() == 3

@pytest.mark.unit
def test_api_client_timeout():
    """Test API timeout configuration"""
    client = APIClient()
    client.set_timeout(300)
    assert client.get_timeout() == 300

@pytest.mark.unit
def test_api_client_session():
    """Test API session management"""
    client = APIClient()
    session = client.get_session()
    assert session is not None
