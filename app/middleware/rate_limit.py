import time
from fastapi import HTTPException

from loguru import logger

from app.services.cache_service import CacheService


class RateLimitMiddleware:
    """Middleware para rate limiting usando Redis."""

    def __init__(self, cache_service: CacheService):
        self.cache = cache_service

    async def check_rate_limit(
        self, user_id: str, endpoint: str, max_requests: int = 10, window: int = 60
    ):
        """Verifica se usuário excedeu rate limit."""
        try:
            current_time = int(time.time())
            window_start = current_time - window

            rate_key = f"rate_limit:{user_id}:{endpoint}"

            # Remove requests antigas
            await self.cache.redis_client.zremrangebyscore(rate_key, 0, window_start)

            # Conta requests na janela atual
            current_requests = await self.cache.redis_client.zcard(rate_key)

            if current_requests >= max_requests:
                raise HTTPException(
                    status_code=429,
                    detail=f"Rate limit exceeded. Max {max_requests} requests per {window} seconds",
                )

            # Adiciona request atual
            await self.cache.redis_client.zadd(
                rate_key, {str(current_time): current_time}
            )
            await self.cache.redis_client.expire(rate_key, window)

            return True

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Erro no rate limiting: {str(e)}")
            return True  # Em caso de erro, permite a request
