import './App.css';
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
  NavLink,
} from 'react-router-dom';
import BooksList from './features/books/BooksList';
import CreateBook from './features/books/CreateBook';
import EditBook from './features/books/EditBook';
import AuthorsList from './features/authors/AuthorsList';
import CreateAuthor from './features/authors/CreateAuthor';
import EditAuthor from './features/authors/EditAuthor';

const navLinkClass = ({ isActive }) => `nav-link${isActive ? ' active' : ''}`;

const App = () => (
  <Router>
    <div className="app-container">
      <header className="header">
        <h1 className="main-title">Library Management System</h1>
        <p className="subtitle">Track authors and their books effortlessly.</p>

        <nav className="top-nav">
          <div className="nav-links">
            <NavLink to="/books" className={navLinkClass}>
              Books
            </NavLink>
            <NavLink to="/authors" className={navLinkClass}>
              Authors
            </NavLink>
          </div>
        </nav>
      </header>

      <main className="main-content">
        <Routes>
          <Route path="/" element={<Navigate to="/books" replace />} />
          <Route path="/books" element={<BooksList />} />
          <Route path="/books/create" element={<CreateBook />} />
          <Route path="/books/edit/:id" element={<EditBook />} />
          <Route path="/authors" element={<AuthorsList />} />
          <Route path="/authors/create" element={<CreateAuthor />} />
          <Route path="/authors/edit/:id" element={<EditAuthor />} />
        </Routes>
      </main>
    </div>
  </Router>
);

export default App;
