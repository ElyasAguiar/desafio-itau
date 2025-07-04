import time
from enum import Enum

from loguru import logger

from app.services.cache_service import CacheService


class CircuitState(Enum):
    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Circuit is open, calls fail fast
    HALF_OPEN = "half_open"  # Testing if service is back


class CircuitBreaker(CacheService):
    """Circuit Breaker para serviços externos."""

    def __init__(
        self, service_name: str, failure_threshold: int = 5, recovery_timeout: int = 60
    ):
        super().__init__()
        self.service_name = service_name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout

    async def get_circuit_state(self) -> CircuitState:
        """Obtém estado atual do circuit breaker."""
        try:
            state_key = f"circuit:{self.service_name}:state"
            state = await self.redis_client.get(state_key)

            if not state:
                return CircuitState.CLOSED

            if state == CircuitState.OPEN.value:
                # Verifica se deve tentar half-open
                last_failure_key = f"circuit:{self.service_name}:last_failure"
                last_failure = await self.redis_client.get(last_failure_key)

                if (
                    last_failure
                    and (time.time() - float(last_failure)) > self.recovery_timeout
                ):
                    await self.set_circuit_state(CircuitState.HALF_OPEN)
                    return CircuitState.HALF_OPEN

            return CircuitState(state)
        except:
            return CircuitState.CLOSED

    async def record_success(self):
        """Registra sucesso na operação."""
        try:
            await self.set_circuit_state(CircuitState.CLOSED)
            failure_key = f"circuit:{self.service_name}:failures"
            await self.redis_client.delete(failure_key)
        except Exception as e:
            logger.error(f"Erro ao registrar sucesso: {str(e)}")

    async def record_failure(self):
        """Registra falha na operação."""
        try:
            failure_key = f"circuit:{self.service_name}:failures"
            failures = await self.redis_client.incr(failure_key)
            await self.redis_client.expire(failure_key, 300)  # 5min TTL

            if failures >= self.failure_threshold:
                await self.set_circuit_state(CircuitState.OPEN)
                last_failure_key = f"circuit:{self.service_name}:last_failure"
                await self.redis_client.set(last_failure_key, time.time())
        except Exception as e:
            logger.error(f"Erro ao registrar falha: {str(e)}")

    async def set_circuit_state(self, state: CircuitState):
        """Define estado do circuit breaker."""
        state_key = f"circuit:{self.service_name}:state"
        await self.redis_client.set(state_key, state.value)
