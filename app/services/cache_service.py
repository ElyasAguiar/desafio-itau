import json
import hashlib
from typing import Optional
import redis.asyncio as redis
from loguru import logger
from app.core.config import settings


class CacheService:
    """Serviço de cache usando Redis."""

    def __init__(self):
        self.redis_client = None

    async def connect(self):
        """Conecta ao Redis."""
        try:
            self.redis_client = redis.Redis.from_url(
                settings.REDIS_URL or "redis://redis:6379", decode_responses=True
            )
            await self.redis_client.ping()
            logger.info("✅ Redis conectado com sucesso!")
            return True
        except Exception as e:
            logger.error(f"❌ Erro ao conectar ao Redis: {str(e)}")
            return False

    def _generate_cache_key(self, prompt: str, model: str, user_id: str = None) -> str:
        """Gera chave única para o cache baseada no prompt e modelo."""
        content = f"{prompt}:{model}"
        if user_id:
            content += f":{user_id}"
        return f"llm_cache:{hashlib.md5(content.encode()).hexdigest()}"

    async def get_cached_response(
        self, prompt: str, model: str, user_id: str = None
    ) -> Optional[dict]:
        """Busca resposta em cache."""
        try:
            if not self.redis_client:
                await self.connect()

            cache_key = self._generate_cache_key(prompt, model, user_id)
            cached_data = await self.redis_client.get(cache_key)

            if cached_data:
                logger.info(f"💾 Cache hit para prompt: {prompt[:50]}...")
                return json.loads(cached_data)

            return None
        except Exception as e:
            logger.error(f"Erro ao buscar cache: {str(e)}")
            return None

    async def cache_response(
        self,
        prompt: str,
        model: str,
        response: dict,
        ttl: int = 3600,
        user_id: str = None,
    ):
        """Salva resposta no cache."""
        try:
            if not self.redis_client:
                await self.connect()

            cache_key = self._generate_cache_key(prompt, model, user_id)
            await self.redis_client.setex(cache_key, ttl, json.dumps(response))
            logger.info(f"💾 Resposta cacheada para: {prompt[:50]}...")
        except Exception as e:
            logger.error(f"Erro ao salvar cache: {str(e)}")
