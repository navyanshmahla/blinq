import { useEffect, useRef } from 'react';
import Message from './Message';
import { FileSpreadsheet, Sparkles } from 'lucide-react';

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
      <div className="flex h-full items-center justify-center p-8">
        <div className="text-center space-y-4 max-w-md">
          <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-gradient-to-br from-orange-400 to-orange-500 text-white shadow-lg">
            <Sparkles className="h-8 w-8" />
          </div>
          <div className="space-y-2">
            <h3 className="text-2xl font-semibold">Welcome to Blinq</h3>
            <p className="text-muted-foreground">
              Upload a CSV file and start asking questions about your data. I'll help you analyze, visualize, and understand your datasets.
            </p>
          </div>
          <div className="flex items-center justify-center gap-2 text-sm text-muted-foreground pt-4">
            <FileSpreadsheet className="h-4 w-4" />
            <span>Upload a CSV to get started</span>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full overflow-y-auto">
      {messages.map((message) => (
        <Message key={message.id} message={message} />
      ))}
      <div ref={messagesEndRef} />
    </div>
  );
}

export default MessageList;
