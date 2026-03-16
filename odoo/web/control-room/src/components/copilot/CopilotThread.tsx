'use client';

import { useEffect, useRef } from "react";
import { CopilotMessage } from "./types";
import { CopilotMessageBubble } from "./CopilotMessage";

interface Props {
  messages: CopilotMessage[];
  isLoading: boolean;
}

export function CopilotThread({ messages, isLoading }: Props) {
  const bottomRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages.length, isLoading]);

  return (
    <div className="flex-1 overflow-y-auto px-4 py-3 space-y-2 bg-surface-900/40">
      {messages.length === 0 && (
        <div className="mt-6 rounded-2xl border border-dashed border-surface-600 bg-surface-800/80 px-4 py-3 text-xs text-surface-300">
          Ask a question about this record, or pick a quick action below to get started.
        </div>
      )}

      {messages.map((m, idx) => (
        <CopilotMessageBubble
          key={m.id}
          message={m}
          isLast={idx === messages.length - 1}
        />
      ))}

      {isLoading && (
        <div className="flex items-center gap-2 text-xs text-surface-400 mt-2">
          <span className="h-2 w-2 rounded-full bg-primary-500 animate-pulse" />
          <span>Copilot is thinking...</span>
        </div>
      )}

      <div ref={bottomRef} />
    </div>
  );
}
