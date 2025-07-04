from .models import ChatRequest, ChatResponse
from app.services.llm_service import OpenAIClient


class ChatService:
    """Service for chat API."""

    async def chat_service(self, chat_request: ChatRequest) -> dict:
        """Chat service."""
        client = OpenAIClient()
        response = await client.get_chat_completions(chat_request.prompt)
        return response
