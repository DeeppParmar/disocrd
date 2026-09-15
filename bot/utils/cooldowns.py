"""Distributed cooldown manager."""
import time
import structlog

logger = structlog.get_logger(__name__)

class CooldownManager:
    __slots__ = ("_redis", "_fallback")

    def __init__(self, redis_client=None) -> None:
        self._redis = redis_client
        self._fallback: dict[str, float] = {}

    def _get_key(self, key: str, user_id: int) -> str:
        return f"cd:{key}:{user_id}"

    async def is_on_cooldown(self, key: str, user_id: int) -> bool:
        cd_key = self._get_key(key, user_id)
        
        if self._redis:
            try:
                # Assuming upstash-redis async client
                ttl = await self._redis.ttl(cd_key)
                return ttl > 0
            except Exception as e:
                logger.error("Redis connection error", error=str(e))
        
        # Fallback
        expiry = self._fallback.get(cd_key, 0)
        if time.time() < expiry:
            return True
        if cd_key in self._fallback:
            del self._fallback[cd_key]
        return False

    async def set_cooldown(self, key: str, user_id: int, seconds: int) -> None:
        cd_key = self._get_key(key, user_id)
        
        if self._redis:
            try:
                await self._redis.set(cd_key, "1", ex=seconds)
                return
            except Exception as e:
                logger.error("Redis connection error", error=str(e))
        
        # Fallback
        self._fallback[cd_key] = time.time() + seconds

    async def get_remaining(self, key: str, user_id: int) -> float:
        cd_key = self._get_key(key, user_id)
        
        if self._redis:
            try:
                ttl = await self._redis.ttl(cd_key)
                return max(0.0, float(ttl))
            except Exception as e:
                logger.error("Redis connection error", error=str(e))
        
        # Fallback
        expiry = self._fallback.get(cd_key, 0)
        remaining = expiry - time.time()
        return max(0.0, remaining)
