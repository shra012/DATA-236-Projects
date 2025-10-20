# Agentic Mission Control UI

Revamped React + Vite experience for orchestrating agentic chat sessions. The interface now uses a light Tailwind CSS + DaisyUI theme to deliver a bright, responsive workspace composed of modular components.

## Setup

```bash
npm install
npm run dev
```

Optional environment override:

```bash
echo "VITE_API_BASE_URL=http://localhost:8000" > .env.local
```

## Scripts

- `npm run dev` – Run the Vite dev server with hot reload
- `npm run build` – Generate a production bundle
- `npm run preview` – Preview the production build locally

## Architecture Notes

- `src/features/chat/ChatDashboard.jsx` – Top-level layout wiring together sidebar, workspace, and state
- `src/features/chat/components/*` – DaisyUI-driven widgets (sidebar, message composer, workspace)
- `src/state/chatSlice.js` – Redux Toolkit slice driving request/response messaging
- `tailwind.config.js` / `postcss.config.js` – Tailwind + DaisyUI configuration and theming
- `src/styles.css` – Tailwind entry point with a few scoped utility helpers

## Key UX Patterns

- Toggle between launching a fresh conversation or resuming existing threads from the left rail
- Request/response messaging exclusively with Google Gemini as the AI provider
- Default user context—conversations always run under the single configured handle
- Light-glass mission control aesthetic with contextual badges indicating the provider in play

The UI ships with a custom **mission** light theme and also keeps the default DaisyUI light palette available for global theme switches.
