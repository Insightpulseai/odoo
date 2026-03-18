import React, { useState } from 'react';

// ============================================================================
// InsightPulse AI Design Tokens (Fluent 2-aligned)
// ============================================================================

export const insightPulseTokens = {
  colors: {
    // Primary brand colors
    primary: {
      50: '#e6f2ff',
      100: '#b3d9ff',
      200: '#80bfff',
      300: '#4da6ff',
      400: '#1a8cff',
      500: '#0073e6',    // Primary brand color
      600: '#005bb3',
      700: '#004380',
      800: '#002b4d',
      900: '#00131a',
    },
    // Neutral grays
    neutral: {
      0: '#ffffff',
      10: '#fafafa',
      20: '#f5f5f5',
      30: '#e0e0e0',
      40: '#d6d6d6',
      50: '#c2c2c2',
      60: '#a0a0a0',
      70: '#7a7a7a',
      80: '#5c5c5c',
      90: '#3d3d3d',
      100: '#1a1a1a',
    },
    // Semantic colors
    success: '#107c10',
    warning: '#faa500',
    error: '#d13438',
    info: '#0078d4',
    // AI-specific accent
    aiAccent: '#7c3aed',  // Purple for AI features
  },

  // Typography scale (Fluent 2-aligned)
  typography: {
    fontFamily: {
      base: `-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif`,
      mono: `"Cascadia Code", "Fira Code", Consolas, "Courier New", monospace`,
    },
    fontSize: {
      100: '10px',
      200: '12px',
      300: '14px',
      400: '16px',
      500: '20px',
      600: '24px',
      700: '28px',
      800: '32px',
      900: '40px',
    },
    fontWeight: {
      regular: 400,
      medium: 500,
      semibold: 600,
      bold: 700,
    },
    lineHeight: {
      100: '14px',
      200: '16px',
      300: '20px',
      400: '22px',
      500: '28px',
      600: '32px',
      700: '36px',
      800: '40px',
      900: '52px',
    },
  },

  // Spacing scale (4px base)
  spacing: {
    xxs: '4px',
    xs: '8px',
    s: '12px',
    m: '16px',
    l: '20px',
    xl: '24px',
    xxl: '32px',
    xxxl: '40px',
  },

  // Border radius
  borderRadius: {
    none: '0',
    small: '2px',
    medium: '4px',
    large: '8px',
    circular: '9999px',
  },

  // Elevation (box-shadow)
  elevation: {
    2: '0 0 2px rgba(0,0,0,0.12), 0 2px 4px rgba(0,0,0,0.14)',
    4: '0 0 2px rgba(0,0,0,0.12), 0 4px 8px rgba(0,0,0,0.14)',
    8: '0 0 2px rgba(0,0,0,0.12), 0 8px 16px rgba(0,0,0,0.14)',
    16: '0 0 2px rgba(0,0,0,0.12), 0 16px 32px rgba(0,0,0,0.14)',
  },

  // Duration (motion)
  duration: {
    faster: '50ms',
    fast: '100ms',
    normal: '200ms',
    slow: '300ms',
    slower: '400ms',
  },
};

// ============================================================================
// AI Chat Widget Component
// ============================================================================

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

export const AIChatWidget: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content: 'Hello! I\'m InsightPulse AI. How can I help you today?',
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);

  const handleSend = () => {
    if (!input.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsTyping(true);

    // Simulate AI response
    setTimeout(() => {
      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: `I received your message: "${input}". This is a demo response.`,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, aiMessage]);
      setIsTyping(false);
    }, 1500);
  };

  return (
    <div
      style={{
        position: 'fixed',
        bottom: insightPulseTokens.spacing.l,
        right: insightPulseTokens.spacing.l,
        zIndex: 1000,
        fontFamily: insightPulseTokens.typography.fontFamily.base,
      }}
    >
      {/* Expanded Panel */}
      {isOpen && (
        <div
          style={{
            position: 'absolute',
            bottom: '72px',
            right: 0,
            width: '400px',
            height: '600px',
            backgroundColor: insightPulseTokens.colors.neutral[0],
            borderRadius: insightPulseTokens.borderRadius.large,
            boxShadow: insightPulseTokens.elevation[16],
            display: 'flex',
            flexDirection: 'column',
            overflow: 'hidden',
          }}
        >
          {/* Header */}
          <div
            style={{
              padding: insightPulseTokens.spacing.m,
              backgroundColor: insightPulseTokens.colors.primary[500],
              color: insightPulseTokens.colors.neutral[0],
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: insightPulseTokens.spacing.xs }}>
              <div
                style={{
                  width: '32px',
                  height: '32px',
                  borderRadius: insightPulseTokens.borderRadius.circular,
                  backgroundColor: insightPulseTokens.colors.aiAccent,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: insightPulseTokens.typography.fontSize[500],
                }}
              >
                ✨
              </div>
              <div>
                <div style={{ fontWeight: insightPulseTokens.typography.fontWeight.semibold }}>
                  InsightPulse AI
                </div>
                <div style={{ fontSize: insightPulseTokens.typography.fontSize[200], opacity: 0.9 }}>
                  Always ready to help
                </div>
              </div>
            </div>
            <button
              onClick={() => setIsOpen(false)}
              style={{
                background: 'none',
                border: 'none',
                color: insightPulseTokens.colors.neutral[0],
                fontSize: insightPulseTokens.typography.fontSize[500],
                cursor: 'pointer',
                padding: insightPulseTokens.spacing.xs,
              }}
            >
              ✕
            </button>
          </div>

          {/* Messages */}
          <div
            style={{
              flex: 1,
              overflowY: 'auto',
              padding: insightPulseTokens.spacing.m,
              display: 'flex',
              flexDirection: 'column',
              gap: insightPulseTokens.spacing.m,
            }}
          >
            {messages.map((msg) => (
              <div
                key={msg.id}
                style={{
                  display: 'flex',
                  justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start',
                }}
              >
                <div
                  style={{
                    maxWidth: '75%',
                    padding: insightPulseTokens.spacing.s,
                    borderRadius: insightPulseTokens.borderRadius.medium,
                    backgroundColor:
                      msg.role === 'user'
                        ? insightPulseTokens.colors.primary[500]
                        : insightPulseTokens.colors.neutral[20],
                    color:
                      msg.role === 'user'
                        ? insightPulseTokens.colors.neutral[0]
                        : insightPulseTokens.colors.neutral[100],
                  }}
                >
                  <div style={{ fontSize: insightPulseTokens.typography.fontSize[300] }}>
                    {msg.content}
                  </div>
                  <div
                    style={{
                      fontSize: insightPulseTokens.typography.fontSize[100],
                      opacity: 0.7,
                      marginTop: insightPulseTokens.spacing.xxs,
                    }}
                  >
                    {msg.timestamp.toLocaleTimeString()}
                  </div>
                </div>
              </div>
            ))}

            {isTyping && (
              <div style={{ display: 'flex', justifyContent: 'flex-start' }}>
                <div
                  style={{
                    padding: insightPulseTokens.spacing.s,
                    borderRadius: insightPulseTokens.borderRadius.medium,
                    backgroundColor: insightPulseTokens.colors.neutral[20],
                  }}
                >
                  <div style={{ display: 'flex', gap: '4px' }}>
                    <div
                      style={{
                        width: '8px',
                        height: '8px',
                        borderRadius: '50%',
                        backgroundColor: insightPulseTokens.colors.neutral[60],
                        animation: 'pulse 1.4s infinite',
                      }}
                    />
                    <div
                      style={{
                        width: '8px',
                        height: '8px',
                        borderRadius: '50%',
                        backgroundColor: insightPulseTokens.colors.neutral[60],
                        animation: 'pulse 1.4s infinite 0.2s',
                      }}
                    />
                    <div
                      style={{
                        width: '8px',
                        height: '8px',
                        borderRadius: '50%',
                        backgroundColor: insightPulseTokens.colors.neutral[60],
                        animation: 'pulse 1.4s infinite 0.4s',
                      }}
                    />
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Input */}
          <div
            style={{
              padding: insightPulseTokens.spacing.m,
              borderTop: `1px solid ${insightPulseTokens.colors.neutral[30]}`,
              display: 'flex',
              gap: insightPulseTokens.spacing.s,
            }}
          >
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSend()}
              placeholder="Ask me anything..."
              style={{
                flex: 1,
                padding: insightPulseTokens.spacing.s,
                borderRadius: insightPulseTokens.borderRadius.medium,
                border: `1px solid ${insightPulseTokens.colors.neutral[40]}`,
                fontSize: insightPulseTokens.typography.fontSize[300],
                outline: 'none',
              }}
            />
            <button
              onClick={handleSend}
              style={{
                padding: `${insightPulseTokens.spacing.s} ${insightPulseTokens.spacing.m}`,
                backgroundColor: insightPulseTokens.colors.primary[500],
                color: insightPulseTokens.colors.neutral[0],
                border: 'none',
                borderRadius: insightPulseTokens.borderRadius.medium,
                cursor: 'pointer',
                fontWeight: insightPulseTokens.typography.fontWeight.semibold,
              }}
            >
              Send
            </button>
          </div>
        </div>
      )}

      {/* FAB (Floating Action Button) */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        style={{
          width: '56px',
          height: '56px',
          borderRadius: insightPulseTokens.borderRadius.circular,
          backgroundColor: insightPulseTokens.colors.primary[500],
          color: insightPulseTokens.colors.neutral[0],
          border: 'none',
          cursor: 'pointer',
          boxShadow: insightPulseTokens.elevation[8],
          fontSize: insightPulseTokens.typography.fontSize[600],
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          transition: `transform ${insightPulseTokens.duration.normal} ease`,
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.transform = 'scale(1.1)';
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.transform = 'scale(1)';
        }}
      >
        {isOpen ? '✕' : '✨'}
      </button>

      {/* Inline CSS for animation */}
      <style>
        {`
          @keyframes pulse {
            0%, 100% { opacity: 0.4; }
            50% { opacity: 1; }
          }
        `}
      </style>
    </div>
  );
};

// ============================================================================
// Demo Page Component
// ============================================================================

export const AIChatWidgetDemo: React.FC = () => {
  return (
    <div
      style={{
        minHeight: '100vh',
        backgroundColor: insightPulseTokens.colors.neutral[10],
        padding: insightPulseTokens.spacing.xxl,
        fontFamily: insightPulseTokens.typography.fontFamily.base,
      }}
    >
      <div style={{ maxWidth: '800px', margin: '0 auto' }}>
        <h1
          style={{
            fontSize: insightPulseTokens.typography.fontSize[900],
            fontWeight: insightPulseTokens.typography.fontWeight.bold,
            color: insightPulseTokens.colors.neutral[100],
            marginBottom: insightPulseTokens.spacing.xl,
          }}
        >
          InsightPulse AI Chat Widget
        </h1>

        <div
          style={{
            backgroundColor: insightPulseTokens.colors.neutral[0],
            padding: insightPulseTokens.spacing.xl,
            borderRadius: insightPulseTokens.borderRadius.large,
            boxShadow: insightPulseTokens.elevation[4],
            marginBottom: insightPulseTokens.spacing.xl,
          }}
        >
          <h2
            style={{
              fontSize: insightPulseTokens.typography.fontSize[600],
              fontWeight: insightPulseTokens.typography.fontWeight.semibold,
              marginBottom: insightPulseTokens.spacing.m,
            }}
          >
            Design System Tokens
          </h2>
          <p style={{ fontSize: insightPulseTokens.typography.fontSize[300], lineHeight: insightPulseTokens.typography.lineHeight[400] }}>
            This component demonstrates the InsightPulse AI design system, featuring Fluent 2-aligned tokens for colors, typography, spacing, elevation, and motion. Click the floating button in the bottom right to interact with the chat widget.
          </p>
        </div>

        {/* Color Palette */}
        <div
          style={{
            backgroundColor: insightPulseTokens.colors.neutral[0],
            padding: insightPulseTokens.spacing.xl,
            borderRadius: insightPulseTokens.borderRadius.large,
            boxShadow: insightPulseTokens.elevation[4],
            marginBottom: insightPulseTokens.spacing.xl,
          }}
        >
          <h3
            style={{
              fontSize: insightPulseTokens.typography.fontSize[500],
              fontWeight: insightPulseTokens.typography.fontWeight.semibold,
              marginBottom: insightPulseTokens.spacing.m,
            }}
          >
            Primary Color Scale
          </h3>
          <div style={{ display: 'flex', gap: insightPulseTokens.spacing.xs, flexWrap: 'wrap' }}>
            {Object.entries(insightPulseTokens.colors.primary).map(([key, value]) => (
              <div key={key} style={{ textAlign: 'center' }}>
                <div
                  style={{
                    width: '60px',
                    height: '60px',
                    backgroundColor: value,
                    borderRadius: insightPulseTokens.borderRadius.medium,
                    marginBottom: insightPulseTokens.spacing.xxs,
                  }}
                />
                <div style={{ fontSize: insightPulseTokens.typography.fontSize[100] }}>{key}</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Chat Widget */}
      <AIChatWidget />
    </div>
  );
};
