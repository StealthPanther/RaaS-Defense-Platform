"""
Redis Caching Service
"""
import redis
import json
from typing import Optional, Any
from app.config import settings
from loguru import logger


class CacheService:
    """Redis caching service wrapper"""
    
    def __init__(self):
        """Initialize Redis connection"""
        try:
            self.redis_client = redis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                socket_connect_timeout=5
            )
            # Test connection
            self.redis_client.ping()
            logger.info(f"✅ Redis connected: {settings.REDIS_URL}")
        except Exception as e:
            logger.error(f"❌ Redis connection failed: {e}")
            self.redis_client = None
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.redis_client:
            return None
        
        try:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            return None
    
    def set(self, key: str, value: Any, expire: int = 3600) -> bool:
        """
        Set value in cache
        Args:
            key: Cache key
            value: Value to cache (will be JSON serialized)
            expire: TTL in seconds (default: 1 hour)
        """
        if not self.redis_client:
            return False
        
        try:
            self.redis_client.setex(
                key,
                expire,
                json.dumps(value)
            )
            return True
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if not self.redis_client:
            return False
        
        try:
            self.redis_client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            return False
    
    def clear_pattern(self, pattern: str) -> int:
        """
        Delete all keys matching pattern
        Example: clear_pattern("analyze:*")
        """
        if not self.redis_client:
            return 0
        
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Cache clear pattern error for {pattern}: {e}")
            return 0
    
    def health_check(self) -> bool:
        """Check if Redis is healthy"""
        try:
            return self.redis_client.ping() if self.redis_client else False
        except:
            return False


# Global cache instance
cache = CacheService()
