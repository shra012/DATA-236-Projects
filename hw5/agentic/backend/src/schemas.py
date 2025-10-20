from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from .models import AIProvider, MessageRole


class ChatIn(BaseModel):
    user_id: str = Field(..., max_length=128)
    message: str = Field(..., min_length=1)
    conversation_id: Optional[int] = None
    title: Optional[str] = Field(default=None, max_length=255)
    ai_provider: Optional[AIProvider] = Field(default=AIProvider.GEMINI)


class ChatOut(BaseModel):
    conversation_id: int
    reply: str


class ConversationOut(BaseModel):
    id: int
    user_id: str
    title: Optional[str] = None
    ai_provider: AIProvider
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ChatMessageOut(BaseModel):
    id: int
    conversation_id: int
    role: MessageRole
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


class MessagesOut(BaseModel):
    conversation_id: int
    messages: List[ChatMessageOut]
