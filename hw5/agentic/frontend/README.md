# Agentic Frontend

React + Vite single-page app that consumes the Agentic AI backend with multi-provider support.

## Setup

```bash
npm install
npm run dev
```

Optional - set backend URL:
```bash
echo "VITE_API_BASE_URL=http://localhost:8000" > .env.local
```

## Scripts

- `npm run dev` - Start dev server with hot reload
- `npm run build` - Create production bundle
- `npm run preview` - Preview production build

## Architecture

- `src/store/chatSlice.js` - Redux Toolkit state management with AI provider handling
- `src/App.jsx` - Main UI component with conversation list and chat interface
- `src/App.css` - Dark theme styling with provider badges

## Usage

**New Conversation**: Enter User ID, select AI Provider (OpenAI/Anthropic), type message  
**Continue Conversation**: Toggle to "Continue", select user, pick conversation from list

The AI provider is locked per conversation and shown with color-coded badges.


