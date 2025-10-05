import { createAsyncThunk, createSlice } from '@reduxjs/toolkit';
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

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
    const { data } = await api.get('/chat/conversations', { params: { user_id: userId } });
    return data;
  } catch (error) {
    return rejectWithValue(handleError(error));
  }
});

export const fetchUsers = createAsyncThunk('chat/fetchUsers', async (_, { rejectWithValue }) => {
  try {
    const { data } = await api.get('/chat/users');
    return data;
  } catch (error) {
    return rejectWithValue(handleError(error));
  }
});

export const fetchMessages = createAsyncThunk('chat/fetchMessages', async ({ userId, conversationId }, { rejectWithValue }) => {
  try {
    const { data } = await api.get(`/chat/messages/${conversationId}`, { params: { user_id: userId } });
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
      const { data } = await api.post('/chat/send', payload);

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

export const sendStreamingMessage = createAsyncThunk(
  'chat/sendStreamingMessage',
  async ({ userId, message, conversationId, title, aiProvider }, { dispatch, rejectWithValue }) => {
    try {
      const payload = buildPayload({ userId, message, conversationId, title, aiProvider });
      
      const response = await fetch(`${API_BASE_URL}/chat/send-stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';
      let resultConversationId = null;
      let userMessageData = null;
      let assistantMessageData = null;

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (!line.trim()) continue;
          
          try {
            const event = JSON.parse(line);
            
            switch (event.type) {
              case 'conversation_id':
                resultConversationId = event.conversation_id;
                dispatch(chatSlice.actions.setStreamingConversationId(resultConversationId));
                break;
              
              case 'user_message':
                userMessageData = event.message;
                dispatch(chatSlice.actions.addStreamingUserMessage({
                  conversationId: resultConversationId,
                  message: userMessageData,
                }));
                break;
              
              case 'content':
                dispatch(chatSlice.actions.appendStreamingContent({
                  conversationId: resultConversationId,
                  content: event.content,
                }));
                break;
              
              case 'assistant_message':
                assistantMessageData = event.message;
                break;
              
              case 'error':
                throw new Error(event.message || 'Stream error');
              
              case 'done':
                dispatch(chatSlice.actions.finalizeStreamingMessage({
                  conversationId: resultConversationId,
                  assistantMessage: assistantMessageData,
                }));
                dispatch(fetchConversations({ userId }));
                dispatch(fetchMessages({ userId, conversationId: resultConversationId }));
                break;
            }
          } catch (parseError) {
            console.error('Failed to parse event:', line, parseError);
          }
        }
      }

      return {
        conversationId: resultConversationId,
        userMessage: userMessageData,
        assistantMessage: assistantMessageData,
      };
    } catch (error) {
      return rejectWithValue(error.message || 'Failed to send streaming message');
    }
  }
);

const initialState = {
  users: [],
  usersStatus: 'idle',
  conversations: [],
  conversationsStatus: 'idle',
  messagesByConversation: {},
  messagesStatus: 'idle',
  currentConversationId: null,
  sendStatus: 'idle',
  isStreaming: false,
  streamingConversationId: null,
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
    setStreamingConversationId: (state, action) => {
      state.streamingConversationId = action.payload;
      state.currentConversationId = action.payload;
    },
    addStreamingUserMessage: (state, action) => {
      const { conversationId, message } = action.payload;
      const existing = state.messagesByConversation[conversationId] || [];
      state.messagesByConversation[conversationId] = [...existing, message];
    },
    appendStreamingContent: (state, action) => {
      const { conversationId, content } = action.payload;
      const messages = state.messagesByConversation[conversationId] || [];
      
      let assistantMsg = messages.find(msg => msg.id === 'streaming-assistant');
      if (!assistantMsg) {
        assistantMsg = {
          id: 'streaming-assistant',
          conversation_id: conversationId,
          role: 'assistant',
          content: '',
          created_at: new Date().toISOString(),
        };
        state.messagesByConversation[conversationId] = [...messages, assistantMsg];
      } else {
        const msgIndex = messages.findIndex(msg => msg.id === 'streaming-assistant');
        state.messagesByConversation[conversationId][msgIndex].content += content;
      }
    },
    finalizeStreamingMessage: (state, action) => {
      const { conversationId, assistantMessage } = action.payload;
      const messages = state.messagesByConversation[conversationId] || [];
      
      const filtered = messages.filter(msg => msg.id !== 'streaming-assistant');
      state.messagesByConversation[conversationId] = [...filtered, assistantMessage];
      state.isStreaming = false;
      state.streamingConversationId = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchUsers.pending, (state) => {
        state.usersStatus = 'loading';
        state.error = null;
      })
      .addCase(fetchUsers.fulfilled, (state, action) => {
        state.usersStatus = 'succeeded';
        state.users = action.payload;
      })
      .addCase(fetchUsers.rejected, (state, action) => {
        state.usersStatus = 'failed';
        state.error = action.payload || 'Failed to fetch users.';
      })
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
      })
      .addCase(sendStreamingMessage.pending, (state) => {
        state.sendStatus = 'loading';
        state.isStreaming = true;
        state.error = null;
      })
      .addCase(sendStreamingMessage.fulfilled, (state) => {
        state.sendStatus = 'succeeded';
        state.isStreaming = false;
      })
      .addCase(sendStreamingMessage.rejected, (state, action) => {
        state.sendStatus = 'failed';
        state.isStreaming = false;
        state.streamingConversationId = null;
        state.error = action.payload || 'Failed to send streaming message.';
      });
  },
});

export const { setCurrentConversationId, clearError } = chatSlice.actions;

export const selectUsers = (state) => state.chat.users;
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
  isStreaming: state.chat.isStreaming,
});
export const selectChatError = (state) => state.chat.error;

export default chatSlice.reducer;
