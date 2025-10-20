import { User, Sparkles, BarChart3 } from 'lucide-react';

function Message({ message }) {
  const isUser = message.role === 'user';

  if (isUser) {
    // User message - chat bubble style
    return (
      <div className="w-full px-4 py-3">
        <div className="mx-auto max-w-3xl">
          <div className="flex gap-3 justify-end">
            <div className="flex flex-col items-end max-w-[80%]">
              <div className="rounded-2xl rounded-tr-sm bg-[#2A2622] px-4 py-3 shadow-lg">
                <p className="whitespace-pre-wrap leading-relaxed text-foreground">
                  {message.content}
                </p>
              </div>
            </div>
            <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-blue-500 to-blue-600 text-white shadow-sm ring-2 ring-blue-500/20">
              <User className="h-4 w-4" />
            </div>
          </div>
        </div>
      </div>
    );
  }

  // AI message - no bubble, plain canvas style
  return (
    <div className="w-full px-4 py-6">
      <div className="mx-auto max-w-3xl">
        <div className="flex gap-4">
          <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-orange-400 to-orange-500 text-white shadow-sm ring-2 ring-orange-500/20">
            <Sparkles className="h-4 w-4" />
          </div>

          <div className="flex-1 space-y-3">
            <div className="flex items-center gap-2">
              <span className="text-sm font-semibold">Blinq AI</span>
            </div>

            <div className="prose prose-sm max-w-none dark:prose-invert">
              <p className="whitespace-pre-wrap leading-7 text-foreground/90">
                {message.content}
              </p>
            </div>

            {message.hasPlot && (
              <div className="mt-4 overflow-hidden rounded-lg border border-border bg-card/50">
                <div className="flex items-center gap-2 border-b border-border bg-muted/50 px-4 py-2">
                  <BarChart3 className="h-4 w-4 text-muted-foreground" />
                  <span className="text-sm font-medium text-muted-foreground">
                    Data Visualization
                  </span>
                </div>
                <div className="p-6 text-center text-sm text-muted-foreground">
                  [Chart would render here]
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default Message;
