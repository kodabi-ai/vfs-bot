import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler

# Create logs directory if not exists
LOGS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "logs")
os.makedirs(LOGS_DIR, exist_ok=True)


def setup_logger(name: str = "vfs-automation", level: int = logging.INFO):
    """
    Setup structured logger for VFS Global automation
    
    Features:
    - Rotating file handler (max 10MB per file)
    - Console and file output
    - Structured JSON logging for async applications
    - Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
    """
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    # Create formatters
    console_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(console_formatter)
    
    # File handler with rotation
    log_file = os.path.join(LOGS_DIR, f"{name}.log")
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(file_formatter)
    
    # Add handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger


# Create default logger instance
logger = setup_logger()


def log_auth_event(account_id: str, event: str, status: str = "success"):
    """
    Log authentication event
    
    Args:
        account_id: Account ID
        event: Event type (login, logout, otp_verify, etc.)
        status: Event status
    """
    logger.info(f"AUTH | account={account_id} | event={event} | status={status}")


def log_otp_event(otp_channel: str, status: str, duration_sec: int = 0):
    """
    Log OTP event
    
    Args:
        otp_channel: Email or Phone
        status: Status (received, failed, timeout)
        duration_sec: Time to receive OTP
    """
    logger.info(f"OTP | channel={otp_channel} | status={status} | duration={duration_sec}s")


def log_cache_event(account_id: str, action: str, duration_sec: int = 0):
    """
    Log cache event
    
    Args:
        account_id: Account ID
        action: Cache action (save, load, refresh, expired)
        duration_sec: Duration in seconds
    """
    logger.info(f"CACHE | account={account_id} | action={action} | duration={duration_sec}s")


def log_browser_event(event: str, page: str = "", duration_sec: int = 0):
    """
    Log browser event
    
    Args:
        event: Browser action (initialized, navigated, clicked, etc.)
        page: Page URL
        duration_sec: Duration in seconds
    """
    logger.info(f"BROWSER | event={event} | page={page} | duration={duration_sec}s")


def log_api_event(endpoint: str, method: str, status_code: int = 0, duration_sec: int = 0):
    """
    Log API event
    
    Args:
        endpoint: API endpoint
        method: HTTP method (GET, POST, PUT, PATCH, DELETE)
        status_code: HTTP status code
        duration_sec: Duration in seconds
    """
    logger.info(f"API | endpoint={endpoint} | method={method} | status={status_code} | duration={duration_sec}s")


def log_error(message: str, error: Exception = None):
    """
    Log error event
    
    Args:
        message: Error message
        error: Exception object (optional)
    """
    logger.error(f"ERROR | message={message}", exc_info=error)


def get_logger(name: str = "vfs-automation") -> logging.Logger:
    """
    Get logger instance
    
    Args:
        name: Logger name
    
    Returns:
        Logger instance
    """
    return setup_logger(name)
