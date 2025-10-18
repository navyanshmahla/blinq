import '../styles/chat.css';

function Sidebar({ conversations, activeConversationId, onSelectConversation, onNewChat }) {
  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffDays = Math.floor((now - date) / (1000 * 60 * 60 * 24));

    if (diffDays === 0) return 'Today';
    if (diffDays === 1) return 'Yesterday';
    if (diffDays < 7) return `${diffDays} days ago`;
    return date.toLocaleDateString();
  };

  return (
    <div className="sidebar">
      <button className="new-chat-btn" onClick={onNewChat}>
        <span className="plus-icon">+</span>
        New Chat
      </button>

      <div className="conversations-list">
        {conversations.map((conv) => (
          <div
            key={conv.id}
            className={`conversation-item ${conv.id === activeConversationId ? 'active' : ''}`}
            onClick={() => onSelectConversation(conv.id)}
          >
            <div className="conversation-title">{conv.title}</div>
            <div className="conversation-timestamp">{formatTimestamp(conv.timestamp)}</div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default Sidebar;
