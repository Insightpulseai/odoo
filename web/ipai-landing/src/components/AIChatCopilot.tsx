import { useState, useRef, useEffect } from 'react';
import { MessageSquare, Send, X, Bot, User, Loader2, ChevronRight, Sparkles, ArrowUpRight } from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  suggestedPrompts?: string[];
  handoff?: {
    type: string;
    label: string;
  } | null;
}

const INITIAL_PROMPTS = [
  "What is Odoo Copilot?",
  "How does Odoo on Cloud work?",
  "Which industries do you support?",
  "Show me how finance close works"
];

export const AIChatCopilot = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [input, setInput] = useState('');
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([
    { 
      role: 'assistant', 
      content: "Hi! I'm your Odoo Copilot. I can help you understand how InsightPulseAI modernizes operations for marketing, media, retail, and finance. What would you like to explore?",
      suggestedPrompts: INITIAL_PROMPTS
    }
  ]);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async (text?: string) => {
    const messageText = text || input.trim();
    if (!messageText || isLoading) return;

    const userMessage: Message = { role: 'user', content: messageText };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      // Calling our Backend Chat Gateway instead of calling AI Foundry directly
      const response = await fetch('/api/copilot/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: messageText,
          sessionId: 'web-anon-session', // In production, use a real session ID
          conversationId: conversationId,
          context: {
            surface: 'landing_page',
            page: window.location.pathname,
            visitorType: 'anonymous'
          }
        })
      });

      if (!response.ok) throw new Error('Gateway error');

      const data = await response.json();
      
      setConversationId(data.conversationId);
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: data.reply,
        suggestedPrompts: data.suggestedPrompts,
        handoff: data.handoff
      }]);
    } catch (error) {
      console.error("Chat error:", error);
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: "I'm sorry, I'm having trouble connecting to the Odoo Copilot service. Please try again or contact our team." 
      }]);
    } finally {
      setIsLoading(false);
    }
  };

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
                    Odoo Copilot <Sparkles size={14} className="text-brand-primary animate-pulse" />
                  </h3>
                  <div className="flex items-center gap-1.5 mt-1.5">
                    <div className="w-1.5 h-1.5 bg-brand-primary rounded-full animate-pulse"></div>
                    <span className="text-gray-400 text-[10px] uppercase font-bold tracking-widest">Public Advisory Mode</span>
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
              {messages.map((msg, i) => (
                <div key={i} className="space-y-4">
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
                        {isLoading && i === messages.length - 1 && msg.role === 'user' && (
                          <div className="mt-2 flex gap-1">
                            <div className="w-1 h-1 bg-white/50 rounded-full animate-bounce"></div>
                            <div className="w-1 h-1 bg-white/50 rounded-full animate-bounce [animation-delay:0.2s]"></div>
                            <div className="w-1 h-1 bg-white/50 rounded-full animate-bounce [animation-delay:0.4s]"></div>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Handoff CTA */}
                  {msg.handoff && (
                    <div className="flex justify-start pl-11">
                      <button className="flex items-center gap-2 px-6 py-3 bg-brand-primary text-black font-bold text-sm rounded-full hover:bg-cyan-400 transition-all shadow-md">
                        {msg.handoff.label} <ArrowUpRight size={16} />
                      </button>
                    </div>
                  )}

                  {/* Suggested Prompts */}
                  {msg.suggestedPrompts && !isLoading && (
                    <div className="flex flex-wrap gap-2 pl-11">
                      {msg.suggestedPrompts.map((prompt, j) => (
                        <button
                          key={j}
                          onClick={() => handleSend(prompt)}
                          className="px-4 py-2 bg-white border border-gray-200 rounded-full text-xs font-bold text-gray-600 hover:border-brand-primary hover:text-brand-primary transition-all shadow-sm"
                        >
                          {prompt}
                        </button>
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
                  onKeyPress={(e) => e.key === 'Enter' && handleSend()}
                  placeholder="Ask Odoo Copilot..."
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
                InsightPulseAI Odoo Copilot can make mistakes. Check important info.
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
                Ask Odoo Copilot
              </span>
            </motion.div>
          )}
        </AnimatePresence>
      </button>
    </div>
  );
};
