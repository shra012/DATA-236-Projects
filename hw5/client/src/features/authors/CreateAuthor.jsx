import { useState } from 'react';
import { useDispatch } from 'react-redux';
import { useNavigate, Link } from 'react-router-dom';
import AuthorForm from './AuthorForm';
import { createAuthor } from './authorsSlice';

const CreateAuthor = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const [formError, setFormError] = useState(null);

  const handleSubmit = async (values) => {
    try {
      await dispatch(createAuthor(values)).unwrap();
      navigate('/authors');
    } catch (error) {
      setFormError(error);
    }
  };

  return (
    <div className="home">
      <div className="navigation-header">
        <h2 className="section-title">Add New Author</h2>
        <Link to="/authors" className="btn btn-secondary">
          Back to list
        </Link>
      </div>

      {formError && <div className="error-banner">{formError}</div>}

      <AuthorForm submitLabel="Create Author" onSubmit={handleSubmit} />
    </div>
  );
};

export default CreateAuthor;
