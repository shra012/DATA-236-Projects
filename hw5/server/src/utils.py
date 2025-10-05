"""Utility helpers shared across the FastAPI server."""

from typing import Any


def model_dump(instance: Any, *, exclude_unset: bool = False) -> dict:
    """Return a plain dictionary from either Pydantic v1 or v2 models."""
    if hasattr(instance, "model_dump"):
        return instance.model_dump(exclude_unset=exclude_unset)
    return instance.dict(exclude_unset=exclude_unset)
