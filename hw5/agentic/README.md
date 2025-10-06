# Agentic Chat Workspace

A full-stack chat application with multi-AI provider support and real-time streaming responses. Users can chat with OpenAI (GPT-4o Mini) or Anthropic (Claude) with instant message display and streaming AI responses.

## Features

### Core Functionality
- **Multi-AI Provider Support**: Choose between OpenAI (GPT-4o Mini) and Anthropic (Claude Haiku) for each conversation
- **Real-Time Streaming**: AI responses stream character-by-character as they're generated
- **Dual Response Modes**: 
  - **Streaming Mode**: Real-time character-by-character response streaming
  - **Fixed Mode**: Traditional request/response pattern
- **Provider Lock**: AI provider is locked per conversation for consistency
- **Conversation Management**: Create, continue, and manage multiple conversations
- **Multi-User Support**: Each user can have their own conversations
- **Auto-Scroll**: Messages automatically scroll to bottom as they arrive
- **Modern UI**: Clean Atom One Dark theme with responsive design
- **CLI Tools**: Inspect and manage conversations from the command line

### AI Models
- **OpenAI**: `gpt-4o-mini` (fast, cost-efficient, supports streaming)
- **Anthropic**: `claude-3-5-haiku-latest` (latest Haiku model)

## Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+
- MySQL 8.0+
- OpenAI API Key
- Anthropic API Key

### Backend Setup
```bash
cd backend
make install          # Install dependencies
cp .env.example .env  # Configure environment variables
# Edit .env with your API keys and database credentials
make dev              # Start development server
```

### Frontend Setup
```bash
cd frontend
npm install           # Install dependencies
npm run dev           # Start development server
```

The application will be available at:
- **Frontend**: http://localhost:5173
- **Backend API**: http://127.0.0.1:8000
- **API Docs**: http://127.0.0.1:8000/docs

## Project Structure

```
agentic/
├── backend/              # FastAPI server
│   ├── src/
│   │   ├── routers/     # API endpoints
│   │   │   └── chat.py  # Chat & streaming endpoints
│   │   ├── models.py    # Database models
│   │   ├── schemas.py   # Pydantic schemas
│   │   └── main.py      # FastAPI application
│   ├── .env             # Environment configuration
│   └── requirements.txt # Python dependencies
└── frontend/            # React application
    ├── src/
    │   ├── store/       # Redux state management
    │   │   └── chatSlice.js  # Chat logic & streaming
    │   ├── App.jsx      # Main component
    │   └── App.css      # Atom One Dark theme
    └── package.json     # Node dependencies
```

## UI Features

### Response Modes
Toggle between two response modes in the sidebar:
- **Streaming (Real-time)**: AI responses appear character-by-character as generated
- **Fixed (Request/Response)**: Traditional mode - wait for complete response

### Conversation Modes
- **New Conversation**: Start fresh with a new user ID
- **Continue Conversation**: Select existing user and conversation

### Theme
Atom One Dark color scheme:
- Background: `#282c34`
- Accent: `#61afef` (Blue)
- Syntax highlighting inspired colors

## API Endpoints

### Chat Endpoints
- `POST /chat/send` - Send message (traditional request/response)
- `POST /chat/send-stream` - Send message with streaming response
- `GET /chat/conversations?user_id={id}` - Get user's conversations
- `GET /chat/messages/{conversation_id}?user_id={id}` - Get conversation messages
- `GET /chat/users` - List all users

### Streaming Format
The `/chat/send-stream` endpoint returns Server-Sent Events (SSE) with JSON payloads:

```json
{"type": "conversation_id", "conversation_id": 1}
{"type": "user_message", "message": {...}}
{"type": "content", "content": "Hello"}
{"type": "content", "content": " world"}
{"type": "assistant_message", "message": {...}}
{"type": "done"}
```

## Configuration

### Backend Environment Variables (.env)
```properties
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4o-mini
ANTHROPIC_API_KEY=your_anthropic_api_key
ANTHROPIC_MODEL=claude-3-5-haiku-latest
DB_USER=root
DB_PASSWORD=your_password
DB_HOST=127.0.0.1
DB_PORT=3306
DB_NAME=agentic_ai
```

### Frontend Environment Variables (.env)
```properties
VITE_API_BASE_URL=http://localhost:8000
```

## 🛠️ Technology Stack

### Backend
- **Framework**: FastAPI 0.115.12
- **Database**: SQLAlchemy + MySQL
- **AI APIs**: OpenAI, Anthropic
- **HTTP Client**: httpx (async streaming)
- **CORS**: Enabled for local development

### Frontend
- **Framework**: React 19.1.1
- **State Management**: Redux Toolkit 2.9.0
- **Build Tool**: Vite 7.1.7
- **HTTP Client**: Axios 1.12.2 + Fetch API (streaming)
- **Styling**: CSS with custom properties

## Development

### CLI Commands
Inspect conversations from the command line:
```bash
cd backend
python -m src.cli list-conversations --user-id user-1
python -m src.cli show-conversation --conversation-id 1
```

### Database Migrations
The application auto-creates tables on startup. For manual control:
```python
from src.database import Base, engine
Base.metadata.create_all(bind=engine)
```

## Security Notes

- API keys should never be committed to version control
- Use environment variables for all sensitive configuration
- CORS is configured for localhost - update for production
- Database credentials should be secured

## Additional Documentation

- [Backend README](backend/README.md) - Detailed backend setup and API docs
- [Frontend README](frontend/README.md) - Frontend architecture and components
- [API Documentation](http://127.0.0.1:8000/docs) - Interactive Swagger UI (when running)

## Troubleshooting

### OpenAI Streaming Errors
- Ensure `gpt-4o-mini` is used (supports streaming without verification)
- Check API key permissions

### Database Connection Issues
- Verify MySQL is running
- Check database credentials in `.env`
- Ensure database `agentic_ai` exists

### Frontend Can't Connect to Backend
- Verify backend is running on port 8000
- Check CORS settings in `main.py`
- Update `VITE_API_BASE_URL` if needed

## License

This project is for educational purposes.

