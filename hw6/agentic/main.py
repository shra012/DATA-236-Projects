from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from datetime import datetime
from typing import List, Dict, Any
import os

from config import settings
from database import Database, MESSAGES_COLLECTION, SUMMARIES_COLLECTION, EPISODES_COLLECTION
from models import (
    ChatRequest, ChatResponse, MemoryContext,
    MemoryView, AggregateView, DailyMessageCount,
    RoleEnum
)
from memory import memory_manager
from ollama_client import openai_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    await Database.connect_db()
    print("FastAPI server started")
    yield
    await Database.close_db()
    print("FastAPI server stopped")


app = FastAPI(
    title="Agentic Memory Chat API",
    description="Chat API with short-term, long-term, and episodic memory",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {
        "message": "Agentic Memory Chat API",
        "version": "1.0.0",
        "endpoints": {
            "POST /api/chat": "Send a message and get a response with memory context",
            "GET /api/memory/{user_id}": "Get memory view for a user",
            "GET /api/aggregate/{user_id}": "Get aggregated statistics for a user",
            "GET /health": "Health check endpoint"
        }
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "database": "connected" if Database.client else "disconnected"
    }


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    user_id = request.user_id
    session_id = request.session_id or "default"
    user_message = request.message
    
    try:
        await memory_manager.save_message(user_id, session_id, RoleEnum.user, user_message)
        
        short_term_messages = await memory_manager.get_short_term_messages(user_id, session_id)
        
        summaries = await memory_manager.get_summaries(user_id, session_id)
        session_summary = summaries["session"]
        lifetime_summary = summaries["lifetime"]
        
        long_term_text = ""
        if lifetime_summary: 
            long_term_text += f"User Profile:\n{lifetime_summary}\n\n"
        if session_summary:
            long_term_text += f"Session Context:\n{session_summary}\n\n"
        
        relevant_episodes = await memory_manager.retrieve_relevant_episodes(user_id, user_message)
        episodic_text = ""
        if relevant_episodes:
            facts = [ep["fact"] for ep in relevant_episodes]
            episodic_text = "Relevant memories: " + " | ".join(facts)
        
        chat_messages = []
        
        system_prompt = """You are a helpful AI assistant with memory capabilities. 
You remember information from previous conversations and use it to provide personalized, context-aware responses.
Be conversational, friendly, and refer to past interactions when relevant.
Keep every reply concise and under 100 tokens."""
        
        if long_term_text:
            system_prompt += f"\n\n{long_term_text}"
        
        if episodic_text:
            system_prompt += f"\n{episodic_text}"
        
        chat_messages.append({"role": "system", "content": system_prompt})
        
        for msg in short_term_messages[-settings.SHORT_TERM_N:]:
            chat_messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        assistant_reply = await openai_client.chat(chat_messages)
        
        await memory_manager.save_message(user_id, session_id, RoleEnum.assistant, assistant_reply)
        
        if await memory_manager.should_summarize(user_id, session_id):
            await memory_manager.create_session_summary(user_id, session_id)
            
            user_msg_count = await memory_manager.count_user_messages(user_id, session_id)
            if user_msg_count % (settings.SUMMARIZE_EVERY_USER_MSGS * 3) == 0:
                await memory_manager.update_lifetime_summary(user_id)
        
        import asyncio
        asyncio.create_task(memory_manager.extract_episodic_facts(user_id, session_id, user_message))
        
        memory_context = MemoryContext(
            short_term_count=len(short_term_messages),
            short_term_messages=[
                {
                    "role": msg["role"],
                    "content": msg["content"][:100] + "..." if len(msg["content"]) > 100 else msg["content"],
                    "created_at": msg["created_at"].isoformat() if isinstance(msg["created_at"], datetime) else str(msg["created_at"])
                }
                for msg in short_term_messages
            ],
            long_term_summary=long_term_text if long_term_text else None,
            episodic_facts=[ep["fact"] for ep in relevant_episodes]
        )
        
        return ChatResponse(
            reply=assistant_reply,
            memory_context=memory_context
        )
    
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")


@app.get("/api/memory/{user_id}", response_model=MemoryView)
async def get_memory(user_id: str, session_id: str = "default"):
    try:
        recent_messages = await memory_manager.get_short_term_messages(user_id, session_id, limit=16)
        
        summaries = await memory_manager.get_summaries(user_id, session_id)
        
        collection = Database.get_collection(EPISODES_COLLECTION)
        cursor = collection.find(
            {"user_id": user_id}
        ).sort("created_at", -1).limit(20)
        episodes = await cursor.to_list(length=20)
        
        return MemoryView(
            user_id=user_id,
            recent_messages=[
                {
                    "role": msg["role"],
                    "content": msg["content"],
                    "created_at": msg["created_at"].isoformat() if isinstance(msg["created_at"], datetime) else str(msg["created_at"])
                }
                for msg in recent_messages
            ],
            session_summary=summaries["session"],
            lifetime_summary=summaries["lifetime"],
            episodic_facts=[ep["fact"] for ep in episodes]
        )
    
    except Exception as e:
        print(f"Error in memory endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving memory: {str(e)}")


@app.get("/api/aggregate/{user_id}", response_model=AggregateView)
async def get_aggregate(user_id: str):
    try:
        collection = Database.get_collection(MESSAGES_COLLECTION)
        
        pipeline = [
            {"$match": {"user_id": user_id}},
            {
                "$group": {
                    "_id": {
                        "$dateToString": {
                            "format": "%Y-%m-%d",
                            "date": "$created_at"
                        }
                    },
                    "count": {"$sum": 1}
                }
            },
            {"$sort": {"_id": -1}},
            {"$limit": 30}
        ]
        
        daily_counts = await collection.aggregate(pipeline).to_list(length=30)
        
        summaries_collection = Database.get_collection(SUMMARIES_COLLECTION)
        cursor = summaries_collection.find(
            {"user_id": user_id}
        ).sort("created_at", -1).limit(5)
        recent_summaries = await cursor.to_list(length=5)
        
        return AggregateView(
            user_id=user_id,
            daily_message_counts=[
                DailyMessageCount(date=dc["_id"], count=dc["count"])
                for dc in daily_counts
            ],
            recent_summaries=[
                {
                    "scope": s["scope"],
                    "text": s["text"],
                    "session_id": s.get("session_id"),
                    "created_at": s["created_at"].isoformat() if isinstance(s["created_at"], datetime) else str(s["created_at"])
                }
                for s in recent_summaries
            ]
        )
    
    except Exception as e:
        print(f"Error in aggregate endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving aggregate data: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True
    )
