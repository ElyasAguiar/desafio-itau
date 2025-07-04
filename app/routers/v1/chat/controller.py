from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from fastapi_utils.cbv import cbv
import uuid
from datetime import datetime

from .models import ChatRequest, ChatResponse
from .service import ChatService

router = APIRouter()


def common_dependency():
    """Common dependency."""
    return {"msg": "This is a dependency"}


@cbv(router)
class ChatRoute:
    """Chat-related routes."""

    def __init__(self, common_dep=Depends(common_dependency)):
        self.common_dep = common_dep
        self.service = ChatService()

    @router.post("/chat", response_model=ChatResponse)
    async def chat_endpoint(self, request: Request, chat_request: ChatRequest):
        # Gera ID e timestamp
        chat_id = str(uuid.uuid4())
        now = datetime.now()
        # Chama LLM (OpenAI)
        llm_response = await self.service.chat_service(chat_request)
        chat_response = ChatResponse(
            id=chat_id,
            userId=chat_request.userId,
            prompt=chat_request.prompt,
            response=llm_response.get("content", ""),
            model=llm_response.get("model", ""),
            timestamp=now.isoformat(),
        )

        # Retorna resposta
        return chat_response
