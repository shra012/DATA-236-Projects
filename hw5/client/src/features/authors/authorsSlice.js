import { createAsyncThunk, createSlice } from '@reduxjs/toolkit';
import api from '../../app/api';
import { handleApiError } from '../../app/apiUtils';

const initialState = {
  items: [],
  total: 0,
  status: 'idle',
  error: null,
  selectedAuthor: null,
  currentPage: 1,
  itemsPerPage: 9,
};

export const fetchAuthors = createAsyncThunk(
  'authors/fetchAuthors',
  async ({ skip = 0, limit = 10 } = {}, { rejectWithValue }) => {
    try {
      const response = await api.get('/authors', { params: { skip, limit } });
      return response.data;
    } catch (error) {
      return rejectWithValue(handleApiError(error));
    }
  }
);

export const fetchAuthorById = createAsyncThunk(
  'authors/fetchAuthorById',
  async (id, { rejectWithValue }) => {
    try {
      const response = await api.get(`/authors/${id}`);
      return response.data;
    } catch (error) {
      return rejectWithValue(handleApiError(error));
    }
  }
);

export const createAuthor = createAsyncThunk(
  'authors/createAuthor',
  async (payload, { rejectWithValue }) => {
    try {
      const response = await api.post('/authors', payload);
      return response.data;
    } catch (error) {
      return rejectWithValue(handleApiError(error));
    }
  }
);

export const updateAuthor = createAsyncThunk(
  'authors/updateAuthor',
  async ({ id, data }, { rejectWithValue }) => {
    try {
      const response = await api.put(`/authors/${id}`, data);
      return response.data;
    } catch (error) {
      return rejectWithValue(handleApiError(error));
    }
  }
);

export const deleteAuthor = createAsyncThunk(
  'authors/deleteAuthor',
  async (id, { rejectWithValue }) => {
    try {
      await api.delete(`/authors/${id}`);
      return id;
    } catch (error) {
      return rejectWithValue(handleApiError(error));
    }
  }
);

const authorsSlice = createSlice({
  name: 'authors',
  initialState,
  reducers: {
    clearSelectedAuthor: (state) => {
      state.selectedAuthor = null;
    },
    setCurrentPage: (state, action) => {
      state.currentPage = action.payload;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchAuthors.pending, (state) => {
        state.status = 'loading';
        state.error = null;
      })
      .addCase(fetchAuthors.fulfilled, (state, action) => {
        state.status = 'succeeded';
        state.items = action.payload.items;
        state.total = action.payload.total;
      })
      .addCase(fetchAuthors.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.payload || 'Unable to fetch authors';
      })
      .addCase(fetchAuthorById.pending, (state) => {
        state.status = 'loading';
        state.error = null;
      })
      .addCase(fetchAuthorById.fulfilled, (state, action) => {
        state.status = 'succeeded';
        state.selectedAuthor = action.payload;
        const existing = state.items.find((author) => author.id === action.payload.id);
        if (!existing) {
          state.items.push(action.payload);
        }
      })
      .addCase(fetchAuthorById.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.payload || 'Unable to load author';
      })
      .addCase(createAuthor.pending, (state) => {
        state.status = 'loading';
        state.error = null;
      })
      .addCase(createAuthor.fulfilled, (state, action) => {
        state.items.push(action.payload);
        state.total += 1;
        state.status = 'succeeded';
        state.error = null;
      })
      .addCase(createAuthor.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.payload || 'Unable to create author';
      })
      .addCase(updateAuthor.pending, (state) => {
        state.status = 'loading';
        state.error = null;
      })
      .addCase(updateAuthor.fulfilled, (state, action) => {
        state.items = state.items.map((author) =>
          author.id === action.payload.id ? action.payload : author
        );
        state.selectedAuthor = action.payload;
        state.status = 'succeeded';
        state.error = null;
      })
      .addCase(updateAuthor.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.payload || 'Unable to update author';
      })
      .addCase(deleteAuthor.pending, (state) => {
        state.error = null;
      })
      .addCase(deleteAuthor.fulfilled, (state, action) => {
        state.items = state.items.filter((author) => author.id !== action.payload);
        state.total = Math.max(0, state.total - 1);
        if (state.selectedAuthor?.id === action.payload) {
          state.selectedAuthor = null;
        }
        state.error = null;
      })
      .addCase(deleteAuthor.rejected, (state, action) => {
        state.error = action.payload || 'Unable to delete author';
      });
  },
});

export const { clearSelectedAuthor, setCurrentPage } = authorsSlice.actions;

export default authorsSlice.reducer;
