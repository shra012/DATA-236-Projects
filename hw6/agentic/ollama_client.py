from openai import AsyncOpenAI
from typing import List, Dict
from config import settings


class OpenAIClient:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.chat_model = settings.CHAT_MODEL
        self.embed_model = settings.EMBED_MODEL
    
    async def chat(self, messages: List[Dict[str, str]]) -> str:
        try:
            response = await self.client.chat.completions.create(
                model=self.chat_model,
                messages=messages
            )
            return response.choices[0].message.content or ""
        except Exception as error:
            print(f"Error calling OpenAI chat: {error}")
            return f"Error: Unable to get response from chat model. {error}"
    
    async def embed(self, text: str) -> List[float]:
        try:
            response = await self.client.embeddings.create(
                model=self.embed_model,
                input=text
            )
            return response.data[0].embedding
        except Exception as error:
            print(f"Error calling OpenAI embed: {error}")
            return [0.0] * 1536
    
    async def generate(self, prompt: str) -> str:
        try:
            response = await self.client.chat.completions.create(
                model=self.chat_model,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content or ""
        except Exception as error:
            print(f"Error calling OpenAI generate: {error}")
            return ""


openai_client = OpenAIClient()
