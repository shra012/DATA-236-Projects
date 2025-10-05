import { useEffect, useState } from 'react';

const AuthorForm = ({ initialValues, onSubmit, submitLabel }) => {
  const [formValues, setFormValues] = useState({
    first_name: '',
    last_name: '',
    email: '',
  });

  const [errors, setErrors] = useState({});

  useEffect(() => {
    if (initialValues) {
      setFormValues({
        first_name: initialValues.first_name || '',
        last_name: initialValues.last_name || '',
        email: initialValues.email || '',
      });
    }
  }, [initialValues]);

  const validate = () => {
    const validationErrors = {};
    if (!formValues.first_name) {
      validationErrors.first_name = 'First name is required';
    }
    if (!formValues.last_name) {
      validationErrors.last_name = 'Last name is required';
    }
    if (!formValues.email) {
      validationErrors.email = 'Email is required';
    }
    setErrors(validationErrors);
    return Object.keys(validationErrors).length === 0;
  };

  const handleChange = (event) => {
    const { name, value } = event.target;
    setFormValues((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    if (!validate()) {
      return;
    }
    onSubmit({ ...formValues });
  };

  return (
    <form className="form-container" onSubmit={handleSubmit}>
      <div className="form-group">
        <label className="form-label" htmlFor="first_name">First name</label>
        <input
          id="first_name"
          name="first_name"
          type="text"
          value={formValues.first_name}
          onChange={handleChange}
          className="form-input"
          placeholder="Ada"
        />
        {errors.first_name && <span className="field-error">{errors.first_name}</span>}
      </div>

      <div className="form-group">
        <label className="form-label" htmlFor="last_name">Last name</label>
        <input
          id="last_name"
          name="last_name"
          type="text"
          value={formValues.last_name}
          onChange={handleChange}
          className="form-input"
          placeholder="Lovelace"
        />
        {errors.last_name && <span className="field-error">{errors.last_name}</span>}
      </div>

      <div className="form-group">
        <label className="form-label" htmlFor="email">Email</label>
        <input
          id="email"
          name="email"
          type="email"
          value={formValues.email}
          onChange={handleChange}
          className="form-input"
          placeholder="ada@example.com"
        />
        {errors.email && <span className="field-error">{errors.email}</span>}
      </div>

      <button type="submit" className="btn btn-primary">
        {submitLabel}
      </button>
    </form>
  );
};

export default AuthorForm;
