import os
from datetime import datetime, timezone
from typing import AsyncIterator, List
import json

import httpx
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/chat", tags=["chat"])


def get_api_config(provider: models.AIProvider) -> dict:
    if provider == models.AIProvider.OPENAI:
        return {
            "url": "https://api.openai.com/v1/chat/completions",
            "headers": {
                "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
                "Content-Type": "application/json",
            },
            "model": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        }
    return {
        "url": "https://api.anthropic.com/v1/messages",
        "headers": {
            "x-api-key": os.getenv("ANTHROPIC_API_KEY"),
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        },
        "model": os.getenv("ANTHROPIC_MODEL", "claude-3-5-haiku-latest"),
    }


async def stream_response(provider: models.AIProvider, messages: List[dict]) -> AsyncIterator[str]:
    config = get_api_config(provider)
    payload = {"model": config["model"], "messages": messages, "stream": True}
    
    if provider == models.AIProvider.ANTHROPIC:
        payload["max_tokens"] = 4096

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream("POST", config["url"], json=payload, headers=config["headers"]) as response:
                if response.status_code != 200:
                    error = await response.aread()
                    raise HTTPException(status_code=502, detail=f"API error: {error.decode()}")
                
                async for line in response.aiter_lines():
                    if not line.startswith("data: "):
                        continue
                    
                    data_str = line[6:]
                    if data_str == "[DONE]":
                        break
                    
                    try:
                        data = json.loads(data_str)
                        if provider == models.AIProvider.OPENAI:
                            content = data.get("choices", [{}])[0].get("delta", {}).get("content", "")
                        else:
                            if data.get("type") != "content_block_delta":
                                continue
                            content = data.get("delta", {}).get("text", "")
                        
                        if content:
                            yield content
                    except json.JSONDecodeError:
                        continue
    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail=str(e))


async def get_response(provider: models.AIProvider, messages: List[dict]) -> str:
    config = get_api_config(provider)
    payload = {"model": config["model"], "messages": messages}
    
    if provider == models.AIProvider.ANTHROPIC:
        payload["max_tokens"] = 4096

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(config["url"], json=payload, headers=config["headers"])
            response.raise_for_status()
            data = response.json()
            
            if provider == models.AIProvider.OPENAI:
                return data["choices"][0]["message"]["content"]
            return data["content"][0]["text"]
    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail=str(e))


def get_or_create_conversation(db: Session, payload: schemas.ChatIn) -> models.Conversation:
    if payload.conversation_id:
        conversation = db.query(models.Conversation).filter(
            models.Conversation.id == payload.conversation_id,
            models.Conversation.user_id == payload.user_id,
        ).first()
        
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        if payload.title and not conversation.title:
            conversation.title = payload.title
        
        return conversation
    
    conversation = models.Conversation(
        user_id=payload.user_id,
        title=payload.title or payload.message[:80],
        ai_provider=payload.ai_provider,
    )
    db.add(conversation)
    db.flush()
    return conversation


def build_message_history(db: Session, conversation_id: int) -> List[dict]:
    messages = db.query(models.Message).filter(
        models.Message.conversation_id == conversation_id
    ).order_by(models.Message.id.asc()).all()
    
    return [{"role": msg.role.value, "content": msg.content} for msg in messages]


@router.post("/send", response_model=schemas.ChatOut, status_code=201)
async def send_message(payload: schemas.ChatIn, db: Session = Depends(get_db)):
    conversation = get_or_create_conversation(db, payload)
    
    db.add(models.Message(
        conversation_id=conversation.id,
        role=models.MessageRole.USER,
        content=payload.message,
    ))
    db.flush()
    
    history = build_message_history(db, conversation.id)
    reply = await get_response(conversation.ai_provider, history)
    
    db.add(models.Message(
        conversation_id=conversation.id,
        role=models.MessageRole.ASSISTANT,
        content=reply,
    ))
    
    conversation.updated_at = datetime.now(timezone.utc)
    db.commit()
    
    return schemas.ChatOut(conversation_id=conversation.id, reply=reply)


@router.post("/send-stream")
async def send_message_stream(payload: schemas.ChatIn, db: Session = Depends(get_db)):
    conversation = get_or_create_conversation(db, payload)
    
    user_msg = models.Message(
        conversation_id=conversation.id,
        role=models.MessageRole.USER,
        content=payload.message,
    )
    db.add(user_msg)
    db.commit()
    db.refresh(conversation)
    db.refresh(user_msg)
    
    conversation_id = conversation.id
    user_msg_id = user_msg.id
    user_msg_created = user_msg.created_at.isoformat()
    
    history = build_message_history(db, conversation_id)
    ai_provider = conversation.ai_provider
    
    async def generate():
        try:
            yield json.dumps({
                "type": "conversation_id",
                "conversation_id": conversation_id
            }) + "\n"
            
            yield json.dumps({
                "type": "user_message",
                "message": {
                    "id": user_msg_id,
                    "role": "user",
                    "content": payload.message,
                    "created_at": user_msg_created
                }
            }) + "\n"
            
            full_response = ""
            async for chunk in stream_response(ai_provider, history):
                full_response += chunk
                yield json.dumps({"type": "content", "content": chunk}) + "\n"
            
            assistant_msg = models.Message(
                conversation_id=conversation_id,
                role=models.MessageRole.ASSISTANT,
                content=full_response,
            )
            db.add(assistant_msg)
            
            conv = db.query(models.Conversation).filter(
                models.Conversation.id == conversation_id
            ).first()
            if conv:
                conv.updated_at = datetime.now(timezone.utc)
            
            db.commit()
            db.refresh(assistant_msg)
            
            yield json.dumps({
                "type": "assistant_message",
                "message": {
                    "id": assistant_msg.id,
                    "role": "assistant",
                    "content": full_response,
                    "created_at": assistant_msg.created_at.isoformat()
                }
            }) + "\n"
            
            yield json.dumps({"type": "done"}) + "\n"
        except Exception as e:
            yield json.dumps({"type": "error", "message": str(e)}) + "\n"
            raise
    
    return StreamingResponse(generate(), media_type="text/event-stream")


@router.get("/conversations", response_model=List[schemas.ConversationOut])
def get_conversations(user_id: str, db: Session = Depends(get_db)):
    return db.query(models.Conversation).filter(
        models.Conversation.user_id == user_id
    ).order_by(
        models.Conversation.updated_at.desc(),
        models.Conversation.created_at.desc()
    ).all()


@router.get("/users", response_model=List[str])
def get_users(db: Session = Depends(get_db)):
    users = db.query(models.Conversation.user_id).distinct().all()
    return [user[0] for user in users]


@router.get("/messages/{conversation_id}", response_model=schemas.MessagesOut)
def get_messages(conversation_id: int, user_id: str, db: Session = Depends(get_db)):
    conversation = db.query(models.Conversation).filter(
        models.Conversation.id == conversation_id,
        models.Conversation.user_id == user_id,
    ).first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    messages = db.query(models.Message).filter(
        models.Message.conversation_id == conversation_id
    ).order_by(models.Message.id.asc()).all()
    
    return schemas.MessagesOut(conversation_id=conversation_id, messages=messages)
