Agentic Memory API

Setup
1. copy .env.example to .env and fill in Mongo URI and OpenAI key
2. uv venv
3. uv pip install -r requirements.txt
4. uv run python -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload

Endpoints
- POST /api/chat
- GET /api/memory/{user_id}
- GET /api/aggregate/{user_id}
