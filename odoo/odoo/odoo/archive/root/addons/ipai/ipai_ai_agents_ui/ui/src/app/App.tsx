/**
 * IPAI AI Agents UI - Main Application Component
 *
 * The root component that provides Fluent UI theming and renders
 * the Ask AI chat panel.
 */

import React, { useEffect, useMemo, useState, useCallback } from "react";
import {
  FluentProvider,
  webLightTheme,
  webDarkTheme,
  Button,
  Dropdown,
  Option,
  Textarea,
  Card,
  CardHeader,
  Subtitle1,
  Body1,
  Caption1,
  Spinner,
  Badge,
  Link,
  Divider,
  makeStyles,
  shorthands,
  tokens,
} from "@fluentui/react-components";
import {
  Send24Regular,
  ChatSparkle24Regular,
  WeatherSunny24Regular,
  WeatherMoon24Regular,
  ThumbLike24Regular,
  ThumbDislike24Regular,
  Open16Regular,
} from "@fluentui/react-icons";
import type { MountOptions } from "../main";
import { odooJsonRpc } from "../lib/odooRpc";

// ============================================================================
// Types
// ============================================================================

interface Agent {
  id: number;
  name: string;
  provider_type: string;
  is_default: boolean;
}

interface Citation {
  rank: number;
  title: string;
  url: string;
  snippet: string;
  score: number;
}

interface Message {
  id?: number;
  role: "user" | "assistant" | "system";
  content: string;
  confidence?: number;
  citations?: Citation[];
  create_date?: string;
}

interface BootstrapResponse {
  agents: Agent[];
  user: { id: number; name: string };
  company: { id: number; name: string };
  config: { max_message_length: number };
}

interface AskResponse {
  ok: boolean;
  thread_id?: number;
  messages?: Message[];
  error?: string;
}

// ============================================================================
// Styles
// ============================================================================

const useStyles = makeStyles({
  root: {
    height: "100%",
    display: "flex",
    flexDirection: "column",
    backgroundColor: tokens.colorNeutralBackground1,
  },
  header: {
    ...shorthands.padding("12px", "16px"),
    ...shorthands.borderBottom("1px", "solid", tokens.colorNeutralStroke1),
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    backgroundColor: tokens.colorNeutralBackground2,
  },
  headerLeft: {
    display: "flex",
    alignItems: "center",
    ...shorthands.gap("12px"),
  },
  headerRight: {
    display: "flex",
    alignItems: "center",
    ...shorthands.gap("8px"),
  },
  body: {
    flexGrow: 1,
    overflowY: "auto",
    ...shorthands.padding("16px"),
  },
  centerContent: {
    height: "100%",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    flexDirection: "column",
    ...shorthands.gap("12px"),
  },
  messageList: {
    display: "flex",
    flexDirection: "column",
    ...shorthands.gap("12px"),
  },
  messageCard: {
    maxWidth: "90%",
  },
  userMessage: {
    alignSelf: "flex-end",
    backgroundColor: tokens.colorBrandBackground,
    color: tokens.colorNeutralForegroundOnBrand,
  },
  assistantMessage: {
    alignSelf: "flex-start",
  },
  messageContent: {
    whiteSpace: "pre-wrap",
    fontSize: "14px",
    lineHeight: "1.5",
    ...shorthands.padding("8px", "0"),
  },
  citations: {
    ...shorthands.margin("12px", "0", "0"),
    ...shorthands.padding("12px"),
    backgroundColor: tokens.colorNeutralBackground3,
    ...shorthands.borderRadius("4px"),
  },
  citationList: {
    listStyleType: "decimal",
    paddingLeft: "20px",
    marginTop: "8px",
    ...shorthands.margin("8px", "0", "0"),
  },
  citationItem: {
    marginBottom: "8px",
    fontSize: "13px",
  },
  composer: {
    ...shorthands.padding("16px"),
    ...shorthands.borderTop("1px", "solid", tokens.colorNeutralStroke1),
    backgroundColor: tokens.colorNeutralBackground2,
  },
  composerActions: {
    display: "flex",
    justifyContent: "flex-end",
    marginTop: "12px",
    ...shorthands.gap("8px"),
  },
  feedbackButtons: {
    display: "flex",
    ...shorthands.gap("4px"),
    marginTop: "8px",
  },
  emptyState: {
    textAlign: "center",
    color: tokens.colorNeutralForeground3,
  },
});

// ============================================================================
// Component
// ============================================================================

interface AppProps {
  options: MountOptions;
}

export function App({ options }: AppProps) {
  const styles = useStyles();

  // State
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [agents, setAgents] = useState<Agent[]>([]);
  const [selectedAgentId, setSelectedAgentId] = useState<number | null>(null);
  const [threadId, setThreadId] = useState<number | null>(null);
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [theme, setTheme] = useState<"light" | "dark">("light");
  const [error, setError] = useState<string | null>(null);

  const fluentTheme = useMemo(
    () => (theme === "dark" ? webDarkTheme : webLightTheme),
    [theme]
  );

  // Bootstrap on mount
  useEffect(() => {
    (async () => {
      try {
        const data = (await odooJsonRpc(
          options.rpcRouteBootstrap,
          {}
        )) as BootstrapResponse | null;

        if (data?.agents) {
          setAgents(data.agents);
          // Select default agent or first available
          const defaultAgent = data.agents.find((a) => a.is_default);
          setSelectedAgentId(defaultAgent?.id ?? data.agents[0]?.id ?? null);
        }
      } catch (e) {
        console.error("Bootstrap failed:", e);
        setError("Failed to load AI configuration");
      } finally {
        setLoading(false);
      }
    })();
  }, [options.rpcRouteBootstrap]);

  // Send message handler
  const handleSend = useCallback(async () => {
    const msg = input.trim();
    if (!msg || !selectedAgentId || sending) return;

    // Optimistic update
    setMessages((prev) => [...prev, { role: "user", content: msg }]);
    setInput("");
    setSending(true);
    setError(null);

    try {
      const resp = (await odooJsonRpc(options.rpcRouteAsk, {
        provider_id: selectedAgentId,
        message: msg,
        thread_id: threadId,
      })) as AskResponse | null;

      if (!resp?.ok) {
        setError(resp?.error ?? "Failed to get response");
        return;
      }

      setThreadId(resp.thread_id ?? null);
      if (resp.messages) {
        setMessages(resp.messages);
      }
    } catch (e) {
      console.error("Ask failed:", e);
      setError("Failed to send message");
    } finally {
      setSending(false);
    }
  }, [input, selectedAgentId, threadId, sending, options.rpcRouteAsk]);

  // Handle Enter key
  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        handleSend();
      }
    },
    [handleSend]
  );

  // New conversation
  const handleNewConversation = useCallback(() => {
    setThreadId(null);
    setMessages([]);
    setError(null);
  }, []);

  // Theme toggle
  const toggleTheme = useCallback(() => {
    setTheme((t) => (t === "light" ? "dark" : "light"));
  }, []);

  // Submit feedback
  const handleFeedback = useCallback(
    async (messageId: number | undefined, rating: "helpful" | "not_helpful") => {
      if (!messageId) return;
      try {
        await odooJsonRpc(options.rpcRouteFeedback, {
          message_id: messageId,
          rating,
        });
      } catch (e) {
        console.warn("Feedback submission failed:", e);
      }
    },
    [options.rpcRouteFeedback]
  );

  // ============================================================================
  // Render
  // ============================================================================

  return (
    <FluentProvider theme={fluentTheme} style={{ height: "100%" }}>
      <div className={styles.root}>
        {/* Header */}
        <div className={styles.header}>
          <div className={styles.headerLeft}>
            <ChatSparkle24Regular />
            <Subtitle1>Ask AI</Subtitle1>

            {agents.length > 0 && (
              <Dropdown
                value={agents.find((a) => a.id === selectedAgentId)?.name ?? ""}
                placeholder="Select agent"
                onOptionSelect={(_, data) => {
                  const id = Number(data.optionValue);
                  setSelectedAgentId(id);
                  handleNewConversation();
                }}
                style={{ minWidth: "180px" }}
              >
                {agents.map((a) => (
                  <Option key={a.id} value={String(a.id)}>
                    {a.name}
                  </Option>
                ))}
              </Dropdown>
            )}
          </div>

          <div className={styles.headerRight}>
            <Button
              appearance="subtle"
              icon={
                theme === "dark" ? <WeatherSunny24Regular /> : <WeatherMoon24Regular />
              }
              onClick={toggleTheme}
              title={`Switch to ${theme === "dark" ? "light" : "dark"} mode`}
            />
            <Button appearance="subtle" onClick={handleNewConversation}>
              New Chat
            </Button>
          </div>
        </div>

        {/* Body */}
        <div className={styles.body}>
          {loading ? (
            <div className={styles.centerContent}>
              <Spinner size="large" label="Loading AI configuration..." />
            </div>
          ) : error && messages.length === 0 ? (
            <div className={styles.centerContent}>
              <Body1 className={styles.emptyState}>{error}</Body1>
              <Button appearance="primary" onClick={() => setError(null)}>
                Try Again
              </Button>
            </div>
          ) : messages.length === 0 ? (
            <div className={styles.centerContent}>
              <ChatSparkle24Regular style={{ fontSize: "48px", opacity: 0.5 }} />
              <Body1 className={styles.emptyState}>
                Ask me anything about your Odoo workflows, records, or processes.
              </Body1>
              <Caption1 className={styles.emptyState}>
                Press Alt+Shift+F anytime to open this panel
              </Caption1>
            </div>
          ) : (
            <div className={styles.messageList}>
              {messages.map((msg, idx) => (
                <Card
                  key={msg.id ?? idx}
                  className={`${styles.messageCard} ${
                    msg.role === "user" ? styles.userMessage : styles.assistantMessage
                  }`}
                  appearance="outline"
                >
                  <CardHeader
                    header={
                      <Body1 weight="semibold">
                        {msg.role === "user" ? "You" : "AI Assistant"}
                      </Body1>
                    }
                    description={
                      msg.role === "assistant" && msg.confidence !== undefined ? (
                        <Badge
                          appearance="outline"
                          color={msg.confidence >= 0.7 ? "success" : msg.confidence >= 0.4 ? "warning" : "danger"}
                        >
                          {msg.confidence >= 0.7 ? "Confident" : msg.confidence >= 0.4 ? "Moderate" : "Uncertain"}
                          {" "}({(msg.confidence * 100).toFixed(0)}%)
                        </Badge>
                      ) : undefined
                    }
                  />

                  <div className={styles.messageContent}>{msg.content}</div>

                  {/* Citations */}
                  {msg.citations && msg.citations.length > 0 && (
                    <div className={styles.citations}>
                      <Caption1 weight="semibold">Sources</Caption1>
                      <ol className={styles.citationList}>
                        {msg.citations.map((cite, i) => (
                          <li key={i} className={styles.citationItem}>
                            {cite.url ? (
                              <Link href={cite.url} target="_blank" rel="noreferrer">
                                {cite.title || cite.url}
                                <Open16Regular style={{ marginLeft: 4, verticalAlign: "middle" }} />
                              </Link>
                            ) : (
                              <span>{cite.title || "Untitled"}</span>
                            )}
                            {cite.snippet && (
                              <Caption1 block style={{ marginTop: 4, opacity: 0.8 }}>
                                {cite.snippet.slice(0, 150)}
                                {cite.snippet.length > 150 ? "..." : ""}
                              </Caption1>
                            )}
                          </li>
                        ))}
                      </ol>
                    </div>
                  )}

                  {/* Feedback buttons for assistant messages */}
                  {msg.role === "assistant" && msg.id && (
                    <div className={styles.feedbackButtons}>
                      <Button
                        appearance="subtle"
                        size="small"
                        icon={<ThumbLike24Regular />}
                        onClick={() => handleFeedback(msg.id, "helpful")}
                        title="Helpful"
                      />
                      <Button
                        appearance="subtle"
                        size="small"
                        icon={<ThumbDislike24Regular />}
                        onClick={() => handleFeedback(msg.id, "not_helpful")}
                        title="Not helpful"
                      />
                    </div>
                  )}
                </Card>
              ))}

              {sending && (
                <Card className={`${styles.messageCard} ${styles.assistantMessage}`}>
                  <CardHeader header={<Body1 weight="semibold">AI Assistant</Body1>} />
                  <Spinner size="small" label="Thinking..." />
                </Card>
              )}

              {error && messages.length > 0 && (
                <Card className={`${styles.messageCard} ${styles.assistantMessage}`} appearance="outline">
                  <Body1 style={{ color: tokens.colorPaletteRedForeground1 }}>{error}</Body1>
                </Card>
              )}
            </div>
          )}
        </div>

        {/* Composer */}
        <div className={styles.composer}>
          <Textarea
            value={input}
            onChange={(_, data) => setInput(data.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask about workflows, records, or how to do something in Odoo..."
            resize="vertical"
            disabled={sending || !selectedAgentId}
            style={{ width: "100%" }}
          />
          <div className={styles.composerActions}>
            <Button
              appearance="primary"
              icon={<Send24Regular />}
              onClick={handleSend}
              disabled={!input.trim() || sending || !selectedAgentId}
            >
              Send
            </Button>
          </div>
        </div>
      </div>
    </FluentProvider>
  );
}
