from pydantic_settings import BaseSettings
from typing import Optional


class Config(BaseSettings):
    """
    Centralized configuration for VFS Global automation
    Uses Pydantic Settings for type-safe environment variable management
    """
    
    # ===== Account Credentials (Secrets) =====
    VFS_EMAIL: str
    VFS_PASSWORD: str
    VFS_PHONE: str
    
    # ===== IMAP Configuration =====
    IMAP_EMAIL: str = ""
    IMAP_PASSWORD: str = ""
    IMAP_SERVER: str = "outlook.office365.com"
    IMAP_PORT: int = 993
    
    # ===== API Configuration =====
    VFS_API_URL: str = "https://lift-api.vfsglobal.com"
    API_TIMEOUT: int = 30
    
    # ===== Cache Configuration =====
    CACHE_DURATION_SEC: int = 900  # 15 minutes
    
    # ===== Retry Configuration =====
    MAX_RETRIES: int = 3
    
    # ===== Logging Configuration =====
    LOG_LEVEL: str = "INFO"
    
    # ===== Browser Configuration =====
    BROWSER_HEADLESS: bool = True
    BROWSER_TIMEOUT: int = 30000  # 30 seconds
    
    # ===== Account Limits =====
    MAX_CONCURRENT_ACCOUNTS: int = 5
    RATE_LIMIT_PER_ACCOUNT: int = 5
    
    # ===== Proxy Configuration =====
    PROXY_ENABLED: bool = False
    PROXY_URL: Optional[str] = None
    
    # ===== Multi-Account =====
    MULTI_ACCOUNT_ENABLED: bool = False
    ACCOUNT_CONFIG_FILE: str = "/app/data/accounts.json"
    
    # ===== CloudFlare Specific =====
    CLOUDFLARE_TOKENS_REFRESH: int = 900  # Refresh tokens every 15 min
    CLOUDFLARE_WAITING_ROOM_TIMEOUT: int = 30  # Wait 30s for waiting room
    
    # ===== OTP Timing =====
    OTP_POLL_INTERVAL_SEC: int = 5
    OTP_TIMEOUT_SEC: int = 300  # 5 minutes max
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"


# Create global config instance
config = Config()


def get_config() -> Config:
    """Get global config instance"""
    return config
