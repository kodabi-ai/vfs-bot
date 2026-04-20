import pytest
from src.modules.auth import AuthenticationManager

@pytest.mark.unit
def test_auth_manager_initialization():
    """Test Authentication Manager initialization"""
    manager = AuthenticationManager()
    assert manager is not None

@pytest.mark.unit
def test_auth_manager_email_format():
    """Test email format validation"""
    manager = AuthenticationManager()
    valid_email = "mustafa.eke@live.com"
    assert manager.validate_email(valid_email) == True

@pytest.mark.unit
def test_auth_manager_phone_format():
    """Test phone format validation"""
    manager = AuthenticationManager()
    valid_phone = "5468224662"
    assert manager.validate_phone(valid_phone) == True

@pytest.mark.unit
def test_auth_manager_login_credentials():
    """Test login credential validation"""
    manager = AuthenticationManager()
    creds = {
        "email": "mustafa.eke@live.com",
        "password": "Vfsglobal!5561!"
    }
    assert manager.validate_credentials(creds) == True

@pytest.mark.unit
def test_auth_manager_token_generation():
    """Test authentication token generation"""
    manager = AuthenticationManager()
    token = manager.generate_token("mustafa.eke@live.com")
    assert token is not None
    assert len(token) > 10
