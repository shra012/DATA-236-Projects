# Agentic Chat Workspace

A full-stack chat application powered by Google Gemini with a refreshed light Mission Control interface. Conversations run in a request/response flow with dynamic conversation management and a bright glassmorphism-inspired UI.

## Features

### Core Functionality
- **Gemini-Powered Responses**: Leverages Google Gemini (Generative Language API) for every conversation
- **Request/Response Flow**: Deterministic completions without streaming for predictable UX
- **Provider Lock**: Gemini provider stored per conversation for auditing consistency
- **Conversation Management**: Create, continue, and manage multiple conversations
- **Default User Context**: Operates under a single, configurable default user handle for simplicity
- **Auto-Scroll**: Messages automatically scroll to bottom as they arrive
- **Mission Control UI**: Tailwind + DaisyUI powered layout with glassmorphism accents and responsive design
- **CLI Tools**: Inspect and manage conversations from the command line

### AI Models
- **Google Gemini**: `gemini-1.5-flash-latest` (default, configurable via environment variables)

## Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+
- MySQL 8.0+
- Google Gemini API Key

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
│   │   ├── routers/             # API endpoints
│   │   │   └── conversations.py # /api/v1/conversations routes
│   │   ├── services/            # Provider + conversation orchestration
│   │   ├── models.py            # Database models
│   │   ├── schemas.py           # Pydantic schemas
│   │   └── main.py              # FastAPI application bootstrap
│   ├── .env             # Environment configuration
│   └── requirements.txt # Python dependencies
└── frontend/            # React application
    ├── src/
    │   ├── state/       # Redux state management
    │   │   └── chatSlice.js        # Chat logic & Gemini API calls
    │   ├── features/chat/          # Mission Control layout & widgets
    │   │   └── ChatDashboard.jsx   # Main dashboard composition
    │   └── styles.css              # Tailwind entry + utility helpers
    └── package.json     # Node dependencies
```

## UI Features

### Conversation Flow
- Request/response interactions with Gemini, shown immediately after completion
- Badge indicators surface the provider and mode (Gemini request/response)

### Conversation Modes
- **New Conversation**: Clear the composer to seed a fresh Gemini thread for the default user
- **Continue Conversation**: Pick an existing conversation from the history rail

### Theme
Tailwind CSS + DaisyUI with a custom **mission** light theme:
- Layered pastel gradients + glass panels for a bright mission control feel
- Primary accent `#2563eb` with supporting violet and amber highlights
- DaisyUI light fallback remains available for global theme switching

## API Endpoints

### Chat Endpoints
- `POST /api/v1/conversations/messages` - Send a user message and receive the Gemini completion
- `GET /api/v1/conversations?user_id={id}` - Get user's conversations
- `GET /api/v1/conversations/{conversation_id}/messages?user_id={id}` - Get conversation messages
- `GET /api/v1/conversations/users` - List all users

## Configuration

### Backend Environment Variables (.env)
```properties
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-1.5-flash-latest
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
- **AI API**: Google Gemini (Generative Language API)
- **HTTP Client**: httpx
- **CORS**: Enabled for local development

### Frontend
- **Framework**: React 19.1.1
- **State Management**: Redux Toolkit 2.9.0
- **Build Tool**: Vite 7.1.7
- **HTTP Client**: Axios 1.12.2
- **Styling**: Tailwind CSS 3 + DaisyUI 4 with scoped utility helpers

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

### Gemini API Errors
- Verify `GEMINI_API_KEY` is set and has access to the requested model
- Confirm `GEMINI_MODEL` matches an available Gemini Generative Language model

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
