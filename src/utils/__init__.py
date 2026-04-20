"""VFS Global Utils Package"""

from src.utils.logger import setup_logger, logger, get_logger, log_auth_event, log_otp_event

__all__ = [
    "setup_logger",
    "logger",
    "get_logger",
    "log_auth_event",
    "log_otp_event",
]