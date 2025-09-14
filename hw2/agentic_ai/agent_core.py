from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List, TypedDict

from pydantic import BaseModel, Field
from langchain.chat_models import init_chat_model


try:
    from dotenv import load_dotenv

    _DOTENV_PATH = Path(__file__).resolve().parent / ".env"
    if _DOTENV_PATH.exists():
        load_dotenv(dotenv_path=_DOTENV_PATH)
    else:
        load_dotenv()
except Exception:
    pass

if os.getenv("LANGSMITH_TRACING") and not os.getenv("LANGCHAIN_TRACING_V2"):
    os.environ["LANGCHAIN_TRACING_V2"] = os.getenv("LANGSMITH_TRACING", "")
if os.getenv("LANGSMITH_API_KEY") and not os.getenv("LANGCHAIN_API_KEY"):
    os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGSMITH_API_KEY", "")
if os.getenv("LANGSMITH_PROJECT") and not os.getenv("LANGCHAIN_PROJECT"):
    os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGSMITH_PROJECT", "")


class AgentState(TypedDict, total=False):
    title: str
    content: str
    email: str
    strict: bool
    task: str
    planner_proposal: Dict[str, Any]
    reviewer_feedback: Dict[str, Any]
    original_issues: List[str]
    turn_count: int


class PlanSchema(BaseModel):
    summary: str = Field(..., description="One-paragraph summary of the plan")
    outline: List[str] = Field(..., description="Ordered list of section titles/steps")
    notes: str = Field(..., description="Additional guidance or considerations")


class ReviewSchema(BaseModel):
    issues: List[str] = Field(default_factory=list, description="List of concrete issues found")
    approved: bool = Field(..., description="True if no issues detected")
    comments: str = Field(..., description="Short summary of the review outcome")


# Initialize a single ChatModel for reuse in all nodes
MODEL_NAME = (os.getenv("OPENAI_MODEL") or os.getenv("MODEL") or "gpt-5-mini").strip()
LLM = init_chat_model(f"openai:{MODEL_NAME}", temperature=1.0)
