Project Notes

Backend API (Node)
1. cd backend
2. npm install
3. create .env with MONGODB_URI and PORT
4. npm start

Agentic API (Python)
1. cd agentic
2. copy .env from sample and fill in Mongo URI and OpenAI key
3. uv venv
4. uv pip install -r requirements.txt
5. uv run python -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload
