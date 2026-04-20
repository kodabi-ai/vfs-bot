import pytest
from src.modules.otp import OTPHandler

@pytest.mark.unit
def test_otp_handler_initialization():
    """Test OTP Handler initialization"""
    handler = OTPHandler()
    assert handler is not None

@pytest.mark.unit
def test_otp_email_channel():
    """Test email OTP channel"""
    handler = OTPHandler()
    result = handler.validate_email_otp("mustafa.eke@live.com")
    assert result == True

@pytest.mark.unit
def test_otp_phone_channel():
    """Test phone OTP channel"""
    handler = OTPHandler()
    result = handler.validate_phone_otp("5468224662")
    assert result == True

@pytest.mark.unit
def test_otp_dual_channel():
    """Test dual channel OTP strategy"""
    handler = OTPHandler()
    result = handler.validate_dual_channel("mustafa.eke@live.com", "5468224662")
    assert result == True

@pytest.mark.unit
def test_otp_retry_mechanism():
    """Test OTP retry mechanism"""
    handler = OTPHandler()
    attempts = handler.get_retry_attempts()
    assert attempts == 3
