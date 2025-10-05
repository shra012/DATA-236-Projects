import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


def _build_database_url():
    if url := os.getenv("DATABASE_URL"):
        return url

    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD", "")
    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT", "3306")
    name = os.getenv("DB_NAME")

    if not (user and host and name):
        raise ValueError("Database configuration missing. Set DB_USER, DB_HOST, and DB_NAME.")

    credentials = f"{user}:{password}" if password else user
    return f"mysql+pymysql://{credentials}@{host}:{port}/{name}"


engine = create_engine(_build_database_url())
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
