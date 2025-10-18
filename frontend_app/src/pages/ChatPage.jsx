import { useState } from 'react';
import Sidebar from '../components/Sidebar';
import ChatHeader from '../components/ChatHeader';
import MessageList from '../components/MessageList';
import CSVStatus from '../components/CSVStatus';
import ChatInput from '../components/ChatInput';
import { mockConversations, mockMessages } from '../utils/mockData';
import '../styles/chat.css';

function ChatPage() {
  const [conversations] = useState(mockConversations);
  const [activeConversationId, setActiveConversationId] = useState('1');
  const [messages, setMessages] = useState(mockMessages);

  const activeConversation = conversations.find(c => c.id === activeConversationId);
  const currentMessages = messages[activeConversationId] || [];

  const handleSelectConversation = (id) => {
    setActiveConversationId(id);
  };

  const handleNewChat = () => {
    console.log('New chat clicked');
  };

  const handleSendMessage = (content) => {
    const newMessage = {
      id: `m${Date.now()}`,
      role: 'user',
      content,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => ({
      ...prev,
      [activeConversationId]: [...(prev[activeConversationId] || []), newMessage]
    }));
  };

  return (
    <div className="chat-page">
      <Sidebar
        conversations={conversations}
        activeConversationId={activeConversationId}
        onSelectConversation={handleSelectConversation}
        onNewChat={handleNewChat}
      />

      <div className="chat-main">
        <ChatHeader title={activeConversation?.title} />

        <MessageList messages={currentMessages} />

        <div className="chat-bottom">
          <CSVStatus
            csvStatus={activeConversation?.csvStatus}
            csvFilename={activeConversation?.csvFilename}
            csvExpiry={activeConversation?.csvExpiry}
          />
          <ChatInput onSendMessage={handleSendMessage} />
        </div>
      </div>
    </div>
  );
}

export default ChatPage;
