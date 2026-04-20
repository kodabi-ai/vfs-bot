from datetime import datetime
from typing import Optional, Dict, List
from pydantic import BaseModel, Field


class Session(BaseModel):
    """
    Session model for managing user authentication state
    Encapsulates cookies, tokens, expiry, and account reference
    """
    account_id: str = Field(..., description="Account ID reference")
    cookies: List[Dict] = Field(default=[], description="Browser cookies")
    tokens: Dict = Field(default={}, description="API tokens")
    created_at: datetime = Field(..., description="Session creation timestamp")
    expires_at: float = Field(..., description="Epoch timestamp of session expiry")
    
    # Session metadata
    user_agent: Optional[str] = Field(default=None, description="Browser user agent")
    ip_address: Optional[str] = Field(default=None, description="IP address used")
    cloudflare_tokens: Dict = Field(default={}, description="CloudFlare __cf_bm/__cfuvid")
    
    # Tracking
    total_retries: int = Field(default=0, description="Total login attempts")
    last_success: Optional[datetime] = Field(default=None, description="Last successful login")
    last_error: Optional[str] = Field(default=None, description="Last error message")
    
    @property
    def is_valid(self) -> bool:
        """Check if session is still valid (not expired)"""
        current_time = datetime.now().timestamp()
        return current_time < self.expires_at
    
    @property
    def time_remaining(self) -> int:
        """Get seconds until session expires"""
        current_time = datetime.now().timestamp()
        return int(self.expires_at - current_time)
    
    class Config:
        json_schema_extra = {
            "example": {
                "account_id": "acc_001",
                "cookies": [],
                "tokens": {},
                "created_at": "2026-04-18T01:45:00",
                "expires_at": 1745000700  # epoch timestamp
            }
        }


class SessionStatus(BaseModel):
    """
    Session status model for monitoring dashboard
    """
    account_id: str
    is_valid: bool
    time_remaining_seconds: Optional[int] = None
    cookies_count: int = 0
    tokens_count: int = 0
    cloudflare_tokens_present: bool = False
    last_success: Optional[str] = None
    last_error: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "account_id": "acc_001",
                "is_valid": True,
                "time_remaining_seconds": 840,
                "cookies_count": 5,
                "tokens_count": 2,
                "cloudflare_tokens_present": True,
                "last_success": "2026-04-18T01:30:00",
                "last_error": None
            }
        }
