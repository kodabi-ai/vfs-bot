import asyncio
from datetime import datetime
from typing import Dict, List, Optional

# Local imports
from src.modules.auth import AuthenticationManager
from src.modules.cache import CacheManager
from src.modules.otp import OTPHandler
from src.modules.api import APIClient
from src.models.account import Account
from src.models.session import Session
from src.models.account import AccountStatus


class AutomationWorker:
    """
    Main automation worker orchestrating all modules
    
    Features:
    - Multi-account batch processing (max 5 concurrent)
    - 15-min cache refresh background task
    - Retry mechanism for failed accounts
    - Real-time status reporting
    - Event logging and error tracking
    """

    def __init__(self):
        """Initialize worker with managers and configuration"""
        self.max_concurrent_accounts = 5
        self.cache_manager = CacheManager()
        self.auth_manager = AuthenticationManager()
        self.otp_handler = OTPHandler()
        self.api_client = APIClient()
        self.accounts: List[Account] = []
        self.failed_accounts: List[str] = []
        self.completed_accounts: List[str] = []
        self.is_running: bool = False

    async def add_account(self, account: Account):
        """Add account for processing"""
        self.accounts.append(account)
        print(f"[WORKER] Added account: {account.id} ({account.email})")

    async def run_batch(self, accounts: Optional[List[Account]] = None):
        """
        Run automation for multiple accounts concurrently
        
        Args:
            accounts: Optional list of accounts, defaults to all registered
        """
        if accounts is None:
            accounts = self.accounts

        self.is_running = True
        tasks = []

        for account in accounts:
            task = asyncio.create_task(
                self._process_account(account)
            )
            tasks.append(task)

            # Rate limiting: max 5 concurrent accounts
            if len(tasks) >= self.max_concurrent_accounts:
                # Wait for at least one task to complete
                done, pending = await asyncio.wait(
                    tasks,
                    return_when=asyncio.FIRST_COMPLETED
                )
                tasks = list(pending)

        # Wait for remaining tasks
        if tasks:
            await asyncio.gather(*tasks)

        self.is_running = False
        print(f"[WORKER] Batch complete: {len(self.completed_accounts)} success, {len(self.failed_accounts)} failed")

    async def _process_account(self, account: Account) -> bool:
        """
        Process single account login and session management
        
        Returns:
            True if successful, False if failed
        """
        try:
            print(f"[WORKER] Processing account: {account.id}")

            # Step 1: Check cache validity
            cached_session = await self.cache_manager.get_or_create(account)

            if cached_session and cached_session.is_valid:
                print(f"[WORKER] Using valid cached session: {account.id}")
                session = cached_session
            else:
                print(f"[WORKER] Cache expired or missing, new login required")

                # Step 2: Authentication
                session = await self.auth_manager.login(account)

                # Step 3: OTP verification
                if not session.tokens.get('otp_verified'):
                    otp_code = await self.otp_handler.get_otp(account, channel="both")
                    if otp_code:
                        verified = await self.otp_handler.verify_otp(account, otp_code)
                        if verified:
                            session.tokens['otp_verified'] = True
                        else:
                            print(f"[WORKER] OTP verification failed for: {account.id}")
                            return False
                    else:
                        print(f"[WORKER] OTP not received for: {account.id}")
                        return False

                # Step 4: Save session to cache
                await self.cache_manager.save_to_json(account, session)

            # Step 5: Start background cache refresh task
            asyncio.create_task(
                self.cache_manager.refresh_every_15_min(account, self.auth_manager)
            )

            # Step 6: Update account status
            self.completed_accounts.append(account.id)
            print(f"[WORKER] Account {account.id} processed successfully")

            return True

        except Exception as e:
            print(f"[WORKER] Account {account.id} failed: {str(e)}")
            self.failed_accounts.append(account.id)
            return False

    async def get_account_status(self, account_id: str) -> AccountStatus:
        """Get status for single account"""
        try:
            cached = await self.cache_manager.get_or_create(self.accounts[0])

            return AccountStatus(
                account_id=account_id,
                status="active" if cached and cached.is_valid else "inactive",
                last_login=datetime.now().isoformat(),
                session_age_seconds=900 - cached.time_remaining if cached else 0,
                otp_channel="email"
            )
        except Exception as e:
            return AccountStatus(
                account_id=account_id,
                status="error",
                last_error=str(e)
            )

    def get_batch_summary(self) -> Dict:
        """Get batch processing summary"""
        return {
            "total": len(self.accounts),
            "completed": len(self.completed_accounts),
            "failed": len(self.failed_accounts),
            "success_rate": len(self.completed_accounts) / len(self.accounts) if self.accounts else 0,
            "completed_accounts": self.completed_accounts,
            "failed_accounts": self.failed_accounts,
            "timestamp": datetime.now().isoformat()
        }

    async def stop(self):
        """Stop worker and cleanup"""
        self.is_running = False
        await self.auth_manager.cache.clear_expired()
        await self.api_client.close()
        print("[WORKER] Worker stopped")


class MultiAccountWorker(AutomationWorker):
    """
    Extended worker for multi-account batch processing
    
    Features:
    - Load accounts from configuration
    - Session cookie sharing across accounts
    - Proxy rotation support
    - Rate limiting by account
    """

    def __init__(self):
        """Initialize multi-account worker"""
        super().__init__()
        self.proxy_rotation_enabled = True
        self.rate_limit_per_account = 5  # requests per minute
        self.cookie_sharing = True

    async def load_accounts_from_config(self, config_file: str) -> List[Account]:
        """Load accounts from configuration file"""
        import json
        with open(config_file, 'r') as f:
            accounts_data = json.load(f)

        accounts = []
        for data in accounts_data:
            account = Account(**data)
            self.accounts.append(account)

        return self.accounts

    async def share_cookies_between_accounts(self, accounts: List[Account]):
        """Share CloudFlare cookies across accounts (V116+ pattern)"""
        if not self.cookie_sharing:
            return

        # Get first account cookies
        if self.accounts:
            first_account = self.accounts[0]
            cookies = await self.auth_manager.browser.context.cookies()

            # Share to other accounts
            for account in accounts[1:]:
                await self.auth_manager.browser.context.add_cookies(cookies)
                print(f"[WORKER] Shared cookies to account: {account.id}")


# Factory function for creating worker
async def create_worker(multi_account: bool = False) -> AutomationWorker:
    """Create and initialize worker instance"""
    if multi_account:
        worker = MultiAccountWorker()
    else:
        worker = AutomationWorker()

    await worker.api_client.initialize()
    return worker
