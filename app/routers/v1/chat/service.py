from .models import ChatRequest, ChatResponse
from app.services.llm_service import OpenAIClient
from app.services.db_service import MongoDBService


class ChatService:
    """Service for chat API."""

    def __init__(self):
        """Initialize the chat service."""
        self.db_service = MongoDBService()

    async def chat_service(self, chat_request: ChatRequest) -> dict:
        """Chat service."""
        client = OpenAIClient()
        response = await client.get_chat_completions(chat_request.prompt)
        return response

    async def save_chat(self, chat_data: dict) -> bool:
        """Save chat to database."""
        return await self.db_service.save_chat_interaction(chat_data)
