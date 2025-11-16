# Kayak Frontend

React frontend application for the Kayak Simulation Platform.

## Features

- ✅ React 18 with Vite
- ✅ React Router for navigation
- ✅ React Query for API caching and data fetching
- ✅ Redux Toolkit for global state management
- ✅ Axios for HTTP requests
- ✅ DaisyUI components
- ✅ Tailwind CSS for styling
- ✅ Modular architecture

## Tech Stack

- **React 18** - UI library
- **Vite** - Build tool and dev server
- **React Router** - Client-side routing
- **React Query** - Server state management and caching
- **Redux Toolkit** - Client state management
- **Axios** - HTTP client
- **DaisyUI** - Component library
- **Tailwind CSS** - Utility-first CSS framework

## Project Structure

```
frontend/
├── src/
│   ├── components/          # Reusable components
│   │   └── layout/          # Layout components
│   ├── pages/               # Page components
│   │   ├── users/
│   │   ├── listings/
│   │   ├── bookings/
│   │   ├── payments/
│   │   ├── admin/
│   │   ├── concierge/
│   │   └── analytics/
│   ├── services/            # API services
│   │   └── api/            # API client functions
│   ├── store/              # Redux store
│   │   └── slices/        # Redux slices
│   ├── hooks/              # Custom React hooks
│   ├── config/             # Configuration files
│   │   └── api.js         # Axios instance
│   ├── App.jsx             # Main app component
│   ├── main.jsx            # Entry point
│   └── index.css           # Global styles
├── index.html
├── vite.config.js
├── tailwind.config.js
├── postcss.config.js
├── package.json
└── README.md
```

## Setup

1. **Install dependencies:**
```bash
npm install
```

2. **Create `.env` file (optional):**
```bash
VITE_API_BASE_URL=http://localhost:3000
VITE_API_VERSION=v1
```

3. **Start development server:**
```bash
npm run dev
```

The app will be available at `http://localhost:5173`

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint
- `npm run lint:fix` - Fix ESLint errors

## Features Overview

### State Management

- **React Query**: Handles server state (API data, caching, refetching)
- **Redux Toolkit**: Handles client state (auth, UI preferences, notifications)

### API Client

The API client (`src/config/api.js`) is configured with:
- Base URL from environment variables
- Automatic token injection from localStorage
- Request/response interceptors
- Error handling (401 redirects to login)

### Routing

Routes are defined in `src/App.jsx`:
- `/` - Home page
- `/login` - Login page
- `/users` - Users list
- `/users/:userId` - User details
- `/flights` - Flight search
- `/hotels` - Hotel search
- `/cars` - Car search
- `/bookings` - Bookings list
- `/bookings/:bookingId` - Booking details
- `/payments` - Payments
- `/admin` - Admin dashboard
- `/concierge` - AI Concierge
- `/analytics` - Analytics

### Components

- **Layout**: Main layout with navbar and footer
- **Pages**: Individual page components
- Uses DaisyUI components for consistent styling

## Development

### Adding a New Page

1. Create component in `src/pages/`
2. Add route in `src/App.jsx`
3. Add navigation link in `src/components/layout/Layout.jsx`

### Adding API Service

1. Create service file in `src/services/api/`
2. Use `apiClient` from `src/config/api.js`
3. Use React Query hooks in components

### Example: Using React Query

```jsx
import { useQuery } from '@tanstack/react-query';
import { usersApi } from '../services/api/users';

function UsersPage() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['users'],
    queryFn: () => usersApi.listUsers(),
  });

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;

  return <div>{/* Render data */}</div>;
}
```

### Example: Using Redux

```jsx
import { useSelector, useDispatch } from 'react-redux';
import { setTheme } from '../store/slices/uiSlice';

function ThemeSelector() {
  const theme = useSelector((state) => state.ui.theme);
  const dispatch = useDispatch();

  return (
    <select
      value={theme}
      onChange={(e) => dispatch(setTheme(e.target.value))}
    >
      <option value="light">Light</option>
      <option value="dark">Dark</option>
    </select>
  );
}
```

## Next Steps

1. Implement authentication flow
2. Complete all page components
3. Add form validation (React Hook Form + Zod)
4. Add error boundaries
5. Add loading states and skeletons
6. Add toast notifications
7. Implement WebSocket for real-time updates
8. Add comprehensive tests

