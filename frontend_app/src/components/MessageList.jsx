import { useEffect, useRef } from 'react';
import Message from './Message';
import '../styles/chat.css';

function MessageList({ messages }) {
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  if (!messages || messages.length === 0) {
    return (
      <div className="messages-container">
        <div className="empty-messages">
          <h3>Start a conversation</h3>
          <p>Upload a CSV file and ask questions about your data</p>
        </div>
      </div>
    );
  }

  return (
    <div className="messages-container">
      {messages.map((message) => (
        <Message key={message.id} message={message} />
      ))}
      <div ref={messagesEndRef} />
    </div>
  );
}

export default MessageList;
