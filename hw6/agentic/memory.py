import numpy as np
from typing import List, Dict, Any, Optional
from database import Database, MESSAGES_COLLECTION, SUMMARIES_COLLECTION, EPISODES_COLLECTION
from models import Message, Summary, Episode, RoleEnum, ScopeEnum
from ollama_client import openai_client
from config import settings
import json

def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    if not vec1 or not vec2 or len(vec1) != len(vec2):
        return 0.0
    
    v1 = np.array(vec1)
    v2 = np.array(vec2)
    
    norm1 = np.linalg.norm(v1)
    norm2 = np.linalg.norm(v2)
    
    if norm1 == 0 or norm2 == 0:
        return 0.0
    
    return float(np.dot(v1, v2) / (norm1 * norm2))


class MemoryManager:
    @staticmethod
    async def save_message(user_id: str, session_id: str, role: RoleEnum, content: str) -> Dict[str, Any]:
        message = Message(
            user_id=user_id,
            session_id=session_id,
            role=role,
            content=content
        )
        
        collection = Database.get_collection(MESSAGES_COLLECTION)
        result = await collection.insert_one(message.model_dump())
        
        return {
            "_id": str(result.inserted_id),
            **message.model_dump()
        }
    
    @staticmethod
    async def get_short_term_messages(user_id: str, session_id: str, limit: int = None) -> List[Dict[str, Any]]:
        if limit is None:
            limit = settings.SHORT_TERM_N
        
        collection = Database.get_collection(MESSAGES_COLLECTION)
        cursor = collection.find(
            {"user_id": user_id, "session_id": session_id}
        ).sort("created_at", -1).limit(limit)
        
        messages = await cursor.to_list(length=limit)
        messages.reverse()
        
        for msg in messages:
            msg["_id"] = str(msg["_id"])
        
        return messages
    
    @staticmethod
    async def get_summaries(user_id: str, session_id: Optional[str] = None) -> Dict[str, Optional[str]]:
        collection = Database.get_collection(SUMMARIES_COLLECTION)
        
        session_summary = None
        if session_id:
            session_doc = await collection.find_one(
                {"user_id": user_id, "session_id": session_id, "scope": "session"},
                sort=[("created_at", -1)]
            )
            if session_doc:
                session_summary = session_doc["text"]
        
        lifetime_doc = await collection.find_one(
            {"user_id": user_id, "session_id": None, "scope": "user"},
            sort=[("created_at", -1)]
        )
        lifetime_summary = lifetime_doc["text"] if lifetime_doc else None
        
        return {
            "session": session_summary,
            "lifetime": lifetime_summary
        }
    
    @staticmethod
    async def count_user_messages(user_id: str, session_id: str) -> int:
        collection = Database.get_collection(MESSAGES_COLLECTION)
        count = await collection.count_documents({
            "user_id": user_id,
            "session_id": session_id,
            "role": "user"
        })
        return count
    
    @staticmethod
    async def should_summarize(user_id: str, session_id: str) -> bool:
        count = await MemoryManager.count_user_messages(user_id, session_id)
        return count > 0 and count % settings.SUMMARIZE_EVERY_USER_MSGS == 0
    
    @staticmethod
    async def create_session_summary(user_id: str, session_id: str) -> Optional[str]:
        recent_messages = await MemoryManager.get_short_term_messages(
            user_id, session_id, limit=20
        )
        
        if len(recent_messages) < 3:
            return None
        
        conversation = []
        for msg in recent_messages:
            role = msg["role"]
            content = msg["content"]
            conversation.append(f"{role}: {content}")
        
        conversation_text = "\n".join(conversation)
        
        prompt = f"""Summarize the following conversation into 3-5 concise bullet points that capture the main topics, user preferences, and key information:

{conversation_text}

Provide only the bullet points, starting each with a dash (-)."""
        
        summary_text = await openai_client.generate(prompt)
        
        if summary_text:
            summary = Summary(
                user_id=user_id,
                session_id=session_id,
                scope=ScopeEnum.session,
                text=summary_text.strip()
            )
            
            collection = Database.get_collection(SUMMARIES_COLLECTION)
            await collection.insert_one(summary.model_dump())
            
            print(f"Created session summary for user {user_id}, session {session_id}")
            return summary_text.strip()
        
        return None
    
    @staticmethod
    async def update_lifetime_summary(user_id: str):
        collection = Database.get_collection(SUMMARIES_COLLECTION)
        
        cursor = collection.find(
            {"user_id": user_id, "scope": "session"}
        ).sort("created_at", -1).limit(10)
        
        session_summaries = await cursor.to_list(length=10)
        
        if len(session_summaries) < 2:
            return None
        
        combined = "\n\n".join([s["text"] for s in session_summaries])
        
        prompt = f"""Create a concise user profile summary from these conversation summaries. Focus on:
- User's interests and preferences
- Recurring topics
- Important information about the user
- Their communication style and needs

Session Summaries:
{combined}

Provide 4-6 bullet points starting with dashes (-)."""
        
        lifetime_text = await openai_client.generate(prompt)
        
        if lifetime_text:
            summary = Summary(
                user_id=user_id,
                session_id=None,
                scope=ScopeEnum.user,
                text=lifetime_text.strip()
            )
            
            await collection.update_one(
                {"user_id": user_id, "session_id": None, "scope": "user"},
                {"$set": summary.model_dump()},
                upsert=True
            )
            
            print(f"Updated lifetime summary for user {user_id}")
            return lifetime_text.strip()
        
        return None
    
    @staticmethod
    async def extract_episodic_facts(user_id: str, session_id: str, message: str) -> List[Dict[str, Any]]:
        prompt = f"""Extract up to {settings.EPISODIC_FACTS_PER_MESSAGE} short, factual statements from this message that would be useful to remember in future conversations. 
For each fact, also rate its importance from 0.0 to 1.0.

Message: "{message}"

Return ONLY a JSON array in this exact format:
[
  {{"fact": "short fact here", "importance": 0.8}},
  {{"fact": "another fact", "importance": 0.6}}
]

If there are no important facts, return an empty array []."""
        
        response = await openai_client.generate(prompt)
        
        try:
            response = response.strip()
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                response = response.split("```")[1].split("```")[0].strip()
            
            facts = json.loads(response)
            
            if not isinstance(facts, list):
                return []
            
            episodes = []
            collection = Database.get_collection(EPISODES_COLLECTION)
            
            for fact_data in facts[:settings.EPISODIC_FACTS_PER_MESSAGE]:
                if not isinstance(fact_data, dict) or "fact" not in fact_data:
                    continue
                
                fact_text = fact_data["fact"]
                importance = float(fact_data.get("importance", 0.5))
                importance = max(0.0, min(1.0, importance))
                
                embedding = await openai_client.embed(fact_text)
                
                episode = Episode(
                    user_id=user_id,
                    session_id=session_id,
                    fact=fact_text,
                    importance=importance,
                    embedding=embedding
                )
                
                result = await collection.insert_one(episode.model_dump())
                episodes.append({
                    "_id": str(result.inserted_id),
                    **episode.model_dump()
                })
            
            print(f"Extracted {len(episodes)} episodic facts")
            return episodes
            
        except json.JSONDecodeError as e:
            print(f"Failed to parse facts JSON: {e}")
            print(f"Response was: {response}")
            return []
        except Exception as e:
            print(f"Error extracting facts: {e}")
            return []
    
    @staticmethod
    async def retrieve_relevant_episodes(user_id: str, query: str, top_k: int = None) -> List[Dict[str, Any]]:
        if top_k is None:
            top_k = settings.EPISODIC_TOP_K
        
        query_embedding = await openai_client.embed(query)
        
        collection = Database.get_collection(EPISODES_COLLECTION)
        cursor = collection.find({"user_id": user_id}).limit(100)
        episodes = await cursor.to_list(length=100)
        
        if not episodes:
            return []
        
        scored_episodes = []
        for ep in episodes:
            similarity = cosine_similarity(query_embedding, ep["embedding"])
            score = similarity * ep["importance"]
            scored_episodes.append({
                "fact": ep["fact"],
                "importance": ep["importance"],
                "similarity": similarity,
                "score": score,
                "created_at": ep["created_at"]
            })
        
        scored_episodes.sort(key=lambda x: x["score"], reverse=True)
        return scored_episodes[:top_k]


memory_manager = MemoryManager()
