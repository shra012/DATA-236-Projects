import axios from 'axios';

const API_BASE_URL = 'http://localhost:3001/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
});

export const bookService = {
  getAllBooks: async () => {
    const response = await api.get('/books');
    return response.data.data;
  },
  getBookById: async (id) => {
    const response = await api.get(`/books/${id}`);
    return response.data.data;
  },
  createBook: async (bookData) => {
    const response = await api.post('/books', bookData);
    return response.data.data;
  },
  updateBook: async (id, bookData) => {
    const response = await api.put(`/books/${id}`, bookData);
    return response.data.data;
  },
  deleteBook: async (id) => {
    await api.delete(`/books/${id}`);
  },
};

export default bookService;
