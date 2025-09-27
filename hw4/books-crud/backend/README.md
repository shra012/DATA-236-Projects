# Books CRUD Backend API

A RESTful API for managing books using Node.js, Express, MySQL, and Sequelize ORM.

## Features

- **Full CRUD Operations**: Create, Read, Update, Delete books
- **MySQL Database**: Persistent data storage with Sequelize ORM
- **Input Validation**: Server-side validation for all inputs
- **Error Handling**: Comprehensive error handling and logging
- **CORS Support**: Cross-origin requests enabled for frontend
- **Auto-seeding**: Initial sample data when database is empty

## Technology Stack

- **Node.js** - Runtime environment
- **Express.js** - Web framework
- **MySQL** - Database
- **Sequelize** - ORM (Object Relational Mapping)
- **CORS** - Cross-origin resource sharing
- **dotenv** - Environment variable management

## Prerequisites

- Node.js (v14 or higher)
- MySQL Server (v5.7 or higher)
- npm or yarn package manager

## Installation

1. **Navigate to backend directory:**
   ```bash
   cd books-crud-backend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Set up environment variables:**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` file with your MySQL configuration:
   ```
   DB_HOST=localhost
   DB_PORT=3306
   DB_NAME=book_db
   DB_USER=root
   DB_PASSWORD=your_password
   PORT=3001
   ```

4. **Create MySQL database:**
   ```sql
   CREATE DATABASE book_db;
   ```

5. **Start the server:**
   ```bash
   # Development mode with auto-restart
   npm run dev
   
   # Production mode
   npm start
   ```

## API Endpoints

### Base URL: `http://localhost:3001/api`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/books` | Get all books |
| GET | `/books/:id` | Get book by ID |
| POST | `/books` | Create a new book |
| PUT | `/books/:id` | Update a book |
| DELETE | `/books/:id` | Delete a book |
| GET | `/health` | Health check |

### Sample API Calls

**Get all books:**
```bash
GET /api/books
```

**Get book by ID:**
```bash
GET /api/books/1
```

**Create a new book:**
```bash
POST /api/books
Content-Type: application/json

{
  "title": "The Hobbit",
  "author": "J.R.R. Tolkien"
}
```

**Update a book:**
```bash
PUT /api/books/1
Content-Type: application/json

{
  "title": "Updated Title",
  "author": "Updated Author"
}
```

**Delete a book:**
```bash
DELETE /api/books/1
```

## Database Schema

### Books Table Structure

```sql
CREATE TABLE books (
  id INT AUTO_INCREMENT PRIMARY KEY,
  title VARCHAR(255) NOT NULL,
  author VARCHAR(255) NOT NULL,
  createdAt DATETIME DEFAULT CURRENT_TIMESTAMP,
  updatedAt DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

## Response Format

### Success Response
```json
{
  "success": true,
  "message": "Operation completed successfully",
  "data": {
    "id": 1,
    "title": "Book Title",
    "author": "Author Name",
    "createdAt": "2025-09-25T10:30:00.000Z",
    "updatedAt": "2025-09-25T10:30:00.000Z"
  }
}
```

### Error Response
```json
{
  "success": false,
  "message": "Error description",
  "error": "Detailed error message"
}
```

## Development

### Project Structure
```
books-crud-backend/
├── config/
│   └── database.js          # Database configuration
├── controllers/
│   └── bookController.js    # Book CRUD logic
├── models/
│   └── Book.js             # Book Sequelize model
├── routes/
│   └── bookRoutes.js       # API routes
├── .env                    # Environment variables
├── .env.example           # Environment template
├── package.json           # Dependencies and scripts
├── server.js              # Main server file
└── README.md              # This file
```

### Running in Development Mode
```bash
npm run dev
```
This uses nodemon for auto-restarting the server on file changes.

## Troubleshooting

1. **Database Connection Issues:**
   - Ensure MySQL server is running
   - Check database credentials in `.env` file
   - Verify database `book_db` exists

2. **Port Already in Use:**
   - Change PORT in `.env` file
   - Kill existing process: `lsof -ti:3001 | xargs kill -9`

3. **CORS Issues:**
   - Frontend URL is whitelisted in server.js
   - Ensure frontend runs on http://localhost:3000

## License

ISC License