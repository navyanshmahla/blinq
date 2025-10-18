import '../styles/chat.css';

function ChatHeader({ title }) {
  return (
    <div className="chat-header">
      <h2 className="chat-title">{title || 'New Conversation'}</h2>
    </div>
  );
}

export default ChatHeader;
