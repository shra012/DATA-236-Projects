const ConversationSidebar = ({
  defaultUserId,
  onCreateConversation,
  conversations,
  conversationsStatus,
  currentConversationId,
  onSelectConversation,
}) => (
  <aside className="glass-panel flex h-full flex-col gap-6 p-6">
    <header className="space-y-1">
      <p className="text-sm uppercase tracking-widest text-primary/80">Agentic Playground</p>
      <h1 className="font-display text-3xl font-semibold leading-tight">Conversation Studio</h1>
      <p className="text-sm text-base-content/70">
        You’re conversing as <span className="font-semibold text-primary">{defaultUserId}</span>. Launch fresh threads or
        revisit previous exchanges from the list below.
      </p>
    </header>

    <div className="flex flex-col gap-4">
      <button type="button" className="btn btn-outline btn-primary" onClick={onCreateConversation}>
        + Start new conversation
      </button>

      <div className="divider m-0 text-xs uppercase text-base-content/50">Conversation history</div>

      <div className="scrollbar-thin flex-1 space-y-3 overflow-y-auto pr-1">
        {conversationsStatus === 'loading' && (
          <div className="alert alert-info glass text-sm">
            <span>Loading conversation history…</span>
          </div>
        )}

        {conversations.map((conversation) => {
          const displayTitle = conversation.title || `Conversation ${conversation.id}`;
          const isActive = currentConversationId === conversation.id;
          return (
            <button
              key={conversation.id}
              type="button"
              className={`w-full rounded-xl border border-base-200 bg-base-100/60 p-4 text-left transition hover:border-primary/50 hover:shadow-lg ${
                isActive ? 'border-primary shadow-primary/20' : ''
              }`}
              onClick={() => onSelectConversation(conversation.id)}
            >
              <div className="flex items-start justify-between gap-2">
                <span className="font-semibold">{displayTitle}</span>
                <span className="badge badge-sm badge-outline border-primary/60 text-primary/80">Gemini</span>
              </div>
              <p className="mt-2 text-xs text-base-content/60">
                {new Date(conversation.updated_at || conversation.created_at).toLocaleString()}
              </p>
            </button>
          );
        })}

        {conversationsStatus === 'succeeded' && conversations.length === 0 && (
          <div className="rounded-xl border border-dashed border-base-content/20 p-6 text-center text-sm text-base-content/60">
            No conversations yet. Send a message to seed a new thread.
          </div>
        )}
      </div>
    </div>
  </aside>
);

export default ConversationSidebar;
