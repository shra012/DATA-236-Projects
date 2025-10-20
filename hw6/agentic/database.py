from motor.motor_asyncio import AsyncIOMotorClient
from config import settings
from typing import Optional

class Database:
    client: Optional[AsyncIOMotorClient] = None
    
    @classmethod
    async def connect_db(cls):
        cls.client = AsyncIOMotorClient(settings.MONGODB_URI)
        print(f"Connected to MongoDB: {settings.DATABASE_NAME}")
    
    @classmethod
    async def close_db(cls):
        if cls.client:
            cls.client.close()
            print("MongoDB connection closed")
    
    @classmethod
    def get_database(cls):
        return cls.client[settings.DATABASE_NAME]
    
    @classmethod
    def get_collection(cls, collection_name: str):
        db = cls.get_database()
        return db[collection_name]


MESSAGES_COLLECTION = "messages"
SUMMARIES_COLLECTION = "summaries"
EPISODES_COLLECTION = "episodes"
TASKS_COLLECTION = "tasks"

