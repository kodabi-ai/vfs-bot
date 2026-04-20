"""VFS Global Modules Package"""

from src.modules.auth import AuthenticationManager
from src.modules.browser import BrowserManager
from src.modules.cache import CacheManager
from src.modules.otp import OTPHandler
from src.modules.api import APIClient, VFSAPIEndpoints

__all__ = [
    "AuthenticationManager",
    "BrowserManager",
    "CacheManager",
    "OTPHandler",
    "APIClient",
    "VFSAPIEndpoints",
]