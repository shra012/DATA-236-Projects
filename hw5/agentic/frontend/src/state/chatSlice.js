import { createAsyncThunk, createSlice } from '@reduxjs/toolkit';
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const API_PREFIX = '/api/v1/conversations';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
});

const buildPayload = ({ userId, message, conversationId, title, aiProvider }) => ({
  user_id: userId,
  message,
  ...(conversationId && { conversation_id: conversationId }),
  ...(title && { title }),
  ...(aiProvider && { ai_provider: aiProvider }),
});

const handleError = (error) => error.response?.data?.detail || error.message;

export const fetchConversations = createAsyncThunk('chat/fetchConversations', async ({ userId }, { rejectWithValue }) => {
  try {
    const { data } = await api.get(API_PREFIX, { params: { user_id: userId } });
    return data;
  } catch (error) {
    return rejectWithValue(handleError(error));
  }
});

export const fetchMessages = createAsyncThunk('chat/fetchMessages', async ({ userId, conversationId }, { rejectWithValue }) => {
  try {
    const { data } = await api.get(`${API_PREFIX}/${conversationId}/messages`, { params: { user_id: userId } });
    return data;
  } catch (error) {
    return rejectWithValue(handleError(error));
  }
});

export const sendMessage = createAsyncThunk(
  'chat/sendMessage',
  async ({ userId, message, conversationId, title, aiProvider }, { dispatch, rejectWithValue }) => {
    try {
      const payload = buildPayload({ userId, message, conversationId, title, aiProvider });
      const { data } = await api.post(`${API_PREFIX}/messages`, payload);

      dispatch(fetchConversations({ userId }));
      dispatch(fetchMessages({ userId, conversationId: data.conversation_id }));

      return {
        conversationId: data.conversation_id,
        userMessage: message,
        assistantMessage: data.reply,
      };
    } catch (error) {
      return rejectWithValue(handleError(error));
    }
  }
);

const initialState = {
  conversations: [],
  conversationsStatus: 'idle',
  messagesByConversation: {},
  messagesStatus: 'idle',
  currentConversationId: null,
  sendStatus: 'idle',
  error: null,
};

const chatSlice = createSlice({
  name: 'chat',
  initialState,
  reducers: {
    setCurrentConversationId: (state, action) => {
      state.currentConversationId = action.payload;
    },
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchConversations.pending, (state) => {
        state.conversationsStatus = 'loading';
        state.error = null;
      })
      .addCase(fetchConversations.fulfilled, (state, action) => {
        state.conversationsStatus = 'succeeded';
        state.conversations = action.payload;
      })
      .addCase(fetchConversations.rejected, (state, action) => {
        state.conversationsStatus = 'failed';
        state.error = action.payload || 'Failed to fetch conversations.';
      })
      .addCase(fetchMessages.pending, (state) => {
        state.messagesStatus = 'loading';
        state.error = null;
      })
      .addCase(fetchMessages.fulfilled, (state, action) => {
        state.messagesStatus = 'succeeded';
        const { conversation_id, messages } = action.payload;
        state.messagesByConversation[conversation_id] = messages;
      })
      .addCase(fetchMessages.rejected, (state, action) => {
        state.messagesStatus = 'failed';
        state.error = action.payload || 'Failed to fetch messages.';
      })
      .addCase(sendMessage.pending, (state) => {
        state.sendStatus = 'loading';
        state.error = null;
      })
      .addCase(sendMessage.fulfilled, (state, action) => {
        state.sendStatus = 'succeeded';
        const { conversationId, userMessage, assistantMessage } = action.payload;
        state.currentConversationId = conversationId;
        const existing = state.messagesByConversation[conversationId] || [];
        const now = new Date().toISOString();
        const baseId = Date.now();
        const userEntry = {
          id: `user-${baseId}`,
          conversation_id: conversationId,
          role: 'user',
          content: userMessage,
          created_at: now,
        };
        const assistantEntry = {
          id: `assistant-${baseId}`,
          conversation_id: conversationId,
          role: 'assistant',
          content: assistantMessage,
          created_at: now,
        };
        state.messagesByConversation[conversationId] = [...existing, userEntry, assistantEntry];
      })
      .addCase(sendMessage.rejected, (state, action) => {
        state.sendStatus = 'failed';
        state.error = action.payload || 'Failed to send message.';
      });
  },
});

export const { setCurrentConversationId, clearError } = chatSlice.actions;

export const selectConversations = (state) => state.chat.conversations;
export const selectMessagesForCurrentConversation = (state) => {
  const conversationId = state.chat.currentConversationId;
  if (!conversationId) {
    return [];
  }
  return state.chat.messagesByConversation[conversationId] || [];
};
export const selectCurrentConversationId = (state) => state.chat.currentConversationId;
export const selectChatStatus = (state) => ({
  conversationsStatus: state.chat.conversationsStatus,
  messagesStatus: state.chat.messagesStatus,
  sendStatus: state.chat.sendStatus,
});
export const selectChatError = (state) => state.chat.error;

export default chatSlice.reducer;
