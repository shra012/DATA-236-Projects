from __future__ import annotations

from datetime import datetime, timezone
from typing import List

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas
from .gemini import generate_gemini_completion


class ConversationService:
  def __init__(self, db: Session):
    self.db = db

  def list_conversations_for_user(self, user_id: str) -> List[models.Conversation]:
    return (
      self.db.query(models.Conversation)
      .filter(models.Conversation.user_id == user_id)
      .order_by(models.Conversation.updated_at.desc(), models.Conversation.created_at.desc())
      .all()
    )

  def list_user_handles(self) -> List[str]:
    records = self.db.query(models.Conversation.user_id).distinct().all()
    return [record[0] for record in records]

  def fetch_conversation_messages(self, conversation_id: int, user_id: str) -> schemas.MessagesOut:
    conversation = (
      self.db.query(models.Conversation)
      .filter(models.Conversation.id == conversation_id, models.Conversation.user_id == user_id)
      .first()
    )
    if not conversation:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")

    messages = (
      self.db.query(models.Message)
      .filter(models.Message.conversation_id == conversation_id)
      .order_by(models.Message.id.asc())
      .all()
    )
    return schemas.MessagesOut(conversation_id=conversation_id, messages=messages)

  async def send_fixed_response(self, payload: schemas.ChatIn) -> schemas.ChatOut:
    conversation = self._get_or_create_conversation(payload)

    user_message = self._create_message(conversation.id, models.MessageRole.USER, payload.message)
    history = self._history_for_conversation(conversation.id)
    reply = await generate_gemini_completion(history)

    self._create_message(conversation.id, models.MessageRole.ASSISTANT, reply)
    self._touch_conversation(conversation)

    self.db.commit()

    return schemas.ChatOut(conversation_id=conversation.id, reply=reply)

  def _get_or_create_conversation(self, payload: schemas.ChatIn) -> models.Conversation:
    if payload.conversation_id:
      conversation = (
        self.db.query(models.Conversation)
        .filter(
          models.Conversation.id == payload.conversation_id,
          models.Conversation.user_id == payload.user_id,
        )
        .first()
      )
      if not conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")

      if payload.title and not conversation.title:
        conversation.title = payload.title

      if conversation.ai_provider != models.AIProvider.GEMINI:
        conversation.ai_provider = models.AIProvider.GEMINI

      return conversation

    conversation = models.Conversation(
      user_id=payload.user_id,
      title=payload.title or payload.message[:80],
      ai_provider=payload.ai_provider or models.AIProvider.GEMINI,
    )

    self.db.add(conversation)
    self.db.flush()
    return conversation

  def _history_for_conversation(self, conversation_id: int) -> List[Dict[str, str]]:
    messages = (
      self.db.query(models.Message)
      .filter(models.Message.conversation_id == conversation_id)
      .order_by(models.Message.id.asc())
      .all()
    )
    return [{"role": message.role.value, "content": message.content} for message in messages]

  def _create_message(
    self,
    conversation_id: int,
    role: models.MessageRole,
    content: str,
    *,
    commit: bool = False,
  ) -> models.Message:
    message = models.Message(conversation_id=conversation_id, role=role, content=content)
    self.db.add(message)
    if commit:
      self.db.commit()
      self.db.refresh(message)
    else:
      self.db.flush()
    return message

  def _touch_conversation(self, conversation: models.Conversation) -> None:
    conversation.updated_at = datetime.now(timezone.utc)
