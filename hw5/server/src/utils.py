from typing import Any


def model_dump(instance: Any, *, exclude_unset: bool = False) -> dict:
    if hasattr(instance, "model_dump"):
        return instance.model_dump(exclude_unset=exclude_unset)
    return instance.dict(exclude_unset=exclude_unset)
