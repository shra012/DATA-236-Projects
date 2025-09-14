# Book Management System - Homework 2

A functional book management application built with HTML, CSS, and Node.js/Express.

## Features Implemented

### Part 1: HTML & CSS - Artist Liberty
- **Creative Design**: Responsive design with gradient backgrounds
- **Beautiful UI**: Card-based layout with hover effects and smooth transitions
- **Custom Styling**: Unique color scheme with purple/blue gradients and creative button styles
- **Mobile Responsive**: Fully responsive design that works on all screen sizes
- **Interactive Elements**: Hover effects, loading animations, and form interactions

### Part 2: HTTP, Express, NodeJS

#### 1. Add New Book
- **Route**: `POST /books`
- **Functionality**: Users can enter Book Title and Author Name
- **Behavior**: After submission, adds book and redirects to home view
- **Implementation**: Form validation, unique ID assignment, and proper data storage

#### 2. Update Book with ID 1
- **Route**: `POST /books/1` (with hidden `_method=PUT`)
- **Functionality**: Updates book with ID 1 to "Harry Potter" by "J.K Rowling"
- **Behavior**: Pre-filled form with correct values, redirects to home after update
- **Implementation**: Finds or creates book with ID 1, updates data, and redirects

#### 3. Delete Highest ID Book
- **Route**: `POST /books/delete-highest`
- **Functionality**: Deletes the book with the highest ID from the collection
- **Behavior**: Confirmation dialog, deletion, and redirect to home view
- **Implementation**: Finds highest ID, removes book, and updates the list

## Project Structure

```
hw2/
├── package.json          # Node.js dependencies and scripts
├── server.js            # Main Express server with all routes
├── public/
│   └── styles.css       # Creative CSS with artist liberty styling
└── views/
    ├── index.html       # Home page displaying all books
```

## Installation & Setup

1. **Install Dependencies**:
   ```bash
   npm install
   ```

2. **Start the Server**:
   ```bash
   npm start
   ```
   or for development with auto-restart:
   ```bash
   npm run dev
   ```

3. **Access the Application**:
   Open your browser and go to `http://localhost:3000`

## API Endpoints

### Web Routes
- `GET /` - Home page (displays all books)
- `GET /add` - Add book form
- `GET /update` - Update book form
- `GET /delete` - Delete book interface

### API Routes
- `GET /api/books` - Returns JSON with all books and stats
- `POST /books` - Add new book (redirects to home)
- `POST /books/1` - Update book with ID 1 (redirects to home)
- `POST /books/delete-highest` - Delete highest ID book (redirects to home)

## Features

### Frontend (HTML/CSS - Artist Liberty)
- **Modern Design**: Gradient backgrounds and smooth animations
- **Responsive Layout**: Works perfectly on desktop, tablet, and mobile
- **Creative Styling**: Custom color schemes and interactive elements
- **Smooth Transitions**: Hover effects and loading animations
- **Dynamic Stats**: Real-time book count and library statistics

### Backend (Node.js/Express)
- **RESTful API**: Clean and organized route structure
- **In-Memory Storage**: Simple array-based data storage for demonstration
- **Form Validation**: Proper input validation and error handling
- **Automatic Redirects**: All operations redirect back to home view
- **Logging**: Console logging for all CRUD operations

## Technologies Used

- **Backend**: Node.js, Express.js
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Styling**: Custom CSS with gradients, animations, and responsive design
- **Package Manager**: npm
- **Development**: nodemon for auto-restart

## Part 3: Stateful Agent Graph (LangGraph)

- **Location**: `agentic_ai/stateful_graph.py`
- **Overview**: Implements a Planner → Reviewer loop using a Supervisor router with LangGraph. Uses a shared `AgentState` and conditional routing to iterate until no issues or a max turn limit.
- **Run**:
  1. Ensure Python 3.12+ is available: `python3 --version`
  2. Install uv: `curl -LsSf https://astral.sh/uv/install.sh | sh`
  3. Install dependency: `uv sync --dev` which pulls required libs from `project.toml`
  4. Execute: `python3 stateful_graph.py`, or with options like `--title, --content` etc,
- **What to expect**: Streaming logs showing `supervisor`, `planner`, `reviewer` steps, and final `END`.
- **Test correction loop**: Temporarily modify `reviewer_node` in `stateful_graph.py` to add issues if needed. The graph will route back to the planner until `max_turns` is hit if issues are not resolved.
