from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr


class Account(BaseModel):
    """
    Account model for multi-account support
    Encapsulates credentials, contact info, and status
    """
    id: str = Field(..., description="Unique identifier for the account")
    email: EmailStr = Field(..., description="VFS Global login email")
    password: str = Field(..., description="VFS Global login password")
    phone: str = Field(..., description="Contact phone for Phone OTP")
    
    # Status flags
    is_active: bool = Field(default=True, description="Account active status")
    is_verified: bool = Field(default=False, description="OTP verification status")
    
    # Session tracking
    last_login: Optional[datetime] = Field(default=None, description="Last successful login")
    last_otp: Optional[datetime] = Field(default=None, description="Last OTP timestamp")
    session_active: bool = Field(default=False, description="Current session active")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    
    # Additional fields for extended features
    notes: Optional[str] = Field(default=None, description="Account notes")
    metadata: dict = Field(default_factory=dict, description="Additional metadata")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "acc_001",
                "email": "{{VFS_EMAIL}}",
                "password": "{{VFS_PASSWORD}}",
                "phone": "{{VFS_PHONE}}"
            }
        }


class AccountStatus(BaseModel):
    """
    Account status model for monitoring dashboard
    """
    account_id: str
    status: str  # active, inactive, locked, pending_otp
    last_login: Optional[str] = None
    session_age_seconds: Optional[int] = None
    otp_channel: Optional[str] = None  # email, phone, none
    retry_count: int = 0
    last_error: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "account_id": "acc_001",
                "status": "pending_otp",
                "last_login": "2026-04-18T01:00:00",
                "session_age_seconds": 180,
                "otp_channel": "email"
            }
        }
