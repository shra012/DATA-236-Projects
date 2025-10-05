import { useEffect, useMemo, useRef, useState } from 'react';

import {
  clearError,
  fetchConversations,
  fetchMessages,
  fetchUsers,
  selectChatError,
  selectChatStatus,
  selectConversations,
  selectCurrentConversationId,
  selectMessagesForCurrentConversation,
  selectUsers,
  sendMessage,
  sendStreamingMessage,
  setCurrentConversationId,
} from './store/chatSlice';
import { useAppDispatch, useAppSelector } from './store/hooks';

import './App.css';

const DEFAULT_USER_ID = 'user-1';

function App() {
  const dispatch = useAppDispatch();
  const users = useAppSelector(selectUsers);
  const conversations = useAppSelector(selectConversations);
  const messages = useAppSelector(selectMessagesForCurrentConversation);
  const currentConversationId = useAppSelector(selectCurrentConversationId);
  const { conversationsStatus, messagesStatus, sendStatus, isStreaming } = useAppSelector(selectChatStatus);
  const error = useAppSelector(selectChatError);

  const messagesEndRef = useRef(null);
  const [mode, setMode] = useState('new');
  const [userId, setUserId] = useState(DEFAULT_USER_ID);
  const [inputMessage, setInputMessage] = useState('');
  const [conversationTitle, setConversationTitle] = useState('');
  const [aiProvider, setAiProvider] = useState('openai');
  const [responseMode, setResponseMode] = useState('streaming');

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isStreaming]);

  useEffect(() => {
    dispatch(fetchUsers());
  }, [dispatch]);

  useEffect(() => {
    if (mode === 'continue' && users.length > 0) {
      const firstUser = users[0];
      setUserId(firstUser);
      dispatch(fetchConversations({ userId: firstUser }));
    }
  }, [dispatch, mode, users]);

  useEffect(() => {
    if (error) {
      const timer = setTimeout(() => dispatch(clearError()), 4000);
      return () => clearTimeout(timer);
    }
    return undefined;
  }, [dispatch, error]);

  const sortedConversations = useMemo(
    () => [...conversations].sort((a, b) => new Date(b.updated_at || b.created_at) - new Date(a.updated_at || a.created_at)),
    [conversations]
  );

  const handleSelectConversation = (conversationId) => {
    dispatch(setCurrentConversationId(conversationId));
    if (conversationId != null) {
      dispatch(fetchMessages({ userId, conversationId }));
    }
  };

  const handleCreateConversation = () => {
    setMode('new');
    dispatch(setCurrentConversationId(null));
    setConversationTitle('');
    setInputMessage('');
    setAiProvider('openai');
  };

  const handleModeChange = (newMode) => {
    setMode(newMode);
    dispatch(setCurrentConversationId(null));
    setConversationTitle('');
    setInputMessage('');
    if (newMode === 'new') {
      setUserId(DEFAULT_USER_ID);
    } else if (newMode === 'continue' && users.length > 0) {
      const firstUser = users[0];
      setUserId(firstUser);
      dispatch(fetchConversations({ userId: firstUser }));
    }
  };

  const handleUserChange = (newUserId) => {
    setUserId(newUserId);
    if (mode === 'continue' && newUserId.trim()) {
      dispatch(fetchConversations({ userId: newUserId }));
    }
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    const trimmed = inputMessage.trim();
    if (!trimmed || !userId.trim()) {
      return;
    }

    const payload = {
      userId,
      message: trimmed,
      conversationId: currentConversationId,
      title: conversationTitle.trim() || undefined,
      aiProvider: currentConversationId ? undefined : aiProvider,
    };

    if (responseMode === 'streaming') {
      dispatch(sendStreamingMessage(payload));
    } else {
      dispatch(sendMessage(payload));
    }
    
    setInputMessage('');
  };

  const isBusy = conversationsStatus === 'loading' || sendStatus === 'loading' || isStreaming;
  const isSendDisabled = isBusy || !userId.trim();

  return (
    <div className="app">
      <aside className="sidebar">
        <h1 className="sidebar__title">Agentic Chats</h1>

        <div className="sidebar__mode-toggle">
          <button
            className={`sidebar__mode-btn ${mode === 'new' ? 'sidebar__mode-btn--active' : ''}`}
            type="button"
            onClick={() => handleModeChange('new')}
          >
            New Conversation
          </button>
          <button
            className={`sidebar__mode-btn ${mode === 'continue' ? 'sidebar__mode-btn--active' : ''}`}
            type="button"
            onClick={() => handleModeChange('continue')}
          >
            Continue Conversation
          </button>
        </div>

        {mode === 'new' ? (
          <>
            <label className="sidebar__label" htmlFor="userId">
              New User ID
            </label>
            <input
              id="userId"
              className="sidebar__input"
              value={userId}
              onChange={(event) => setUserId(event.target.value)}
              placeholder="Enter new user id"
            />
            
            <div style={{ marginTop: '1rem' }}>
              <label className="sidebar__label" htmlFor="responseModeNew">
                Response Mode
              </label>
              <select
                id="responseModeNew"
                className="sidebar__select"
                value={responseMode}
                onChange={(event) => setResponseMode(event.target.value)}
              >
                <option value="streaming">Streaming (Real-time)</option>
                <option value="fixed">Fixed (Request/Response)</option>
              </select>
            </div>
          </>
        ) : (
          <>
            <label className="sidebar__label" htmlFor="userSelect">
              Select Existing User
            </label>
            <select
              id="userSelect"
              className="sidebar__select"
              value={userId}
              onChange={(event) => handleUserChange(event.target.value)}
            >
              {users.length === 0 ? (
                <option value="">No users found</option>
              ) : (
                users.map((id) => (
                  <option key={id} value={id}>
                    {id}
                  </option>
                ))
              )}
            </select>
            
            <div style={{ marginTop: '1rem' }}>
              <label className="sidebar__label" htmlFor="responseMode">
                Response Mode
              </label>
              <select
                id="responseMode"
                className="sidebar__select"
                value={responseMode}
                onChange={(event) => setResponseMode(event.target.value)}
              >
                <option value="streaming">Streaming (Real-time)</option>
                <option value="fixed">Fixed (Request/Response)</option>
              </select>
            </div>
          </>
        )}

        {mode === 'continue' && (
          <>
            <button className="sidebar__button sidebar__button--new" type="button" onClick={handleCreateConversation}>
              + New Conversation
            </button>

            <div className="sidebar__list" role="list">
              {conversationsStatus === 'loading' && <p className="sidebar__hint">Loading conversations…</p>}
              {sortedConversations.map((conversation) => (
                <button
                  key={conversation.id}
                  type="button"
                  className={`sidebar__item ${currentConversationId === conversation.id ? 'sidebar__item--active' : ''}`}
                  onClick={() => handleSelectConversation(conversation.id)}
                >
                  <div className="sidebar__item-header">
                    <span className="sidebar__item-title">{conversation.title || `Conversation ${conversation.id}`}</span>
                    {conversation.ai_provider && (
                      <span className={`sidebar__item-badge sidebar__item-badge--${conversation.ai_provider}`}>
                        {conversation.ai_provider === 'openai' ? 'gpt-4o-mini' : 'claude-3-5-haiku'}
                      </span>
                    )}
                  </div>
                  <span className="sidebar__item-meta">{new Date(conversation.updated_at || conversation.created_at).toLocaleString()}</span>
                </button>
              ))}
              {!sortedConversations.length && conversationsStatus === 'succeeded' && (
                <p className="sidebar__hint">No conversations yet.</p>
              )}
            </div>
          </>
        )}
      </aside>

      {(mode === 'new' || currentConversationId) && (
        <main className="chat">
          <header className="chat__header">
            <h2 className="chat__title">
              {currentConversationId ? `Conversation #${currentConversationId}` : 'Start a new conversation'}
            </h2>
            {messagesStatus === 'loading' && <span className="chat__status">Loading messages…</span>}
            {isStreaming && <span className="chat__status">Streaming response…</span>}
            {sendStatus === 'loading' && !isStreaming && <span className="chat__status">Sending…</span>}
          </header>

          <section className="chat__messages" aria-live="polite">
            {messages.length === 0 && (
              <p className="chat__hint">No messages yet. Send a message to begin chatting.</p>
            )}
            {messages.map((message) => (
              <article key={`${message.id}`} className={`chat__message chat__message--${message.role}`}>
                <div className="chat__message-role">{message.role}</div>
                <div className="chat__message-content">{message.content}</div>
                <time className="chat__message-time">{new Date(message.created_at).toLocaleString()}</time>
              </article>
            ))}
            <div ref={messagesEndRef} />
          </section>

          <form className="chat__composer" onSubmit={handleSubmit}>
            {!currentConversationId && (
              <>
                <input
                  className="chat__title-input"
                  placeholder="Optional title for the new conversation"
                  value={conversationTitle}
                  onChange={(event) => setConversationTitle(event.target.value)}
                />
                <div className="chat__ai-provider">
                  <label htmlFor="ai-provider" className="chat__ai-provider-label">
                    AI Provider:
                  </label>
                  <select
                    id="ai-provider"
                    className="chat__ai-provider-select"
                    value={aiProvider}
                    onChange={(event) => setAiProvider(event.target.value)}
                  >
                    <option value="openai">gpt-4o-mini</option>
                    <option value="anthropic">claude-3-5-haiku-latest</option>
                  </select>
                </div>
              </>
            )}
            <textarea
              className="chat__input"
              placeholder="Type your message…"
              value={inputMessage}
              onChange={(event) => setInputMessage(event.target.value)}
              required
              rows={3}
              disabled={isSendDisabled}
            />
            <button className="chat__send" type="submit" disabled={isSendDisabled}>
              Send
            </button>
          </form>

          {error && <div className="chat__error">{error}</div>}
        </main>
      )}

      {mode === 'continue' && !currentConversationId && (
        <main className="chat">
          <div className="chat__hint" style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-muted)' }}>
            Select a conversation from the list to continue chatting
          </div>
        </main>
      )}
    </div>
  );
}

export default App;
