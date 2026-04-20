"""
VFS Global Visa Automation - FastAPI Entry Point
Centralized configuration via config.py
"""

import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware

# Local imports
from src.config import config, get_config
from src.modules.auth import AuthenticationManager
from src.modules.cache import CacheManager
from src.workers.automation import AutomationWorker, MultiAccountWorker
from src.models.account import Account, AccountStatus
from src.utils.logger import log_auth_event, log_error


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan manager for startup/shutdown
    """
    # Startup
    print("[APP] VFS Global Automation starting...")
    print(f"[APP] VFS Email: {config.VFS_EMAIL}")
    print(f"[APP] Cache Duration: {config.CACHE_DURATION_SEC}s")
    
    yield
    
    # Shutdown
    print("[APP] VFS Global Automation stopping...")


# Create FastAPI application
app = FastAPI(
    title="VFS Global Visa Automation",
    description="Modern VFS Global Portal Automation with CloudFlare Bypass",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "phase": "Phase 3 - Implementation",
        "config": {
            "cache_duration_sec": config.CACHE_DURATION_SEC,
            "max_retries": config.MAX_RETRIES,
            "browser_headless": config.BROWSER_HEADLESS
        }
    }


@app.get("/api/v1/status")
async def get_status():
    """Get system status"""
    return {
        "service": "VFS Global Automation",
        "state": "active",
        "uptime": "00:00:00",
        "version": "1.0.0",
        "bmad_phase": "Phase 4 - Quality"
    }


@app.post("/api/v1/accounts")
async def create_account(account: Account):
    """Create new account"""
    return {
        "message": f"Account created: {account.id}",
        "email": account.email,
        "phone": account.phone
    }


@app.post("/api/v1/accounts/{account_id}/refresh")
async def refresh_account(account_id: str):
    """Refresh session for account"""
    try:
        account = Account(id=account_id, **config.__dict__)
        cache = CacheManager()
        
        # Get cached session
        cached = await cache.get_or_create(account)
        
        if cached and cached.is_valid:
            return {
                "status": "success",
                "message": "Valid session found",
                "expires_in": cached.time_remaining
            }
        else:
            # Refresh session
            auth = AuthenticationManager()
            session = await auth.login(account)
            await cache.save_to_json(account, session)
            
            return {
                "status": "success",
                "message": "Session refreshed",
                "expires_in": 900
            }
    
    except Exception as e:
        log_error(f"Refresh failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/accounts/{account_id}/login")
async def login_account(account_id: str, background_tasks: BackgroundTasks):
    """Execute login flow for account"""
    try:
        account = Account(id=account_id, **config.__dict__)
        worker = await AutomationWorker()
        
        # Run login
        success = await worker._process_account(account)
        
        if success:
            log_auth_event(account_id, "login", "success")
            return {
                "status": "success",
                "message": "Login completed",
                "account_id": account_id
            }
        else:
            log_auth_event(account_id, "login", "failed")
            return {
                "status": "failed",
                "message": "Login failed",
                "account_id": account_id
            }
    
    except Exception as e:
        log_error(f"Login error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/accounts/{account_id}/status")
async def get_account_status(account_id: str) -> AccountStatus:
    """Get account status"""
    try:
        cache = CacheManager()
        account = Account(id=account_id, **config.__dict__)
        
        cached = await cache.get_or_create(account)
        
        return AccountStatus(
            account_id=account_id,
            status="active" if cached and cached.is_valid else "inactive",
            last_login=account.last_login.isoformat() if account.last_login else None,
            session_age_seconds=900 - cached.time_remaining if cached and cached.is_valid else 900,
            otp_channel="email"
        )
    
    except Exception as e:
        return AccountStatus(
            account_id=account_id,
            status="error",
            last_error=str(e)
        )
