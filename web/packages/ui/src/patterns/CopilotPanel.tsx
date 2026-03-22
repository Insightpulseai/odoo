"use client";

import { useState } from "react";

interface CopilotMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  citations?: string[];
}

interface CopilotPanelProps {
  goalId: string;
  goalTitle: string;
}

const PLACEHOLDER_MESSAGES: CopilotMessage[] = [
  {
    id: "msg-001",
    role: "assistant",
    content:
      "I have context for this goal from Odoo. The month-end close for March is in progress with 78% reconciliation coverage. Would you like me to analyze the remaining gaps?",
    citations: ["account.move #2026-03-001", "project.task #close-march-2026"],
  },
];

export function CopilotPanel({ goalId, goalTitle }: CopilotPanelProps) {
  const [messages, setMessages] =
    useState<CopilotMessage[]>(PLACEHOLDER_MESSAGES);
  const [input, setInput] = useState("");

  function handleSend() {
    if (!input.trim()) return;

    const userMsg: CopilotMessage = {
      id: `msg-${Date.now()}`,
      role: "user",
      content: input,
    };

    const assistantMsg: CopilotMessage = {
      id: `msg-${Date.now() + 1}`,
      role: "assistant",
      content:
        "I am analyzing the Odoo context for this goal. This is a placeholder response — the Foundry backend is not yet connected.",
      citations: [],
    };

    setMessages((prev) => [...prev, userMsg, assistantMsg]);
    setInput("");
  }

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="px-4 py-3 border-b">
        <h3 className="text-sm font-medium">Copilot</h3>
        <p className="text-xs text-gray-500 mt-0.5 truncate">{goalTitle}</p>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-auto px-4 py-3 space-y-4">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={
              msg.role === "user"
                ? "ml-8 bg-blue-50 rounded-lg p-3"
                : "mr-4 bg-gray-50 rounded-lg p-3"
            }
          >
            <p className="text-sm">{msg.content}</p>
            {msg.citations && msg.citations.length > 0 && (
              <div className="mt-2 flex flex-wrap gap-1">
                {msg.citations.map((cite, i) => (
                  <span
                    key={i}
                    className="text-xs bg-gray-200 text-gray-600 px-2 py-0.5 rounded"
                  >
                    {cite}
                  </span>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Input */}
      <div className="border-t px-4 py-3">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSend()}
            placeholder="Ask about this goal..."
            className="flex-1 border rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            onClick={handleSend}
            className="px-3 py-2 bg-blue-600 text-white rounded-md text-sm hover:bg-blue-700"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
}
