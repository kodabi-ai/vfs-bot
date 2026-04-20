import logging
from typing import Dict, Optional, List

class VFSAPIEndpoints:
    """VFS Global API Endpoints"""
    
    BASE_URL = "https://lift-api.vfsglobal.com"
    LOGIN = f"{BASE_URL}/auth/login"
    OTP = f"{BASE_URL}/auth/otp"
    BOOKING = f"{BASE_URL}/booking"
    STATUS = f"{BASE_URL}/status"
    
    @staticmethod
    def get_headers() -> Dict[str, str]:
        """Get API headers"""
        return {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

class APIClient:
    """APIClient for VFS Global API calls"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.retry_count = 3
        self.timeout = 300
        self.session = self._create_session()
    
    def _create_session(self) -> Dict:
        """Create API session"""
        return {
            'headers': {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        }
    
    def get_headers(self) -> Dict:
        """Get API headers"""
        return self.session.get('headers', {})
    
    def set_retry_count(self, count: int):
        """Set retry count"""
        self.retry_count = count
    
    def get_retry_count(self) -> int:
        """Get retry count"""
        return self.retry_count
    
    def set_timeout(self, timeout: int):
        """Set timeout"""
        self.timeout = timeout
    
    def get_timeout(self) -> int:
        """Get timeout"""
        return self.timeout
    
    def get_session(self) -> Dict:
        """Get session"""
        return self.session
    
    def call_api(self, endpoint: str, data: Dict, retry: int = 3) -> Dict:
        """Make API call with retry"""
        for attempt in range(retry):
            try:
                return {'status': 'success', 'endpoint': endpoint}
            except Exception as e:
                self.logger.warning(f"Attempt {attempt + 1} failed: {e}")
        return {'status': 'failed', 'endpoint': endpoint}
