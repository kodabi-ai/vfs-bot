import logging
import os
import json
import time
from typing import Dict, Any, Optional

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None

logger = logging.getLogger(__name__)

class CacheManager:
    """Redis-backed Cache Manager for VFS Global session caching.
    Optimized for Docker Swarm & 12-factor apps.
    Falls back to in-memory cache if Redis is unavailable.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        # 12-Factor: Environment Variable Injection
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.cache_ttl = int(os.getenv("CACHE_TTL_SECONDS", "900"))  # 15 mins default
        
        self.client = None
        self.memory_cache: Dict[str, Any] = {}
        
        if REDIS_AVAILABLE:
            try:
                # RAG Best Practice: Explicit Connection Pool
                pool = redis.ConnectionPool.from_url(
                    self.redis_url,
                    socket_timeout=5,
                    socket_connect_timeout=2,
                    max_connections=10
                )
                self.client = redis.Redis(connection_pool=pool)
                self.client.ping()
                self.logger.info("✅ Cache Manager connected to Redis")
            except (redis.ConnectionError, Exception) as e:
                self.logger.warning(f"⚠️ Redis connection failed, fallback to memory cache: {e}")
                self.client = None
        else:
            self.logger.warning("⚠️ Redis package not installed, using memory cache")
            
    def cache_write(self, key: str, value: Any) -> bool:
        """Write to Redis cache with TTL"""
        try:
            if self.client:
                self.client.setex(key, self.cache_ttl, json.dumps(value))
                return True
            else:
                self.memory_cache[key] = {'value': value, 'timestamp': time.time()}
                return True
        except Exception as e:
            self.logger.error(f"❌ Cache write failed: {e}")
            return False
            
    def cache_read(self, key: str) -> Any:
        """Read from Redis cache"""
        try:
            if self.client:
                data = self.client.get(key)
                if data:
                    return json.loads(data)
                return None
            else:
                if key in self.memory_cache:
                    item = self.memory_cache[key]
                    if time.time() - item.get('timestamp', 0) < self.cache_ttl:
                        return item['value']
                return None
        except Exception as e:
            self.logger.error(f"❌ Cache read failed: {e}")
            return None
            
    def cache_refresh(self, key: str) -> bool:
        """Refresh cache TTL"""
        try:
            if self.client:
                return self.client.expire(key, self.cache_ttl)
            else:
                if key in self.memory_cache:
                    self.memory_cache[key]['timestamp'] = time.time()
                return True
        except Exception as e:
            self.logger.error(f"❌ Cache refresh failed: {e}")
            return False
            
    def multi_account_cache(self, accounts: list) -> Dict[str, Any]:
        """Cache multiple accounts concurrently"""
        results = {}
        for account in accounts:
            account_data = f"session_data_{account}"
            self.cache_write(account, account_data)
            results[account] = account_data
        return results
        
    def close(self):
        """Gracefully close Redis connection"""
        if self.client:
            self.client.close()
