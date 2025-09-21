# MSADI-SJSU Authentication System

A Node.js authentication system for the Department of Applied Data Science

## Features

 - User login and logout functionality
 - Session management with secure cookies
 - Protected routes for authenticated users only
 - Bootstrap-styled interface with Un branding
 - Responsive design for mobile and desktop
 - Multiple user roles (admin, student, faculty)

## Project Structure

```
NodeAuth/
├── app.js              # Main server application
├── auth.js             # Authentication router
├── package.json        # Project dependencies
└── views/              # EJS templates
    ├── index.ejs       # Home page
    ├── login.ejs       # Login page
    └── dashboard.ejs   # Protected dashboard
```

## Installation

1. Navigate to the NodeAuth directory:
   ```bash
   cd NodeAuth
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the server:
   ```bash
   npm start
   ```

4. Open your browser and visit: `http://localhost:3000`

## Routes

| Route | Method | Description | Protection |
|-------|--------|-------------|------------|
| `/` | GET | Home page | Public |
| `/login` | GET | Login form | Public |
| `/login` | POST | Process login | Public |
| `/dashboard` | GET | User dashboard | Protected |
| `/logout` | GET | Logout and destroy session | Protected |

## Key Features Implemented

### 1. Session Management
- Uses `express-session` with secure configuration
- HTTP-only cookies for security
- 24-hour session timeout
- Proper session destruction on logout

### 2. Authentication
- Password hashing with `bcryptjs`
- Input validation
- Error handling for invalid credentials
- Automatic redirect for authenticated users

### 3. Route Protection
- Middleware function `requireAuth` protects dashboard
- Automatic redirection to login for unauthenticated users
- Session-based user state management

## Development

To run in development mode with auto-restart:

```bash
npm run dev
```

## License

This project is created for educational purposes as part of DATA-236 coursework.

---