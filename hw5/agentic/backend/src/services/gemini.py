import os
from typing import Dict, List

import httpx
from fastapi import HTTPException, status


def _to_gemini_contents(messages: List[Dict[str, str]]) -> List[Dict]:
  contents: List[Dict] = []
  for message in messages:
    role = message.get("role", "user")
    content_text = message.get("content", "")
    if not content_text:
      continue
    contents.append(
      {
        "role": "model" if role == "assistant" else "user",
        "parts": [{"text": content_text}],
      }
    )
  return contents


def _mock_completion(messages: List[Dict[str, str]]) -> str:
  last_user_message = next(
    (message.get("content", "") for message in reversed(messages) if message.get("role") == "user"),
    "",
  )
  preamble = "Gemini (mock): "
  if not last_user_message:
    return f"{preamble}I'm running in mock mode, so I can't see a user prompt yet. Ask me something!"
  return f"{preamble}I received your message \"{last_user_message}\" but no live Gemini API is configured. This is a placeholder response."


async def generate_gemini_completion(messages: List[Dict[str, str]]) -> str:
  api_key = os.getenv("GEMINI_API_KEY")
  if not api_key:
    return _mock_completion(messages)

  model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
  url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

  payload = {"contents": _to_gemini_contents(messages)}

  try:
    async with httpx.AsyncClient(timeout=60.0) as client:
      response = await client.post(url, params={"key": api_key}, json=payload)
      response.raise_for_status()
      data = response.json()
  except httpx.HTTPStatusError as error:
    raise HTTPException(
      status_code=status.HTTP_502_BAD_GATEWAY,
      detail=f"Gemini error: {error.response.text}",
    ) from error
  except httpx.HTTPError as error:
    raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(error)) from error

  candidates = data.get("candidates", [])
  for candidate in candidates:
    parts = candidate.get("content", {}).get("parts", [])
    collected = [part.get("text", "") for part in parts if part.get("text")]
    if collected:
      return "".join(collected)

  raise HTTPException(
    status_code=status.HTTP_502_BAD_GATEWAY,
    detail="Gemini returned an empty response.",
  )
