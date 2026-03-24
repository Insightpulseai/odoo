import { useState, useRef, useEffect, useCallback } from 'react';
import { MessageSquare, Send, X, Bot, User, Sparkles, ArrowUpRight, Info, ExternalLink } from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';

// --- CTA Action Contract ---

export type ChatCtaAction =
  | { type: 'send_prompt'; label: string; prompt: string; analytics_id?: string }
  | { type: 'navigate'; label: string; href: string; new_tab?: boolean; analytics_id?: string }
  | { type: 'open_scheduler'; label: string; href: string; analytics_id?: string }
  | { type: 'open_contact'; label: string; page?: string; analytics_id?: string };

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  sourceLabel?: string;
  ctas?: ChatCtaAction[];
}

// --- CTA Validation ---

function isValidCta(action: ChatCtaAction): boolean {
  if (!action.label) return false;
  switch (action.type) {
    case 'send_prompt': return !!action.prompt;
    case 'navigate': return !!action.href;
    case 'open_scheduler': return !!action.href;
    case 'open_contact': return true;
    default: return false;
  }
}

// --- Analytics ---

function trackCtaClick(action: ChatCtaAction, messageId: string) {
  try {
    // Emit structured event for analytics pipeline
    const event = {
      event: 'pulser_cta_clicked',
      cta_type: action.type,
      cta_label: action.label,
      cta_analytics_id: action.analytics_id ?? null,
      message_id: messageId,
      page: window.location.hash || '#home',
      timestamp: new Date().toISOString(),
    };
    // Log for now; wire to real analytics when available
    console.info('[Pulser CTA]', event);
  } catch { /* analytics must not break the widget */ }
}

// --- Initial CTAs ---

const INITIAL_CTAS: ChatCtaAction[] = [
  { type: 'send_prompt', label: 'What is Pulser?', prompt: 'What is Pulser?', analytics_id: 'chat_what_is_pulser' },
  { type: 'send_prompt', label: 'How does Odoo on Cloud work?', prompt: 'How does Odoo on Cloud work?', analytics_id: 'chat_odoo_on_cloud' },
  { type: 'send_prompt', label: 'Which industries do you support?', prompt: 'Which industries do you support?', analytics_id: 'chat_industries' },
  { type: 'open_scheduler', label: 'Book a demo', href: 'https://calendar.google.com/calendar/appointments', analytics_id: 'chat_book_demo' },
];

const FIRST_USE_DISCLOSURE = "I'm the InsightPulseAI product assistant. I answer from approved public sources — our docs, architecture pages, FAQs, pricing, and selected release content. I can't access your ERP, company data, tenant records, or perform actions from this page.";

let msgCounter = 0;
function nextMsgId(): string {
  return `msg_${++msgCounter}_${Date.now()}`;
}

// --- CTA Button Component ---

function CtaButton({ action, onAction, messageId }: { action: ChatCtaAction; onAction: (a: ChatCtaAction, msgId: string) => void; messageId: string }) {
  const valid = isValidCta(action);
  const isExternal = action.type === 'open_scheduler' || (action.type === 'navigate' && action.new_tab);

  return (
    <button
      type="button"
      disabled={!valid}
      onClick={() => valid && onAction(action, messageId)}
      className={`px-4 py-2 rounded-full text-xs font-bold transition-all shadow-sm flex items-center gap-1.5 ${
        action.type === 'open_scheduler' || action.type === 'open_contact'
          ? 'bg-brand-primary text-black hover:bg-cyan-400'
          : 'bg-white border border-gray-200 text-gray-600 hover:border-brand-primary hover:text-brand-primary'
      } ${!valid ? 'opacity-40 cursor-not-allowed' : ''}`}
    >
      {action.label}
      {isExternal && <ExternalLink size={10} />}
      {action.type === 'open_contact' && <ArrowUpRight size={10} />}
    </button>
  );
}

// --- Main Widget ---

export const AskPulser = ({ onNavigate }: { onNavigate?: (page: string) => void }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [input, setInput] = useState('');
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([
    {
      id: nextMsgId(),
      role: 'assistant',
      content: `Hi! I'm Pulser, your product assistant. ${FIRST_USE_DISCLOSURE}\n\nWhat would you like to explore?`,
      sourceLabel: 'Product Docs',
      ctas: INITIAL_CTAS,
    }
  ]);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // --- Send a user message ---
  const handleSend = useCallback(async (text?: string) => {
    const messageText = text || input.trim();
    if (!messageText || isLoading) return;

    const userMsg: Message = { id: nextMsgId(), role: 'user', content: messageText };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await fetch('/api/pulser/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: messageText,
          sessionId: 'web-anon-session',
          conversationId,
          context: { surface: 'landing_page', page: window.location.hash || '#home', visitorType: 'anonymous' },
        }),
      });

      if (!response.ok) throw new Error('Gateway error');
      const data = await response.json();

      setConversationId(data.conversationId);
      setMessages(prev => [...prev, {
        id: nextMsgId(),
        role: 'assistant',
        content: data.reply,
        sourceLabel: data.sourceLabel || 'Product Docs',
        ctas: data.ctas ?? mapLegacyResponse(data),
      }]);
    } catch (error) {
      console.error('Chat error:', error);
      setMessages(prev => [...prev, {
        id: nextMsgId(),
        role: 'assistant',
        content: "I'm sorry, I'm having trouble connecting right now. Please try again or contact our team.",
        sourceLabel: 'System',
      }]);
    } finally {
      setIsLoading(false);
    }
  }, [input, isLoading, conversationId]);

  // --- Centralized CTA handler ---
  const handleCtaAction = useCallback((action: ChatCtaAction, messageId: string) => {
    if (!isValidCta(action)) {
      console.error('[Pulser CTA] Invalid action:', action);
      return;
    }

    trackCtaClick(action, messageId);

    switch (action.type) {
      case 'send_prompt':
        handleSend(action.prompt);
        return;

      case 'navigate':
        if (action.new_tab) {
          window.open(action.href, '_blank', 'noopener,noreferrer');
        } else if (action.href.startsWith('#') && onNavigate) {
          onNavigate(action.href.replace('#', ''));
        } else {
          window.location.hash = action.href;
        }
        return;

      case 'open_scheduler':
        window.open(action.href, '_blank', 'noopener,noreferrer');
        return;

      case 'open_contact':
        if (onNavigate) {
          onNavigate(action.page || 'contact');
        } else {
          window.location.hash = '#contact';
        }
        return;
    }
  }, [handleSend, onNavigate]);

  return (
    <div className="fixed bottom-8 right-8 z-[100]">
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.9, y: 20 }}
            className="bg-white rounded-[32px] shadow-[0_8px_16px_rgba(0,0,0,0.08),0_32px_64px_-16px_rgba(0,0,0,0.25)] w-[400px] h-[600px] flex flex-col overflow-hidden border border-gray-100 mb-6"
          >
            {/* Header */}
            <div className="bg-brand-dark p-6 flex items-center justify-between relative overflow-hidden">
              <div className="absolute inset-0 grid-pattern opacity-10"></div>
              <div className="flex items-center gap-3 relative z-10">
                <div className="relative w-10 h-10 flex items-center justify-center">
                  <div className="absolute inset-0 bg-brand-primary/30 rounded-full blur-md"></div>
                  <div className="relative w-8 h-4 bg-brand-primary rounded-full"></div>
                </div>
                <div>
                  <h3 className="text-white font-bold text-base leading-none flex items-center gap-2">
                    Pulser <Sparkles size={14} className="text-brand-primary animate-pulse" />
                  </h3>
                  <div className="flex items-center gap-1.5 mt-1.5">
                    <div className="w-1.5 h-1.5 bg-brand-primary rounded-full animate-pulse"></div>
                    <span className="text-gray-400 text-[10px] uppercase font-bold tracking-widest">Product Assistant</span>
                  </div>
                </div>
              </div>
              <button
                onClick={() => setIsOpen(false)}
                className="text-gray-400 hover:text-white transition-colors relative z-10 p-2 hover:bg-white/5 rounded-full"
              >
                <X size={20} />
              </button>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-6 space-y-6 bg-gray-50/50">
              {messages.map((msg) => (
                <div key={msg.id} className="space-y-4">
                  <div className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                    <div className={`flex gap-3 max-w-[85%] ${msg.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
                      <div className={`w-8 h-8 rounded-full flex-shrink-0 flex items-center justify-center shadow-sm ${msg.role === 'user' ? 'bg-black' : 'bg-brand-primary'}`}>
                        {msg.role === 'user' ? <User size={14} className="text-white" /> : <Bot size={14} className="text-black" />}
                      </div>
                      <div className={`p-4 rounded-2xl text-sm leading-relaxed ${
                        msg.role === 'user'
                          ? 'bg-black text-white rounded-tr-none shadow-lg'
                          : 'bg-white text-gray-800 shadow-sm border border-gray-100 rounded-tl-none'
                      }`}>
                        {msg.content}
                        {msg.role === 'assistant' && msg.sourceLabel && (
                          <div className="mt-3 flex items-center gap-1.5 text-[10px] text-gray-400 font-medium border-t border-gray-100 pt-2">
                            <Info size={10} />
                            Source: {msg.sourceLabel}
                          </div>
                        )}
                        {isLoading && msg === messages[messages.length - 1] && msg.role === 'user' && (
                          <div className="mt-2 flex gap-1">
                            <div className="w-1 h-1 bg-white/50 rounded-full animate-bounce"></div>
                            <div className="w-1 h-1 bg-white/50 rounded-full animate-bounce [animation-delay:0.2s]"></div>
                            <div className="w-1 h-1 bg-white/50 rounded-full animate-bounce [animation-delay:0.4s]"></div>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* CTAs — rendered from structured action data */}
                  {msg.role === 'assistant' && msg.ctas && msg.ctas.length > 0 && !isLoading && (
                    <div className="flex flex-wrap gap-2 pl-11">
                      {msg.ctas.filter(isValidCta).map((cta, j) => (
                        <CtaButton key={j} action={cta} onAction={handleCtaAction} messageId={msg.id} />
                      ))}
                    </div>
                  )}
                </div>
              ))}
              <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <div className="p-6 bg-white border-t border-gray-100">
              <div className="relative flex items-center">
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                  placeholder="Ask Pulser..."
                  className="w-full pl-5 pr-14 py-4 bg-gray-100 rounded-2xl text-sm focus:outline-none focus:ring-2 focus:ring-brand-primary/50 transition-all font-medium"
                />
                <button
                  onClick={() => handleSend()}
                  disabled={isLoading || !input.trim()}
                  className="absolute right-2 p-3 bg-brand-primary text-black rounded-xl hover:bg-cyan-400 transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-md"
                >
                  <Send size={18} />
                </button>
              </div>
              <p className="text-[10px] text-gray-400 mt-4 text-center font-medium">
                Pulser answers from public sources only. Verify important information independently.
              </p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <button
        onClick={() => setIsOpen(!isOpen)}
        className={`group relative w-20 h-20 rounded-full flex items-center justify-center shadow-[0_8px_16px_rgba(0,0,0,0.1),0_32px_64px_-16px_rgba(0,0,0,0.3)] transition-all duration-500 ${
          isOpen ? 'bg-black text-white rotate-90' : 'bg-brand-primary text-black hover:scale-110'
        }`}
      >
        <AnimatePresence mode="wait">
          {isOpen ? (
            <motion.div key="close" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
              <X size={28} />
            </motion.div>
          ) : (
            <motion.div key="open" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="flex flex-col items-center">
              <MessageSquare size={28} />
              <span className="absolute -top-12 right-0 bg-brand-dark text-white text-[10px] font-bold px-3 py-1.5 rounded-full whitespace-nowrap shadow-xl border border-white/10 opacity-0 group-hover:opacity-100 transition-opacity">
                Ask Pulser
              </span>
            </motion.div>
          )}
        </AnimatePresence>
      </button>
    </div>
  );
};

// --- Legacy Response Adapter ---
// Maps old suggestedPrompts/handoff shape to structured CTAs
// Remove once backend fully emits ctas[]

function mapLegacyResponse(data: { suggestedPrompts?: string[]; handoff?: { type: string; label: string } | null }): ChatCtaAction[] {
  const ctas: ChatCtaAction[] = [];

  if (data.suggestedPrompts) {
    for (const prompt of data.suggestedPrompts) {
      const lower = prompt.toLowerCase();
      if (lower.includes('demo')) {
        ctas.push({ type: 'open_scheduler', label: prompt, href: 'https://calendar.google.com/calendar/appointments', analytics_id: 'chat_book_demo' });
      } else {
        ctas.push({ type: 'send_prompt', label: prompt, prompt, analytics_id: `chat_suggested_${prompt.replace(/\s+/g, '_').toLowerCase().slice(0, 30)}` });
      }
    }
  }

  if (data.handoff) {
    ctas.push({ type: 'open_contact', label: data.handoff.label, page: 'contact', analytics_id: 'chat_handoff_specialist' });
  }

  return ctas;
}
