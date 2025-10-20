from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class RoleEnum(str, Enum):
    user = "user"
    assistant = "assistant"


class ScopeEnum(str, Enum):
    session = "session"
    user = "user"


class Message(BaseModel):
    user_id: str
    session_id: str
    role: RoleEnum
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class MessageInDB(Message):
    id: Optional[str] = Field(None, alias="_id")


class Summary(BaseModel):
    user_id: str
    session_id: Optional[str] = None
    scope: ScopeEnum
    text: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class SummaryInDB(Summary):
    id: Optional[str] = Field(None, alias="_id")


class Episode(BaseModel):
    user_id: str
    session_id: str
    fact: str
    importance: float = Field(ge=0.0, le=1.0)
    embedding: List[float]
    created_at: datetime = Field(default_factory=datetime.utcnow)


class EpisodeInDB(Episode):
    id: Optional[str] = Field(None, alias="_id")


class ChatRequest(BaseModel):
    user_id: str
    session_id: Optional[str] = "default"
    message: str


class MemoryContext(BaseModel):
    short_term_count: int
    short_term_messages: List[Dict[str, Any]]
    long_term_summary: Optional[str] = None
    episodic_facts: List[str] = []


class ChatResponse(BaseModel):
    reply: str
    memory_context: MemoryContext


class MemoryView(BaseModel):
    user_id: str
    recent_messages: List[Dict[str, Any]]
    session_summary: Optional[str] = None
    lifetime_summary: Optional[str] = None
    episodic_facts: List[str] = []


class DailyMessageCount(BaseModel):
    date: str
    count: int


class AggregateView(BaseModel):
    user_id: str
    daily_message_counts: List[DailyMessageCount]
    recent_summaries: List[Dict[str, Any]]
