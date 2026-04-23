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
    valid_email = "{{VFS_EMAIL}}"
    assert manager.validate_email(valid_email) == True

@pytest.mark.unit
def test_auth_manager_phone_format():
    """Test phone format validation"""
    manager = AuthenticationManager()
    valid_phone = "{{VFS_PHONE}}"
    assert manager.validate_phone(valid_phone) == True

@pytest.mark.unit
def test_auth_manager_login_credentials():
    """Test login credential validation"""
    manager = AuthenticationManager()
    creds = {
        "email": "{{VFS_EMAIL}}",
        "password": "{{VFS_PASSWORD}}"
    }
    assert manager.validate_credentials(creds) == True

@pytest.mark.unit
def test_auth_manager_token_generation():
    """Test authentication token generation"""
    manager = AuthenticationManager()
    token = manager.generate_token("{{VFS_EMAIL}}")
    assert token is not None
    assert len(token) > 10
