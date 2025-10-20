from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import schemas
from ..database import get_db
from ..services.chat_service import ConversationService

router = APIRouter(prefix="/api/v1/conversations", tags=["conversations"])


def get_conversation_service(db: Session = Depends(get_db)) -> ConversationService:
  return ConversationService(db)


@router.post("/messages", response_model=schemas.ChatOut, status_code=201)
async def create_message(payload: schemas.ChatIn, service: ConversationService = Depends(get_conversation_service)):
  return await service.send_fixed_response(payload)


@router.get("", response_model=List[schemas.ConversationOut])
def list_conversations(user_id: str, service: ConversationService = Depends(get_conversation_service)):
  return service.list_conversations_for_user(user_id)


@router.get("/users", response_model=List[str])
def list_users(service: ConversationService = Depends(get_conversation_service)):
  return service.list_user_handles()


@router.get("/{conversation_id}/messages", response_model=schemas.MessagesOut)
def list_messages(conversation_id: int, user_id: str, service: ConversationService = Depends(get_conversation_service)):
  return service.fetch_conversation_messages(conversation_id, user_id)
