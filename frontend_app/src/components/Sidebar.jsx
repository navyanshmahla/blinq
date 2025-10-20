import { Button } from './ui/button';
import { Card } from './ui/card';
import { Plus, MessageSquare } from 'lucide-react';
import { cn } from '@/lib/utils';

function Sidebar({ conversations, activeConversationId, onSelectConversation, onNewChat, isOpen }) {
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
    <div
      className={cn(
        "flex h-full flex-col border-r bg-muted/10 p-4 transition-all duration-300 ease-in-out",
        isOpen ? "w-64" : "w-0 p-0 border-0 overflow-hidden"
      )}
    >
      <Button onClick={onNewChat} className="mb-4 w-full justify-start gap-2">
        <Plus className="h-4 w-4" />
        New Chat
      </Button>

      <div className="flex-1 space-y-2 overflow-y-auto">
        {conversations.map((conv) => (
          <Card
            key={conv.id}
            className={cn(
              "cursor-pointer p-3 transition-all hover:shadow-md",
              conv.id === activeConversationId
                ? "border-primary bg-accent"
                : "hover:bg-accent/50"
            )}
            onClick={() => onSelectConversation(conv.id)}
          >
            <div className="flex items-start gap-2">
              <MessageSquare className="h-4 w-4 mt-1 text-muted-foreground shrink-0" />
              <div className="flex-1 min-w-0">
                <div className="font-medium text-sm truncate">{conv.title}</div>
                <div className="text-xs text-muted-foreground mt-1">
                  {formatTimestamp(conv.timestamp)}
                </div>
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}

export default Sidebar;
