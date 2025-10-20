from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from .database import Base, engine
from .routers import conversations_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Agentic AI Mission Control", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(conversations_router)


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")
