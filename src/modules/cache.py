import logging
import time
from typing import Dict, Any

class CacheManager:
    """Cache Manager for VFS Global session caching"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.cache: Dict[str, Any] = {}
        self.cache_ttl = 900  # 15 minutes in seconds
    
    def cache_write(self, key: str, value: Any):
        """Write to cache with timestamp"""
        self.cache[key] = {
            'value': value,
            'timestamp': time.time()
        }
    
    def cache_read(self, key: str) -> Any:
        """Read from cache if not expired"""
        if key in self.cache:
            data = self.cache[key]
            if time.time() - data['timestamp'] < self.cache_ttl:
                return data['value']
        return None
    
    def cache_refresh(self, key: str):
        """Refresh cache timestamp"""
        if key in self.cache:
            self.cache[key]['timestamp'] = time.time()
    
    def get_cache_expiry(self) -> int:
        """Get cache expiry in seconds"""
        return self.cache_ttl
    
    def multi_account_cache(self, accounts: list) -> Dict[str, Any]:
        """Cache multiple accounts"""
        for account in accounts:
            self.cache_write(account, f"data_{account}")
        return self.cache
