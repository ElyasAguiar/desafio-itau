"""Request module for chat streaming API."""

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    userId: str = Field(..., min_length=1)
    prompt: str = Field(..., min_length=1)


class ChatResponse(BaseModel):
    id: str
    userId: str
    prompt: str
    response: str
    model: str
    timestamp: str
