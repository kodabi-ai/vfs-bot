import logging
import re
import hashlib
from typing import Dict, Optional

class AuthenticationManager:
    """Authentication Manager for VFS Global login"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def validate_email(self, email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def validate_phone(self, phone: str) -> bool:
        """Validate phone format"""
        pattern = r'^\d{10}$'
        return bool(re.match(pattern, phone))
    
    def validate_credentials(self, creds: Dict) -> bool:
        """Validate login credentials"""
        email_valid = self.validate_email(creds.get('email', ''))
        password_valid = len(creds.get('password', '')) > 5
        return email_valid and password_valid
    
    def generate_token(self, user: str) -> str:
        """Generate authentication token"""
        return hashlib.sha256(user.encode()).hexdigest()[:32]
