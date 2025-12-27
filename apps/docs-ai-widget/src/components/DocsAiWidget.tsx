// InsightPulse Docs AI Widget
// Embeddable React component for documentation Q&A

import React, { useState, useRef, useEffect } from "react";

type Message = {
  id: string;
  role: "user" | "assistant";
  content: string;
  citations?: Citation[];
  confidence?: number;
  timestamp: Date;
};

type Citation = {
  document_id: string;
  url: string | null;
  title: string | null;
  score: number;
};

export type DocsAiWidgetProps = {
  apiUrl: string; // Supabase Edge Function URL
  tenantId: string;
  surface?: string; // 'docs', 'product', 'support', etc.
  userId?: string | null;
  initialContext?: Record<string, unknown>;
  // Theming
  primaryColor?: string;
  position?: "bottom-right" | "bottom-left";
  title?: string;
  placeholder?: string;
  welcomeMessage?: string;
};

export const DocsAiWidget: React.FC<DocsAiWidgetProps> = ({
  apiUrl,
  tenantId,
  surface = "docs",
  userId = null,
  initialContext = {},
  primaryColor = "#2563eb",
  position = "bottom-right",
  title = "Ask AI",
  placeholder = "Ask a question...",
  welcomeMessage = "Hi! I can help you find answers in our documentation. What would you like to know?",
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Add welcome message on first open
  useEffect(() => {
    if (isOpen && messages.length === 0) {
      setMessages([
        {
          id: "welcome",
          role: "assistant",
          content: welcomeMessage,
          timestamp: new Date(),
        },
      ]);
    }
  }, [isOpen, welcomeMessage, messages.length]);

  const handleAsk = async (e: React.FormEvent) => {
    e.preventDefault();
    const question = input.trim();
    if (!question || loading) return;

    setErrorMsg(null);
    const userMessage: Message = {
      id: `user-${Date.now()}`,
      role: "user",
      content: question,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      const context = {
        ...initialContext,
        url: typeof window !== "undefined" ? window.location.href : undefined,
        path: typeof window !== "undefined" ? window.location.pathname : undefined,
      };

      const res = await fetch(apiUrl, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          question,
          tenantId,
          surface,
          userId,
          context,
        }),
      });

      if (!res.ok) {
        const errorData = await res.json().catch(() => ({}));
        throw new Error(errorData.error || `API error: ${res.status}`);
      }

      const data = await res.json();

      const assistantMessage: Message = {
        id: `assistant-${Date.now()}`,
        role: "assistant",
        content: data.answer || "Sorry, I couldn't generate an answer.",
        citations: data.citations || [],
        confidence: data.confidence,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      console.error("DocsAiWidget error:", err);
      setErrorMsg(err instanceof Error ? err.message : "Something went wrong. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleFeedback = async (messageId: string, score: number) => {
    // TODO: Implement feedback submission
    console.log("Feedback:", messageId, score);
  };

  const positionStyles =
    position === "bottom-left"
      ? { left: 20, right: "auto" }
      : { right: 20, left: "auto" };

  if (!isOpen) {
    return (
      <button
        onClick={() => setIsOpen(true)}
        style={{
          position: "fixed",
          bottom: 20,
          ...positionStyles,
          width: 56,
          height: 56,
          borderRadius: "50%",
          backgroundColor: primaryColor,
          color: "#fff",
          border: "none",
          cursor: "pointer",
          boxShadow: "0 4px 12px rgba(0,0,0,0.15)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          zIndex: 9999,
          transition: "transform 0.2s, box-shadow 0.2s",
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.transform = "scale(1.05)";
          e.currentTarget.style.boxShadow = "0 6px 16px rgba(0,0,0,0.2)";
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.transform = "scale(1)";
          e.currentTarget.style.boxShadow = "0 4px 12px rgba(0,0,0,0.15)";
        }}
        aria-label="Open AI Assistant"
      >
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
        </svg>
      </button>
    );
  }

  return (
    <div
      style={{
        position: "fixed",
        bottom: 20,
        ...positionStyles,
        width: 380,
        height: 520,
        display: "flex",
        flexDirection: "column",
        borderRadius: 16,
        border: "1px solid rgba(0,0,0,0.1)",
        boxShadow: "0 8px 32px rgba(0,0,0,0.16)",
        overflow: "hidden",
        backgroundColor: "#ffffff",
        fontFamily: "system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
        fontSize: 14,
        zIndex: 9999,
      }}
    >
      {/* Header */}
      <div
        style={{
          padding: "14px 16px",
          backgroundColor: primaryColor,
          color: "#fff",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="12" r="10" />
            <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3" />
            <line x1="12" y1="17" x2="12.01" y2="17" />
          </svg>
          <span style={{ fontWeight: 600 }}>{title}</span>
        </div>
        <button
          onClick={() => setIsOpen(false)}
          style={{
            background: "none",
            border: "none",
            color: "#fff",
            cursor: "pointer",
            padding: 4,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
          aria-label="Close"
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <line x1="18" y1="6" x2="6" y2="18" />
            <line x1="6" y1="6" x2="18" y2="18" />
          </svg>
        </button>
      </div>

      {/* Messages */}
      <div
        style={{
          flex: 1,
          padding: "12px 16px",
          overflowY: "auto",
          display: "flex",
          flexDirection: "column",
          gap: 12,
        }}
      >
        {messages.map((m) => (
          <div
            key={m.id}
            style={{
              alignSelf: m.role === "user" ? "flex-end" : "flex-start",
              maxWidth: "85%",
            }}
          >
            <div
              style={{
                padding: "10px 14px",
                borderRadius: 12,
                backgroundColor:
                  m.role === "user" ? primaryColor : "#f3f4f6",
                color: m.role === "user" ? "#fff" : "#111",
                whiteSpace: "pre-wrap",
                lineHeight: 1.5,
              }}
            >
              {m.content}
            </div>

            {/* Citations */}
            {m.citations && m.citations.length > 0 && (
              <div style={{ marginTop: 8 }}>
                <div style={{ fontSize: 11, color: "#6b7280", marginBottom: 4 }}>
                  Sources:
                </div>
                <div style={{ display: "flex", flexWrap: "wrap", gap: 4 }}>
                  {m.citations.slice(0, 3).map((c, i) => (
                    <a
                      key={i}
                      href={c.url || "#"}
                      target="_blank"
                      rel="noopener noreferrer"
                      style={{
                        fontSize: 11,
                        color: primaryColor,
                        textDecoration: "none",
                        padding: "2px 6px",
                        backgroundColor: `${primaryColor}10`,
                        borderRadius: 4,
                      }}
                    >
                      {c.title || `Source ${i + 1}`}
                    </a>
                  ))}
                </div>
              </div>
            )}

            {/* Feedback buttons for assistant messages */}
            {m.role === "assistant" && m.id !== "welcome" && (
              <div style={{ marginTop: 6, display: "flex", gap: 8 }}>
                <button
                  onClick={() => handleFeedback(m.id, 1)}
                  style={{
                    background: "none",
                    border: "none",
                    cursor: "pointer",
                    fontSize: 14,
                    opacity: 0.6,
                  }}
                  title="Helpful"
                >
                  +
                </button>
                <button
                  onClick={() => handleFeedback(m.id, -1)}
                  style={{
                    background: "none",
                    border: "none",
                    cursor: "pointer",
                    fontSize: 14,
                    opacity: 0.6,
                  }}
                  title="Not helpful"
                >
                  -
                </button>
              </div>
            )}
          </div>
        ))}

        {loading && (
          <div
            style={{
              alignSelf: "flex-start",
              padding: "10px 14px",
              borderRadius: 12,
              backgroundColor: "#f3f4f6",
              color: "#6b7280",
            }}
          >
            <span style={{ animation: "pulse 1.5s infinite" }}>Thinking...</span>
          </div>
        )}

        {errorMsg && (
          <div
            style={{
              padding: "8px 12px",
              backgroundColor: "#fef2f2",
              color: "#b91c1c",
              borderRadius: 8,
              fontSize: 12,
            }}
          >
            {errorMsg}
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <form
        onSubmit={handleAsk}
        style={{
          padding: "12px 16px",
          borderTop: "1px solid rgba(0,0,0,0.08)",
          display: "flex",
          gap: 8,
        }}
      >
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder={placeholder}
          style={{
            flex: 1,
            borderRadius: 8,
            border: "1px solid rgba(0,0,0,0.16)",
            padding: "10px 12px",
            fontSize: 14,
            outline: "none",
            transition: "border-color 0.2s",
          }}
          onFocus={(e) => {
            e.currentTarget.style.borderColor = primaryColor;
          }}
          onBlur={(e) => {
            e.currentTarget.style.borderColor = "rgba(0,0,0,0.16)";
          }}
          disabled={loading}
        />
        <button
          type="submit"
          disabled={loading || !input.trim()}
          style={{
            borderRadius: 8,
            border: "none",
            padding: "10px 16px",
            fontSize: 14,
            fontWeight: 500,
            backgroundColor: primaryColor,
            color: "#fff",
            cursor: loading || !input.trim() ? "default" : "pointer",
            opacity: loading || !input.trim() ? 0.6 : 1,
            transition: "opacity 0.2s",
          }}
        >
          {loading ? "..." : "Send"}
        </button>
      </form>
    </div>
  );
};

export default DocsAiWidget;
