import json
from typing import List, Dict

from loguru import logger

from app.services.cache_service import CacheService


class SessionService(CacheService):
    """Gerenciamento de sessões de chat."""

    async def save_chat_context(
        self, user_id: str, conversation_history: List[Dict], ttl: int = 7200
    ):
        """Salva contexto da conversa do usuário."""
        try:
            session_key = f"session:{user_id}"
            await self.redis_client.setex(
                session_key, ttl, json.dumps(conversation_history)
            )
            logger.info(f"💬 Contexto salvo para usuário: {user_id}")
        except Exception as e:
            logger.error(f"Erro ao salvar contexto: {str(e)}")

    async def get_chat_context(self, user_id: str) -> List[Dict]:
        """Recupera contexto da conversa."""
        try:
            session_key = f"session:{user_id}"
            context_data = await self.redis_client.get(session_key)

            if context_data:
                return json.loads(context_data)
            return []
        except Exception as e:
            logger.error(f"Erro ao recuperar contexto: {str(e)}")
            return []

    async def update_user_activity(self, user_id: str):
        """Atualiza timestamp da última atividade."""
        try:
            activity_key = f"activity:{user_id}"
            await self.redis_client.setex(activity_key, 1800, "active")  # 30min TTL
        except Exception as e:
            logger.error(f"Erro ao atualizar atividade: {str(e)}")
