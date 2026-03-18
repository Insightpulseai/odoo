'use client'

import { useState, useRef, useEffect, useCallback } from 'react'
import {
  makeStyles,
  tokens,
  Text,
  Input,
  Button,
  Card,
  Spinner,
  mergeClasses,
} from '@fluentui/react-components'
import {
  Sparkle24Filled,
  Sparkle20Regular,
  Send24Regular,
  Dismiss24Regular,
} from '@fluentui/react-icons'
import { sendCopilotMessage } from '@/lib/hooks'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
}

const useStyles = makeStyles({
  fab: {
    position: 'fixed',
    bottom: '24px',
    right: '24px',
    width: '56px',
    height: '56px',
    borderRadius: '28px',
    background: 'linear-gradient(135deg, #7B2FF2, #2264D1)',
    border: 'none',
    cursor: 'pointer',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    color: '#fff',
    boxShadow: '0 4px 16px rgba(123, 47, 242, 0.4)',
    transitionProperty: 'transform, box-shadow',
    transitionDuration: '200ms',
    zIndex: 1000,
    ':hover': {
      transform: 'scale(1.08)',
      boxShadow: '0 6px 24px rgba(123, 47, 242, 0.5)',
    },
  },
  panel: {
    position: 'fixed',
    bottom: '24px',
    right: '24px',
    width: '400px',
    height: '560px',
    borderRadius: '16px',
    display: 'flex',
    flexDirection: 'column',
    overflow: 'hidden',
    boxShadow: '0 8px 32px rgba(0, 0, 0, 0.16)',
    zIndex: 1000,
    animationName: {
      from: { opacity: 0, transform: 'translateY(16px) scale(0.95)' },
      to: { opacity: 1, transform: 'translateY(0) scale(1)' },
    },
    animationDuration: '300ms',
    animationTimingFunction: 'cubic-bezier(0.33, 1, 0.68, 1)',
  },
  panelHeader: {
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
    padding: '16px 20px',
    background: 'linear-gradient(135deg, #7B2FF2, #2264D1)',
    color: '#fff',
    flexShrink: 0,
  },
  panelHeaderTitle: {
    flex: 1,
    color: '#fff',
    fontWeight: tokens.fontWeightSemibold,
  },
  closeBtn: {
    color: 'rgba(255,255,255,0.8)',
    minWidth: 'auto',
    ':hover': {
      color: '#fff',
      backgroundColor: 'rgba(255,255,255,0.15)',
    },
  },
  messages: {
    flex: 1,
    overflowY: 'auto',
    padding: '16px',
    display: 'flex',
    flexDirection: 'column',
    gap: '12px',
    backgroundColor: tokens.colorNeutralBackground2,
  },
  messageBubble: {
    maxWidth: '85%',
    padding: '10px 14px',
    borderRadius: '12px',
    fontSize: tokens.fontSizeBase200,
    lineHeight: '1.5',
    whiteSpace: 'pre-wrap',
    wordBreak: 'break-word',
  },
  userBubble: {
    alignSelf: 'flex-end',
    background: 'linear-gradient(135deg, #7B2FF2, #2264D1)',
    color: '#fff',
    borderBottomRightRadius: '4px',
  },
  assistantBubble: {
    alignSelf: 'flex-start',
    backgroundColor: tokens.colorNeutralBackground1,
    color: tokens.colorNeutralForeground1,
    borderBottomLeftRadius: '4px',
    boxShadow: '0 1px 3px rgba(0,0,0,0.06)',
  },
  errorBubble: {
    alignSelf: 'flex-start',
    backgroundColor: tokens.colorPaletteRedBackground1,
    color: tokens.colorPaletteRedForeground1,
    borderBottomLeftRadius: '4px',
    boxShadow: '0 1px 3px rgba(0,0,0,0.06)',
  },
  assistantIcon: {
    display: 'flex',
    alignItems: 'center',
    gap: '6px',
    marginBottom: '4px',
    color: '#7B2FF2',
  },
  inputBar: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    padding: '12px 16px',
    borderTop: `1px solid ${tokens.colorNeutralStroke2}`,
    backgroundColor: tokens.colorNeutralBackground1,
    flexShrink: 0,
  },
  sendBtn: {
    minWidth: 'auto',
    color: '#7B2FF2',
  },
  welcomeCard: {
    padding: '16px',
    borderRadius: '12px',
    textAlign: 'center' as const,
    backgroundColor: tokens.colorNeutralBackground1,
  },
  welcomeIcon: {
    color: '#7B2FF2',
    marginBottom: '8px',
  },
  suggestionChips: {
    display: 'flex',
    flexWrap: 'wrap' as const,
    gap: '6px',
    marginTop: '12px',
    justifyContent: 'center',
  },
  chip: {
    fontSize: tokens.fontSizeBase100,
    padding: '4px 10px',
    borderRadius: '12px',
    border: `1px solid ${tokens.colorNeutralStroke2}`,
    backgroundColor: tokens.colorNeutralBackground1,
    cursor: 'pointer',
    transitionProperty: 'background-color, color',
    transitionDuration: '150ms',
    color: tokens.colorNeutralForeground2,
    ':hover': {
      backgroundColor: tokens.colorNeutralBackground3Hover,
      color: '#7B2FF2',
    },
  },
  typing: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    alignSelf: 'flex-start',
    padding: '8px 14px',
    borderRadius: '12px',
    backgroundColor: tokens.colorNeutralBackground1,
    color: tokens.colorNeutralForeground3,
    fontSize: tokens.fontSizeBase200,
  },
})

const SUGGESTIONS = ['Platform status', 'Release blockers', 'Agent tools', 'Service health', 'Foundry SDK', 'KB coverage']

export function CopilotChat() {
  const styles = useStyles()
  const [open, setOpen] = useState(false)
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [typing, setTyping] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, typing])

  useEffect(() => {
    if (open) inputRef.current?.focus()
  }, [open])

  const sendMessage = useCallback(async (text: string) => {
    if (!text.trim()) return
    const userMsg: Message = {
      id: `u-${Date.now()}`,
      role: 'user',
      content: text.trim(),
      timestamp: new Date(),
    }
    setMessages((prev) => [...prev, userMsg])
    setInput('')
    setTyping(true)

    try {
      const history = messages.map((m) => ({ role: m.role, content: m.content }))
      const { reply } = await sendCopilotMessage(text.trim(), history)
      const assistantMsg: Message = {
        id: `a-${Date.now()}`,
        role: 'assistant',
        content: reply,
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, assistantMsg])
    } catch (err) {
      const errorMsg: Message = {
        id: `e-${Date.now()}`,
        role: 'assistant',
        content: `Failed to get a response. ${err instanceof Error ? err.message : 'Please try again.'}`,
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, errorMsg])
    } finally {
      setTyping(false)
    }
  }, [messages])

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault()
        sendMessage(input)
      }
    },
    [input, sendMessage]
  )

  if (!open) {
    return (
      <button
        className={styles.fab}
        onClick={() => setOpen(true)}
        aria-label="Open Copilot chat"
      >
        <Sparkle24Filled />
      </button>
    )
  }

  return (
    <Card className={styles.panel}>
      <div className={styles.panelHeader}>
        <Sparkle20Regular />
        <Text className={styles.panelHeaderTitle} size={400}>
          Copilot
        </Text>
        <Button
          appearance="subtle"
          className={styles.closeBtn}
          icon={<Dismiss24Regular />}
          onClick={() => setOpen(false)}
          aria-label="Close chat"
        />
      </div>

      <div className={styles.messages}>
        {messages.length === 0 && (
          <div className={styles.welcomeCard}>
            <div className={styles.welcomeIcon}>
              <Sparkle24Filled style={{ fontSize: 32 }} />
            </div>
            <Text weight="semibold" size={400} block>
              IPAI Copilot
            </Text>
            <Text size={200} style={{ color: tokens.colorNeutralForeground3, marginTop: 4, display: 'block' }}>
              Ask about platform health, agent readiness, deployment status, or release blockers.
            </Text>
            <div className={styles.suggestionChips}>
              {SUGGESTIONS.map((s) => (
                <button
                  key={s}
                  className={styles.chip}
                  onClick={() => sendMessage(s)}
                >
                  {s}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg) => {
          const isError = msg.role === 'assistant' && msg.content.startsWith('Failed to get a response')
          return (
            <div key={msg.id}>
              {msg.role === 'assistant' && (
                <div className={styles.assistantIcon}>
                  <Sparkle20Regular />
                  <Text size={100} weight="semibold">Copilot</Text>
                </div>
              )}
              <div
                className={mergeClasses(
                  styles.messageBubble,
                  msg.role === 'user'
                    ? styles.userBubble
                    : isError
                      ? styles.errorBubble
                      : styles.assistantBubble
                )}
              >
                {msg.content}
              </div>
            </div>
          )
        })}

        {typing && (
          <div className={styles.typing}>
            <Spinner size="tiny" />
            <Text size={200}>Copilot is thinking...</Text>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <div className={styles.inputBar}>
        <Input
          ref={inputRef}
          value={input}
          onChange={(_, data) => setInput(data.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask Copilot..."
          style={{ flex: 1 }}
          appearance="filled-darker"
        />
        <Button
          appearance="subtle"
          className={styles.sendBtn}
          icon={<Send24Regular />}
          onClick={() => sendMessage(input)}
          disabled={!input.trim() || typing}
          aria-label="Send message"
        />
      </div>
    </Card>
  )
}
