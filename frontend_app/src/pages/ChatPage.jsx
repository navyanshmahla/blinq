import { useState } from 'react';
import Sidebar from '../components/Sidebar';
import ChatHeader from '../components/ChatHeader';
import MessageList from '../components/MessageList';
import CSVStatus from '../components/CSVStatus';
import ChatInput from '../components/ChatInput';
import { mockConversations, mockMessages } from '../utils/mockData';

function ChatPage() {
  const [conversations] = useState(mockConversations);
  const [activeConversationId, setActiveConversationId] = useState('1');
  const [messages, setMessages] = useState(mockMessages);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);

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

  const handleToggleSidebar = () => {
    setIsSidebarOpen(prev => !prev);
  };

  return (
    <div className="flex h-screen bg-background">
      <Sidebar
        conversations={conversations}
        activeConversationId={activeConversationId}
        onSelectConversation={handleSelectConversation}
        onNewChat={handleNewChat}
        isOpen={isSidebarOpen}
      />

      <div className="flex flex-1 flex-col">
        <ChatHeader
          title={activeConversation?.title}
          isSidebarOpen={isSidebarOpen}
          onToggleSidebar={handleToggleSidebar}
        />

        <div className="flex-1 overflow-hidden">
          <MessageList messages={currentMessages} />
        </div>

        <div className="border-t">
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
