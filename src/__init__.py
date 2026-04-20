"""VFS Global Visa Automation Package"""

from src.utils.logger import setup_logger, logger
from src.models.account import Account, AccountStatus
from src.models.session import Session, SessionStatus
from src.modules.auth import AuthenticationManager
from src.modules.browser import BrowserManager
from src.modules.cache import CacheManager
from src.modules.otp import OTPHandler
from src.modules.api import APIClient, VFSAPIEndpoints
from src.workers.automation import AutomationWorker, MultiAccountWorker, create_worker

__version__ = "1.0.0"
__author__ = "Kodabi Vize Otomasyonu Team"

__all__ = [
    "Account",
    "AccountStatus",
    "Session",
    "SessionStatus",
    "AuthenticationManager",
    "BrowserManager",
    "CacheManager",
    "OTPHandler",
    "APIClient",
    "VFSAPIEndpoints",
    "AutomationWorker",
    "MultiAccountWorker",
    "create_worker",
    "logger",
    "setup_logger",
]