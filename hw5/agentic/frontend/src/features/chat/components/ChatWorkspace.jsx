const formatTimestamp = (timestamp) =>
  new Date(timestamp).toLocaleString(undefined, {
    hour: '2-digit',
    minute: '2-digit',
    month: 'short',
    day: 'numeric',
  });

const roleDesign = {
  user: {
    alignment: 'chat-end',
    bubble: 'bg-primary text-primary-content shadow-primary/40',
  },
  assistant: {
    alignment: 'chat-start',
    bubble: 'bg-base-100 text-base-content shadow-lg',
  },
};

const ChatWorkspace = ({
  isVisible,
  currentConversationId,
  messages,
  messagesStatus,
  sendStatus,
  inputMessage,
  onInputChange,
  onSubmit,
  conversationTitle,
  onTitleChange,
  aiProvider,
  isSendDisabled,
  error,
  messagesEndRef,
}) => {
  const providerLabel = aiProvider.charAt(0).toUpperCase() + aiProvider.slice(1);

  if (!isVisible) {
    return (
      <main className="glass-panel hidden min-h-[28rem] flex-col items-center justify-center p-12 text-center text-base-content/70 lg:flex">
        <div className="space-y-4">
          <div className="inline-flex items-center gap-2 rounded-full bg-primary/10 px-4 py-1 text-sm font-medium text-primary">
            <span className="loading loading-dots loading-sm" />
            Ready when you are
          </div>
          <h2 className="font-display text-2xl font-semibold">Pick a conversation to resume</h2>
          <p className="mx-auto max-w-sm">
            Choose an existing thread from the left panel to continue the dialogue, or launch a fresh conversation to
            explore a new idea.
          </p>
        </div>
      </main>
    );
  }

  const sendingState = sendStatus === 'loading' ? 'Sending…' : null;

  return (
    <main className="glass-panel flex min-h-[28rem] flex-1 flex-col overflow-hidden">
      <header className="flex flex-wrap items-center justify-between gap-4 border-b border-base-200/60 px-8 py-6">
        <div>
          <p className="text-xs uppercase tracking-widest text-base-content/60">
            {currentConversationId ? `Conversation #${currentConversationId}` : 'New conversation'}
          </p>
          <h2 className="font-display text-2xl font-semibold leading-tight">
            {currentConversationId ? 'Active thread' : 'Start something new'}
          </h2>
        </div>
        <div className="flex items-center gap-3 text-sm text-base-content/70">
          {messagesStatus === 'loading' && (
            <span className="badge badge-outline badge-info gap-2 border-info/40 px-3 py-2">
              <span className="loading loading-spinner loading-xs" />
              Loading messages…
            </span>
          )}
          {sendingState && (
            <span className="badge badge-outline badge-warning gap-2 border-warning/40 px-3 py-2">
              <span className="loading loading-spinner loading-xs" />
              {sendingState}
            </span>
          )}
        </div>
      </header>

      <section
        className="scrollbar-thin flex-1 space-y-6 overflow-y-auto bg-gradient-to-b from-base-200/60 via-transparent to-base-100/10 px-8 py-6"
        aria-live="polite"
      >
        {messages.length === 0 ? (
          <div className="h-full min-h-[12rem] rounded-2xl border border-dashed border-base-content/10 p-8 text-center text-base-content/60">
            Compose a message below to seed this conversation.
          </div>
        ) : (
          messages.map((message) => {
            const design = roleDesign[message.role] ?? roleDesign.assistant;
            return (
              <article key={message.id} className={`chat ${design.alignment}`}>
                <div className="chat-header mb-1 text-xs font-semibold uppercase tracking-widest text-base-content/60">
                  {message.role}
                  <time className="ml-2 text-[0.6rem] lowercase opacity-60">
                    {formatTimestamp(message.created_at)}
                  </time>
                </div>
                <div className={`chat-bubble max-w-2xl whitespace-pre-wrap text-left shadow-lg ${design.bubble}`}>
                  {message.content}
                </div>
              </article>
            );
          })
        )}
        <div ref={messagesEndRef} />
      </section>

      <form onSubmit={onSubmit} className="border-t border-base-200/60 bg-base-200/40 px-8 py-6">
        {!currentConversationId && (
          <div className="mb-4 grid gap-4 lg:grid-cols-[2fr_1fr]">
            <label className="form-control">
              <div className="label">
                <span className="label-text text-xs uppercase tracking-widest text-base-content/60">
                  Optional conversation title
                </span>
              </div>
              <input
                type="text"
                className="input input-bordered input-primary"
                placeholder="Launchpad brainstorm"
                value={conversationTitle}
                onChange={(event) => onTitleChange(event.target.value)}
              />
            </label>

            <div className="form-control">
              <div className="label">
                <span className="label-text text-xs uppercase tracking-widest text-base-content/60">
                  AI Provider
                </span>
              </div>
              <div className="badge badge-lg border-primary/40 bg-primary/10 text-primary uppercase">
                {providerLabel}
              </div>
            </div>
          </div>
        )}

        <div className="flex flex-col gap-4 lg:flex-row">
          <label className="form-control flex-1">
            <div className="label">
              <span className="label-text text-xs uppercase tracking-widest text-base-content/60">Your message</span>
            </div>
            <textarea
              className="textarea textarea-bordered min-h-[7rem] resize-y rounded-xl border-base-200/60 bg-base-100/60 shadow-inner"
              placeholder="Ask for insights, craft prompts, or iterate on ideas…"
              value={inputMessage}
              onChange={(event) => onInputChange(event.target.value)}
              required
              rows={3}
              disabled={isSendDisabled}
            />
          </label>

          <div className="flex w-full flex-col justify-end gap-4 lg:w-48">
            <button
              type="submit"
              className="btn btn-primary btn-block h-14 text-lg font-semibold uppercase"
              disabled={isSendDisabled}
            >
              Send
            </button>
            <p className="text-xs text-base-content/50">Shift+Enter for newline. Messages auto-save to the timeline.</p>
          </div>
        </div>
      </form>

      {error && (
        <div className="alert alert-error mx-8 mb-6 shadow-lg">
          <span>{error}</span>
        </div>
      )}
    </main>
  );
};

export default ChatWorkspace;
