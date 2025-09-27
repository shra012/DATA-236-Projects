import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';

const CreateBook = ({ addBook }) => {
  const [title, setTitle] = useState('');
  const [author, setAuthor] = useState('');
  const [saving, setSaving] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!title.trim() || !author.trim()) {
      return;
    }
    setSaving(true);
    const result = await addBook(title.trim(), author.trim());
    setSaving(false);
    if (result.success) {
      navigate('/');
    }
  };

  return (
    <div>
      <div className='navigation-header'>
        <h2 className='section-title'>Add Book</h2>
        <Link to='/' className='back-button'>
          Back to Home
        </Link>
      </div>
      <div className='form-container'>
        <form onSubmit={handleSubmit}>
          <div className='form-group'>
            <label htmlFor='bookTitle' className='form-label'>
              Book Title
            </label>
            <input
              id='bookTitle'
              type='text'
              className='form-input'
              value={title}
              onChange={(event) => setTitle(event.target.value)}
              placeholder='Enter a title'
              required
            />
          </div>
          <div className='form-group'>
            <label htmlFor='authorName' className='form-label'>
              Author
            </label>
            <input
              id='authorName'
              type='text'
              className='form-input'
              value={author}
              onChange={(event) => setAuthor(event.target.value)}
              placeholder='Enter an author'
              required
            />
          </div>
          <div className='form-actions'>
            <button type='submit' className='btn btn-primary' disabled={saving}>
              {saving ? 'Saving...' : 'Save'}
            </button>
            <Link to='/' className='btn btn-secondary'>
              Cancel
            </Link>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CreateBook;
