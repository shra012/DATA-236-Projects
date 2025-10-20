import { useEffect, useMemo, useRef, useState } from 'react';

import {
  clearError,
  fetchConversations,
  fetchMessages,
  selectChatError,
  selectChatStatus,
  selectConversations,
  selectCurrentConversationId,
  selectMessagesForCurrentConversation,
  sendMessage,
  setCurrentConversationId,
} from '../../state/chatSlice';
import { useAppDispatch, useAppSelector } from '../../state/hooks';
import ConversationSidebar from './components/ConversationSidebar';
import ChatWorkspace from './components/ChatWorkspace';

const DEFAULT_USER_ID = 'mission-control';

const ChatDashboard = () => {
  const dispatch = useAppDispatch();
  const conversations = useAppSelector(selectConversations);
  const messages = useAppSelector(selectMessagesForCurrentConversation);
  const currentConversationId = useAppSelector(selectCurrentConversationId);
  const { conversationsStatus, messagesStatus, sendStatus } = useAppSelector(selectChatStatus);
  const error = useAppSelector(selectChatError);

  const messagesEndRef = useRef(null);
  const [inputMessage, setInputMessage] = useState('');
  const [conversationTitle, setConversationTitle] = useState('');
  const aiProvider = 'gemini';
  const aiProviderLabel = 'Gemini';

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  useEffect(() => {
    dispatch(fetchConversations({ userId: DEFAULT_USER_ID }));
  }, [dispatch]);

  useEffect(() => {
    if (error) {
      const timer = setTimeout(() => dispatch(clearError()), 4000);
      return () => clearTimeout(timer);
    }
    return undefined;
  }, [dispatch, error]);

  const sortedConversations = useMemo(
    () =>
      [...conversations].sort(
        (a, b) => new Date(b.updated_at || b.created_at) - new Date(a.updated_at || a.created_at)
      ),
    [conversations]
  );

  const handleSelectConversation = (conversationId) => {
    dispatch(setCurrentConversationId(conversationId));
    if (conversationId != null) {
      dispatch(fetchMessages({ userId: DEFAULT_USER_ID, conversationId }));
    }
  };

  const handleCreateConversation = () => {
    dispatch(setCurrentConversationId(null));
    setConversationTitle('');
    setInputMessage('');
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    const trimmed = inputMessage.trim();
    if (!trimmed) {
      return;
    }

    const payload = {
      userId: DEFAULT_USER_ID,
      message: trimmed,
      conversationId: currentConversationId,
      title: conversationTitle.trim() || undefined,
      aiProvider,
    };

    dispatch(sendMessage(payload));

    setInputMessage('');
  };

  const isBusy = conversationsStatus === 'loading' || sendStatus === 'loading';
  const isSendDisabled = isBusy;
  const isChatVisible = true;

  return (
    <div className="relative min-h-screen w-full overflow-hidden bg-gradient-to-br from-sky-50 via-white to-indigo-50">
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_top,_rgba(37,99,235,0.15),_transparent_60%)]" />
      <div className="pointer-events-none absolute inset-y-0 right-0 w-1/2 bg-[radial-gradient(circle_at_center,_rgba(124,58,237,0.12),_transparent_55%)]" />

      <div className="relative z-10 mx-auto flex min-h-screen max-w-7xl flex-col gap-8 px-4 py-10 md:px-8 lg:px-12">
        <nav className="flex flex-wrap items-center justify-between gap-4 rounded-3xl border border-base-200 bg-white/90 px-6 py-4 shadow-lg backdrop-blur">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-primary/10 text-primary">
              <span className="font-display text-lg font-semibold">AG</span>
            </div>
            <div>
              <p className="text-xs uppercase tracking-widest text-neutral">Agentic AI Ops</p>
              <h1 className="font-display text-xl font-semibold text-neutral">Mission Control</h1>
            </div>
          </div>
          <div className="flex items-center gap-3 text-sm text-neutral/80">
            <span className="badge badge-outline border-primary/40 bg-primary/10 text-primary uppercase">
              {aiProviderLabel}
            </span>
            <span className="badge badge-outline border-base-300 bg-base-100 text-neutral">
              Request/Response
            </span>
          </div>
        </nav>

        <div className="grid flex-1 gap-6 lg:grid-cols-[24rem_1fr]">
          <ConversationSidebar
            defaultUserId={DEFAULT_USER_ID}
            onCreateConversation={handleCreateConversation}
            conversations={sortedConversations}
            conversationsStatus={conversationsStatus}
            currentConversationId={currentConversationId}
            onSelectConversation={handleSelectConversation}
          />

          <ChatWorkspace
            isVisible={isChatVisible}
            currentConversationId={currentConversationId}
            messages={messages}
            messagesStatus={messagesStatus}
            sendStatus={sendStatus}
            inputMessage={inputMessage}
            onInputChange={setInputMessage}
            onSubmit={handleSubmit}
            conversationTitle={conversationTitle}
            onTitleChange={setConversationTitle}
            aiProvider={aiProvider}
            isSendDisabled={isSendDisabled}
            error={error}
            messagesEndRef={messagesEndRef}
          />
        </div>
      </div>
    </div>
  );
};

export default ChatDashboard;
