from enum import Enum as PyEnum

from sqlalchemy import Column, DateTime, Enum as SQLEnum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .database import Base


class AIProvider(str, PyEnum):
    GEMINI = "gemini"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"


class MessageRole(str, PyEnum):
    USER = "user"
    ASSISTANT = "assistant"


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(128), nullable=False, index=True)
    title = Column(String(255))
    ai_provider = Column(
        SQLEnum(AIProvider, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=AIProvider.GEMINI,
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan", order_by="Message.id")


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(SQLEnum(MessageRole, name="message_role"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    conversation = relationship("Conversation", back_populates="messages")
