# Agentic Mission Control API

FastAPI backend powering the conversational Mission Control UI. The service now features a dedicated service layer, provider gateway, and versioned routing under `/api/v1/conversations`.

## Setup

1. Create virtual environment and install dependencies:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   make install
   ```

2. Configure environment variables (`backend/.env` or export):

   ```env
   DB_HOST=127.0.0.1
   DB_PORT=3306
   DB_USER=root
   DB_PASSWORD=your_password
   DB_NAME=agentic_ai

   GEMINI_API_KEY=your_gemini_api_key
   GEMINI_MODEL=gemini-1.5-flash-latest
   ```

3. Launch the server:

   ```bash
    make dev
   ```

## CLI Commands

```bash
make users                    # List all users
make list USER=user-1         # List conversations for a user
make show CONV=1              # Show messages in a conversation
make clear-user USER=user-1   # Clear a user's conversations
make clear-all                # Purge all conversations (with confirmation)
```

## Service Architecture

- `src/services/gemini.py` – Integration helper for Google Gemini (Generative Language API)
- `src/services/chat_service.py` – Conversation orchestration and persistence helpers
- `src/routers/conversations.py` – Versioned API surface (`/api/v1/conversations`) exposing conversation + message routes

The FastAPI app is now named **Agentic AI Mission Control** (see `src/main.py`).

## HTTP API

| Method & Path | Description |
| --- | --- |
| `POST /api/v1/conversations/messages` | Persist a user message and return the Gemini completion |
| `GET /api/v1/conversations?user_id={id}` | List conversations for a given user handle |
| `GET /api/v1/conversations/users` | Retrieve distinct user handles |
| `GET /api/v1/conversations/{conversation_id}/messages?user_id={id}` | Retrieve messages for a conversation (ownership enforced) |

## Database Schema

- **Conversations**: `id`, `user_id`, `title`, `ai_provider`, `created_at`, `updated_at`
- **Messages**: `id`, `conversation_id`, `role`, `content`, `created_at`

AI provider selection remains fixed per conversation and is stored alongside each conversation record.
