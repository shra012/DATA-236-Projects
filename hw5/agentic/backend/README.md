# Agentic AI Chat Backend

FastAPI-based backend service that supports multiple AI providers (OpenAI and Anthropic Claude).

## Setup

1. Create virtual environment and install dependencies:
```bash
python -m venv .venv
source .venv/bin/activate
make install
```

2. Create `.env` file:
```env
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=agentic_ai

OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4o-mini

ANTHROPIC_API_KEY=your_anthropic_api_key
ANTHROPIC_MODEL=claude-3-5-haiku-latest
```

3. Start the server:
```bash
make dev
```

## CLI Commands

```bash
make users                    # List all users
make list USER=user-1         # List conversations for a user
make show CONV=1              # Show messages in a conversation
make clear-user USER=user-1   # Clear user's conversations
make clear-all                # Clear all conversations
```

## API Endpoints

**Primary Endpoints**:
- `POST /chat/send` - Send a message (auto-routes to correct AI provider)
- `GET /chat/conversations?userId={userId}` - Get user's conversations
- `GET /chat/users` - Get all users
- `GET /chat/messages/{conversationId}` - Get conversation messages

**Provider-Specific Endpoints**:
- `POST /openai/chat` - OpenAI-specific endpoint
- `POST /anthropic/chat` - Anthropic-specific endpoint

## Database Schema

**Conversations**: `id`, `user_id`, `title`, `ai_provider`, `created_at`, `updated_at`  
**Messages**: `id`, `conversation_id`, `role`, `content`, `created_at`

## AI Provider Selection

Users select between OpenAI (gpt-4o-mini) or Anthropic (Claude 3.5 Haiku) when creating a conversation. The provider is locked for the conversation's lifetime and stored in the `ai_provider` column.

