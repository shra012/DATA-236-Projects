from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    MONGODB_URI: str
    DATABASE_NAME: str = "taskmanagement"
    
    OPENAI_API_KEY: str
    CHAT_MODEL: str = "gpt-4o-minii"
    EMBED_MODEL: str = "text-embedding-3-small"
    
    SHORT_TERM_N: int = 10
    SUMMARIZE_EVERY_USER_MSGS: int = 5
    EPISODIC_TOP_K: int = 5
    EPISODIC_FACTS_PER_MESSAGE: int = 3
    
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8001
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
