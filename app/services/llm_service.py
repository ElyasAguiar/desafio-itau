from openai import AsyncOpenAI, OpenAIError
from app.core.config import settings
from app.services.cache_service import CacheService
from app.services.circuit_breaker import CircuitBreaker, CircuitState


class OpenAIClient:
    """Cliente para interagir com a API da OpenAI com cache e circuit breaker."""

    def __init__(
        self, api_key: str = settings.OPENAI_API_KEY, model: str = "gpt-4o-mini"
    ):
        self.api_key = api_key
        self.model = model
        self.client = AsyncOpenAI(api_key=self.api_key, max_retries=3)
        self.cache = CacheService()
        self.circuit_breaker = CircuitBreaker("openai_api")

    async def get_chat_completions(self, message: str, user_id: str = None) -> dict:
        # 1. Verifica cache primeiro
        cached_response = await self.cache.get_cached_response(
            message, self.model, user_id
        )
        if cached_response:
            return cached_response

        # 2. Verifica circuit breaker
        circuit_state = await self.circuit_breaker.get_circuit_state()

        if circuit_state == CircuitState.OPEN:
            return {
                "content": "Serviço temporariamente indisponível. Tente novamente em alguns minutos.",
                "model": self.model,
                "from_cache": False,
                "circuit_open": True,
            }

        # 3. Tenta chamar a API
        try:
            response = await self.client.chat.completions.create(
                model=self.model, messages=[{"role": "user", "content": message}]
            )

            result = {
                "content": response.choices[0].message.content,
                "model": response.model,
                "from_cache": False,
                "circuit_open": False,
            }

            # 4. Sucesso: salva no cache e registra no circuit breaker
            await self.cache.cache_response(
                message, self.model, result, user_id=user_id
            )
            await self.circuit_breaker.record_success()

            return result

        except OpenAIError as e:
            await self.circuit_breaker.record_failure()
            return {
                "content": f"Erro ao conectar com a OpenAI: {str(e)}",
                "model": self.model,
                "from_cache": False,
                "circuit_open": False,
            }
        except Exception as e:
            await self.circuit_breaker.record_failure()
            return {
                "content": f"Erro inesperado: {str(e)}",
                "model": self.model,
                "from_cache": False,
                "circuit_open": False,
            }
