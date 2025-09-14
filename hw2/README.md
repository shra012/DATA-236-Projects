# Book Management System - Homework 2

A functional book management application built with EJS templating, CSS, and Node.js/Express.

## Recent Updates
- **EJS Integration**: Converted from static HTML to EJS templating for dynamic content
- **Route Optimization**: Fixed delete-highest route to work with form submissions and redirects
- **Server-Side Rendering**: Now renders data directly in templates for improved performance

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

#### 2. Update Book with ID
- **Route**: `PUT /api/books/:id`
- **Functionality**: Updates existing books by ID
- **Behavior**: AJAX-based updates with real-time UI refresh
- **Implementation**: Finds book by ID, updates data, returns JSON response

#### 3. Delete Highest ID Book
- **Route**: `POST /books/delete-highest`
- **Functionality**: Deletes the book with the highest ID from the collection
- **Behavior**: Confirmation dialog, form submission, deletion, and redirect to home view
- **Implementation**: Finds highest ID, removes book, redirects to refresh page

## Project Structure

```
hw2/
├── package.json          # Node.js dependencies (includes EJS)
├── server.js            # Main Express server with EJS configuration
├── public/
│   └── styles.css       # Creative CSS with artist liberty styling
└── views/
    └── index.ejs        # EJS template with dynamic book rendering
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
- `PUT /api/books/:id` - Update book by ID (returns JSON)
- `DELETE /api/books/:id` - Delete book by ID (returns JSON)
- `POST /books/delete-highest` - Delete highest ID book (redirects to home)

## Features

### Frontend (EJS Templates)
- **Server-Side Rendering**: Dynamic content rendered with EJS templating
- **Modern Design**: Gradient backgrounds and smooth animations
- **Responsive Layout**: Works perfectly on desktop, tablet, and mobile
- **Interactive Elements**: AJAX operations for seamless user experience
- **Dynamic Stats**: Real-time book count and library statistics

### Backend (Node.js/Express)
- **EJS Integration**: Template engine for dynamic HTML generation
- **RESTful API**: Clean and organized route structure
- **Mixed Response Types**: JSON for AJAX, redirects for form submissions
- **Form Validation**: Proper input validation and error handling
- **Logging**: Console logging for all CRUD operations

## Technologies Used

- **Backend**: Node.js, Express.js, EJS
- **Frontend**: EJS Templates, CSS3, Vanilla JavaScript
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
