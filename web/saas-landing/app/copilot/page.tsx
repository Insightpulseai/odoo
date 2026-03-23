'use client'

import { useState } from 'react'

export default function OdooCopilotPage() {
  const [isChatOpen, setIsChatOpen] = useState(false)
  const [messages, setMessages] = useState([
    {
      type: 'ai',
      content: "Hi! I'm your Odoo Copilot. I can help you with sales quotes, invoice processing, pipeline analysis, and more. How can I assist you today?"
    },
    {
      type: 'user',
      content: 'Show me overdue invoices'
    },
    {
      type: 'ai',
      content: 'I found 3 overdue invoices totaling $12,450. The oldest is INV-2024-0142 for Acme Corp ($4,500), overdue by 15 days. Would you like me to send automated reminders?'
    }
  ])
  const [inputValue, setInputValue] = useState('')
  const [isTyping, setIsTyping] = useState(false)

  const sendMessage = () => {
    if (!inputValue.trim()) return

    // Add user message
    const newMessages = [...messages, { type: 'user', content: inputValue }]
    setMessages(newMessages)
    setInputValue('')
    setIsTyping(true)

    // Simulate AI response
    setTimeout(() => {
      setIsTyping(false)
      setMessages([
        ...newMessages,
        {
          type: 'ai',
          content: 'I can help you with that. Let me pull up the latest information from your Odoo system...'
        }
      ])
    }, 1500)
  }

  return (
    <div className="min-h-screen bg-[#0F2A44] py-[60px] px-[40px]">
      <style jsx global>{`
        @keyframes float {
          0%, 100% { transform: translate(0, 0) rotate(0deg); }
          33% { transform: translate(30px, -30px) rotate(120deg); }
          66% { transform: translate(-20px, 20px) rotate(240deg); }
        }

        @keyframes iconFloat {
          0%, 100% { transform: translateY(0px); }
          50% { transform: translateY(-20px); }
        }

        @keyframes slideUp {
          from {
            opacity: 0;
            transform: translateY(20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(10px); }
          to { opacity: 1; transform: translateY(0); }
        }

        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.5; }
        }

        @keyframes typing {
          0%, 60%, 100% { transform: translateY(0); }
          30% { transform: translateY(-10px); }
        }
      `}</style>

      {/* Header */}
      <header className="text-center mb-[60px] relative">
        <button className="absolute top-0 right-[40px] px-7 py-3 bg-white/10 backdrop-blur-[10px] border-[1.5px] border-white/20 rounded-xl text-white text-[15px] font-semibold cursor-pointer transition-all duration-300 flex items-center gap-2 hover:bg-white/15 hover:border-white/30 hover:-translate-y-0.5 hover:shadow-[0_4px_16px_rgba(0,0,0,0.2)]">
          <svg className="w-[18px] h-[18px]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
          </svg>
          Sign In
        </button>
        <h1 className="text-5xl font-bold text-white mb-4 font-[SF_Pro_Display,-apple-system,sans-serif]">
          Odoo Copilot
        </h1>
        <p className="text-xl text-white/70 max-w-[720px] mx-auto">
          Hyperrealistic AI-powered workflows that transform how your business operates
        </p>
      </header>

      {/* Use Case Cards Grid */}
      <div className="grid grid-cols-[repeat(auto-fit,minmax(380px,1fr))] gap-8 max-w-[1400px] mx-auto">
        {useCaseCards.map((card, index) => (
          <div
            key={index}
            className="bg-white rounded-[20px] overflow-hidden shadow-[0_8px_32px_rgba(0,0,0,0.3)] transition-all duration-300 cursor-pointer hover:-translate-y-2 hover:shadow-[0_16px_48px_rgba(0,0,0,0.4)]"
          >
            <div className="h-[320px] flex items-center justify-center bg-gradient-to-br from-[#0F2A44] to-[#1a3d5c] relative overflow-hidden">
              <div className="absolute inset-0 bg-[radial-gradient(circle_at_30%_50%,rgba(100,185,202,0.15)_0%,transparent_50%),radial-gradient(circle_at_70%_50%,rgba(123,192,67,0.1)_0%,transparent_50%)] animate-[float_20s_ease-in-out_infinite]" />
              <div className="relative z-[2] animate-[iconFloat_6s_ease-in-out_infinite]">
                {card.icon}
              </div>
            </div>
            <div className="p-8 bg-white">
              <h2 className="text-2xl font-bold mb-3 text-[#1a1a1a] font-[SF_Pro_Display,-apple-system,sans-serif]">
                {card.title}
              </h2>
              <p className="text-base text-[#666] mb-5 leading-relaxed">
                {card.description}
              </p>
              <div className="flex gap-2 flex-wrap">
                {card.tags.map((tag, i) => (
                  <span
                    key={i}
                    className={`px-3.5 py-1.5 rounded-[20px] text-[13px] font-medium ${
                      i === 0
                        ? 'bg-[#7BC043]/15 text-[#5a9c2f]'
                        : 'bg-[#0F2A44]/8 text-[#0F2A44]'
                    }`}
                  >
                    {tag}
                  </span>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Copilot Chat Widget */}
      <div className="fixed bottom-8 right-8 z-[1000]">
        {/* Chat Window */}
        {isChatOpen && (
          <div className="fixed bottom-28 right-8 w-[380px] h-[560px] bg-white rounded-[20px] shadow-[0_16px_48px_rgba(0,0,0,0.3)] flex flex-col overflow-hidden animate-[slideUp_0.3s_ease]">
            {/* Chat Header */}
            <div className="bg-gradient-to-br from-[#0F2A44] to-[#1a3d5c] p-5 text-white flex items-center gap-3">
              <div className="flex-1">
                <h3 className="text-lg font-semibold">Odoo Copilot</h3>
                <div className="flex items-center gap-1.5 text-[13px] text-white/70">
                  <span className="w-2 h-2 bg-[#7BC043] rounded-full animate-[pulse_2s_ease-in-out_infinite]" />
                  Online
                </div>
              </div>
            </div>

            {/* Messages */}
            <div className="flex-1 p-5 overflow-y-auto bg-[#F5F7FA] flex flex-col gap-4">
              {messages.map((msg, i) => (
                <div
                  key={i}
                  className={`flex gap-3 animate-[fadeIn_0.3s_ease] ${
                    msg.type === 'user' ? 'flex-row-reverse' : ''
                  }`}
                >
                  <div
                    className={`w-9 h-9 rounded-full flex items-center justify-center flex-shrink-0 ${
                      msg.type === 'user'
                        ? 'bg-gradient-to-br from-[#875A7B] to-[#7C4C6F]'
                        : 'bg-gradient-to-br from-[#7BC043] to-[#64B9CA]'
                    }`}
                  >
                    {msg.type === 'user' ? (
                      <svg className="w-5 h-5" fill="white" viewBox="0 0 24 24">
                        <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
                      </svg>
                    ) : (
                      <svg className="w-5 h-5" fill="white" viewBox="0 0 24 24">
                        <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm-1-13h2v6h-2zm0 8h2v2h-2z"/>
                      </svg>
                    )}
                  </div>
                  <div
                    className={`max-w-[70%] px-4 py-3 rounded-2xl text-sm leading-relaxed ${
                      msg.type === 'user'
                        ? 'bg-gradient-to-br from-[#875A7B] to-[#7C4C6F] text-white'
                        : 'bg-white shadow-[0_2px_8px_rgba(0,0,0,0.08)]'
                    }`}
                  >
                    {msg.content}
                  </div>
                </div>
              ))}
              {isTyping && (
                <div className="flex gap-3 animate-[fadeIn_0.3s_ease]">
                  <div className="w-9 h-9 rounded-full bg-gradient-to-br from-[#7BC043] to-[#64B9CA] flex items-center justify-center flex-shrink-0">
                    <svg className="w-5 h-5" fill="white" viewBox="0 0 24 24">
                      <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm-1-13h2v6h-2zm0 8h2v2h-2z"/>
                    </svg>
                  </div>
                  <div className="bg-white shadow-[0_2px_8px_rgba(0,0,0,0.08)] px-4 py-3 rounded-2xl flex gap-1">
                    <div className="w-2 h-2 bg-[#9AA5B1] rounded-full animate-[typing_1.4s_ease-in-out_infinite]" />
                    <div className="w-2 h-2 bg-[#9AA5B1] rounded-full animate-[typing_1.4s_ease-in-out_infinite] [animation-delay:0.2s]" />
                    <div className="w-2 h-2 bg-[#9AA5B1] rounded-full animate-[typing_1.4s_ease-in-out_infinite] [animation-delay:0.4s]" />
                  </div>
                </div>
              )}
            </div>

            {/* Input */}
            <div className="p-4 border-t border-[#E4E7EB] bg-white flex gap-3">
              <input
                type="text"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                placeholder="Ask me anything..."
                className="flex-1 px-4 py-3 border-[1.5px] border-[#E4E7EB] rounded-xl text-sm outline-none transition-all duration-200 focus:border-[#7BC043] focus:shadow-[0_0_0_3px_rgba(123,192,67,0.1)]"
              />
              <button
                onClick={sendMessage}
                className="w-11 h-11 bg-gradient-to-br from-[#7BC043] to-[#64B9CA] border-none rounded-xl flex items-center justify-center cursor-pointer transition-all duration-200 hover:scale-105 hover:shadow-[0_4px_12px_rgba(123,192,67,0.4)]"
              >
                <svg className="w-5 h-5" fill="white" viewBox="0 0 24 24">
                  <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
                </svg>
              </button>
            </div>
          </div>
        )}

        {/* Floating Button */}
        <button
          onClick={() => setIsChatOpen(!isChatOpen)}
          className={`w-16 h-16 rounded-full flex items-center justify-center cursor-pointer shadow-[0_8px_24px_rgba(123,192,67,0.4)] transition-all duration-300 border-2 border-white/20 hover:scale-110 hover:shadow-[0_12px_32px_rgba(123,192,67,0.6)] ${
            isChatOpen
              ? 'bg-gradient-to-br from-[#E5484D] to-[#F6C445]'
              : 'bg-gradient-to-br from-[#7BC043] to-[#64B9CA]'
          }`}
        >
          <svg className="w-8 h-8" fill="white" viewBox="0 0 24 24">
            <path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 14H6l-2 2V4h16v12z"/>
            <circle cx="12" cy="10" r="1.5"/>
            <circle cx="8" cy="10" r="1.5"/>
            <circle cx="16" cy="10" r="1.5"/>
          </svg>
        </button>
      </div>
    </div>
  )
}

// Use case cards data with SVG icons
const useCaseCards = [
  {
    title: 'CRM Pipeline Analysis',
    description: 'Identify at-risk deals, suggest optimal follow-up timing, and forecast revenue with AI-powered insights across your entire sales pipeline.',
    tags: ['Sales', 'Forecasting', 'Predictive AI'],
    icon: <CRMIcon />
  },
  {
    title: 'Invoice Document Processing',
    description: 'Extract invoice data automatically from PDFs and images, match to purchase orders, and flag discrepancies before approval.',
    tags: ['Finance', 'OCR', 'Automation'],
    icon: <InvoiceIcon />
  },
  {
    title: 'Cost Scenario Modeling',
    description: 'Simulate raw material price changes and see instant impact on product profitability across your manufacturing portfolio.',
    tags: ['Manufacturing', 'What-If Analysis', 'Pricing'],
    icon: <CostIcon />
  },
  {
    title: 'Task Organization',
    description: 'Automatically prioritize tasks, detect bottlenecks, and suggest resource reallocation across your project portfolio.',
    tags: ['Projects', 'Kanban', 'Resource Planning'],
    icon: <TaskIcon />
  },
  {
    title: 'Quote Generation',
    description: 'Generate professional quotations from natural language requests, pulling current pricing and availability automatically.',
    tags: ['Sales', 'Voice Commands', 'Templates'],
    icon: <QuoteIcon />
  },
  {
    title: 'Invoice Reconciliation',
    description: 'Spot mismatches between invoices and purchase orders instantly, reducing month-end close time from days to hours.',
    tags: ['Finance', 'Variance Analysis', 'Compliance'],
    icon: <ReconIcon />
  }
]

// SVG Icon Components
function CRMIcon() {
  return (
    <svg width="180" height="180" viewBox="0 0 128 128" fill="none">
      <defs>
        <filter id="floatShadow1" x="-50%" y="-50%" width="200%" height="200%">
          <feGaussianBlur in="SourceAlpha" stdDeviation="8" />
          <feOffset dx="0" dy="12" />
          <feComponentTransfer><feFuncA type="linear" slope="0.5" /></feComponentTransfer>
          <feMerge><feMergeNode /><feMergeNode in="SourceGraphic" /></feMerge>
        </filter>
        <linearGradient id="paperGrad1" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#F5F7FA" />
          <stop offset="100%" stopColor="#E4E7EB" />
        </linearGradient>
      </defs>
      <g filter="url(#floatShadow1)">
        <path d="M36 20 H92 C94 20 96 22 96 24 V100 C96 102 94 104 92 104 H36 C34 104 32 102 32 100 V24 C32 22 34 20 36 20 Z" fill="#fff" opacity="0.4" transform="translate(8, -8)"/>
        <path d="M36 20 H92 C94 20 96 22 96 24 V100 C96 102 94 104 92 104 H36 C34 104 32 102 32 100 V24 C32 22 34 20 36 20 Z" fill="#fff" opacity="0.6" transform="translate(4, -4)"/>
        <path d="M32 24 H80 L100 44 V108 C100 112 96 116 92 116 H32 C28 116 24 112 24 108 V32 C24 28 28 24 32 24 Z" fill="url(#paperGrad1)" stroke="#D7DDE6" strokeWidth="1.5"/>
        <path d="M80 24 V44 H100" fill="#CBD2D9" opacity="0.6"/>
        <circle cx="62" cy="64" r="18" fill="rgba(228, 84, 77, 0.15)" stroke="#E5484D" strokeWidth="2"/>
        <circle cx="62" cy="64" r="8" fill="#E5484D"/>
        <circle cx="46" cy="88" r="6" fill="rgba(228, 84, 77, 0.5)"/>
        <circle cx="78" cy="88" r="6" fill="rgba(228, 84, 77, 0.5)"/>
        <line x1="62" y1="72" x2="46" y2="82" stroke="#E5484D" strokeWidth="2"/>
        <line x1="62" y1="72" x2="78" y2="82" stroke="#E5484D" strokeWidth="2"/>
      </g>
      <g transform="translate(52, 76)">
        <rect x="0" y="0" width="64" height="36" rx="10" fill="#E5484D" fillOpacity="0.95" stroke="rgba(255,255,255,0.5)" strokeWidth="1.5" filter="url(#floatShadow1)"/>
        <path d="M4 10 Q 32 36 60 10" stroke="white" strokeWidth="12" strokeOpacity="0.15" strokeLinecap="round" transform="translate(0, -4)"/>
        <text x="32" y="24" fontFamily="Arial, sans-serif" fontSize="16" fontWeight="900" fill="white" textAnchor="middle" letterSpacing="1.5">CRM</text>
      </g>
      <path d="M26 32 V106 Q 26 114 34 114 H90" fill="none" stroke="white" strokeWidth="2.5" strokeOpacity="0.7"/>
    </svg>
  )
}

function InvoiceIcon() {
  return (
    <svg width="180" height="180" viewBox="0 0 128 128" fill="none">
      <defs>
        <filter id="floatShadow2" x="-50%" y="-50%" width="200%" height="200%">
          <feGaussianBlur in="SourceAlpha" stdDeviation="8" />
          <feOffset dx="0" dy="12"/>
          <feComponentTransfer><feFuncA type="linear" slope="0.5" /></feComponentTransfer>
          <feMerge><feMergeNode /><feMergeNode in="SourceGraphic" /></feMerge>
        </filter>
        <linearGradient id="paperGrad2" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#F5F7FA" />
          <stop offset="100%" stopColor="#E4E7EB" />
        </linearGradient>
      </defs>
      <g filter="url(#floatShadow2)">
        <path d="M36 20 H92 C94 20 96 22 96 24 V100 C96 102 94 104 92 104 H36 C34 104 32 102 32 100 V24 C32 22 34 20 36 20 Z" fill="#fff" opacity="0.4" transform="translate(8, -8)"/>
        <path d="M36 20 H92 C94 20 96 22 96 24 V100 C96 102 94 104 92 104 H36 C34 104 32 102 32 100 V24 C32 22 34 20 36 20 Z" fill="#fff" opacity="0.6" transform="translate(4, -4)"/>
        <path d="M32 24 H80 L100 44 V108 C100 112 96 116 92 116 H32 C28 116 24 112 24 108 V32 C24 28 28 24 32 24 Z" fill="url(#paperGrad2)" stroke="#D7DDE6" strokeWidth="1.5"/>
        <path d="M80 24 V44 H100" fill="#CBD2D9" opacity="0.6"/>
        <rect x="40" y="52" width="48" height="5" rx="2" fill="#9AA5B1" opacity="0.3"/>
        <rect x="40" y="62" width="55" height="5" rx="2" fill="#9AA5B1" opacity="0.3"/>
        <rect x="40" y="72" width="52" height="5" rx="2" fill="#9AA5B1" opacity="0.3"/>
        <circle cx="62" cy="90" r="12" fill="rgba(123, 192, 67, 0.2)" stroke="#7BC043" strokeWidth="2"/>
        <path d="M56 90 L60 94 L68 84" stroke="#7BC043" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" fill="none"/>
      </g>
      <g transform="translate(48, 76)">
        <rect x="0" y="0" width="72" height="36" rx="10" fill="#7BC043" fillOpacity="0.95" stroke="rgba(255,255,255,0.5)" strokeWidth="1.5" filter="url(#floatShadow2)"/>
        <path d="M4 10 Q 36 36 68 10" stroke="white" strokeWidth="12" strokeOpacity="0.15" strokeLinecap="round" transform="translate(0, -4)"/>
        <text x="36" y="24" fontFamily="Arial, sans-serif" fontSize="15" fontWeight="900" fill="white" textAnchor="middle" letterSpacing="1">INVOICE</text>
      </g>
      <path d="M26 32 V106 Q 26 114 34 114 H90" fill="none" stroke="white" strokeWidth="2.5" strokeOpacity="0.7"/>
    </svg>
  )
}

function CostIcon() {
  return (
    <svg width="180" height="180" viewBox="0 0 128 128" fill="none">
      <defs>
        <filter id="floatShadow3" x="-50%" y="-50%" width="200%" height="200%">
          <feGaussianBlur in="SourceAlpha" stdDeviation="8" />
          <feOffset dx="0" dy="12"/>
          <feComponentTransfer><feFuncA type="linear" slope="0.5" /></feComponentTransfer>
          <feMerge><feMergeNode /><feMergeNode in="SourceGraphic" /></feMerge>
        </filter>
        <linearGradient id="paperGrad3" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#F5F7FA" />
          <stop offset="100%" stopColor="#E4E7EB" />
        </linearGradient>
      </defs>
      <g filter="url(#floatShadow3)">
        <path d="M36 20 H92 C94 20 96 22 96 24 V100 C96 102 94 104 92 104 H36 C34 104 32 102 32 100 V24 C32 22 34 20 36 20 Z" fill="#fff" opacity="0.4" transform="translate(8, -8)"/>
        <path d="M36 20 H92 C94 20 96 22 96 24 V100 C96 102 94 104 92 104 H36 C34 104 32 102 32 100 V24 C32 22 34 20 36 20 Z" fill="#fff" opacity="0.6" transform="translate(4, -4)"/>
        <path d="M32 24 H80 L100 44 V108 C100 112 96 116 92 116 H32 C28 116 24 112 24 108 V32 C24 28 28 24 32 24 Z" fill="url(#paperGrad3)" stroke="#D7DDE6" strokeWidth="1.5"/>
        <path d="M80 24 V44 H100" fill="#CBD2D9" opacity="0.6"/>
        <rect x="40" y="75" width="8" height="25" rx="2" fill="#64B9CA" opacity="0.7"/>
        <rect x="52" y="65" width="8" height="35" rx="2" fill="#64B9CA" opacity="0.7"/>
        <rect x="64" y="55" width="8" height="45" rx="2" fill="#F6C445" opacity="0.7"/>
        <rect x="76" y="70" width="8" height="30" rx="2" fill="#7BC043" opacity="0.7"/>
      </g>
      <g transform="translate(44, 76)">
        <rect x="0" y="0" width="78" height="36" rx="10" fill="#64B9CA" fillOpacity="0.95" stroke="rgba(255,255,255,0.5)" strokeWidth="1.5" filter="url(#floatShadow3)"/>
        <path d="M4 10 Q 39 36 74 10" stroke="white" strokeWidth="12" strokeOpacity="0.15" strokeLinecap="round" transform="translate(0, -4)"/>
        <text x="39" y="24" fontFamily="Arial, sans-serif" fontSize="14" fontWeight="900" fill="white" textAnchor="middle" letterSpacing="1">COSTS</text>
      </g>
      <path d="M26 32 V106 Q 26 114 34 114 H90" fill="none" stroke="white" strokeWidth="2.5" strokeOpacity="0.7"/>
    </svg>
  )
}

function TaskIcon() {
  return (
    <svg width="180" height="180" viewBox="0 0 128 128" fill="none">
      <defs>
        <filter id="floatShadow4" x="-50%" y="-50%" width="200%" height="200%">
          <feGaussianBlur in="SourceAlpha" stdDeviation="8" />
          <feOffset dx="0" dy="12"/>
          <feComponentTransfer><feFuncA type="linear" slope="0.5" /></feComponentTransfer>
          <feMerge><feMergeNode /><feMergeNode in="SourceGraphic" /></feMerge>
        </filter>
        <linearGradient id="paperGrad4" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#F5F7FA" />
          <stop offset="100%" stopColor="#E4E7EB" />
        </linearGradient>
      </defs>
      <g filter="url(#floatShadow4)">
        <path d="M36 20 H92 C94 20 96 22 96 24 V100 C96 102 94 104 92 104 H36 C34 104 32 102 32 100 V24 C32 22 34 20 36 20 Z" fill="#fff" opacity="0.4" transform="translate(8, -8)"/>
        <path d="M36 20 H92 C94 20 96 22 96 24 V100 C96 102 94 104 92 104 H36 C34 104 32 102 32 100 V24 C32 22 34 20 36 20 Z" fill="#fff" opacity="0.6" transform="translate(4, -4)"/>
        <path d="M32 24 H80 L100 44 V108 C100 112 96 116 92 116 H32 C28 116 24 112 24 108 V32 C24 28 28 24 32 24 Z" fill="url(#paperGrad4)" stroke="#D7DDE6" strokeWidth="1.5"/>
        <path d="M80 24 V44 H100" fill="#CBD2D9" opacity="0.6"/>
        <rect x="36" y="50" width="18" height="24" rx="3" fill="#F6C445" opacity="0.4" stroke="#F6C445" strokeWidth="1"/>
        <rect x="58" y="50" width="18" height="24" rx="3" fill="#64B9CA" opacity="0.4" stroke="#64B9CA" strokeWidth="1"/>
        <rect x="80" y="50" width="18" height="24" rx="3" fill="#7BC043" opacity="0.4" stroke="#7BC043" strokeWidth="1"/>
        <rect x="36" y="78" width="18" height="14" rx="2" fill="#E5484D" opacity="0.3" stroke="#E5484D" strokeWidth="1"/>
      </g>
      <g transform="translate(44, 76)">
        <rect x="0" y="0" width="78" height="36" rx="10" fill="#875A7B" fillOpacity="0.95" stroke="rgba(255,255,255,0.5)" strokeWidth="1.5" filter="url(#floatShadow4)"/>
        <path d="M4 10 Q 39 36 74 10" stroke="white" strokeWidth="12" strokeOpacity="0.15" strokeLinecap="round" transform="translate(0, -4)"/>
        <text x="39" y="24" fontFamily="Arial, sans-serif" fontSize="14" fontWeight="900" fill="white" textAnchor="middle" letterSpacing="1">TASKS</text>
      </g>
      <path d="M26 32 V106 Q 26 114 34 114 H90" fill="none" stroke="white" strokeWidth="2.5" strokeOpacity="0.7"/>
    </svg>
  )
}

function QuoteIcon() {
  return (
    <svg width="180" height="180" viewBox="0 0 128 128" fill="none">
      <defs>
        <filter id="floatShadow5" x="-50%" y="-50%" width="200%" height="200%">
          <feGaussianBlur in="SourceAlpha" stdDeviation="8" />
          <feOffset dx="0" dy="12"/>
          <feComponentTransfer><feFuncA type="linear" slope="0.5" /></feComponentTransfer>
          <feMerge><feMergeNode /><feMergeNode in="SourceGraphic" /></feMerge>
        </filter>
        <linearGradient id="paperGrad5" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#F5F7FA" />
          <stop offset="100%" stopColor="#E4E7EB" />
        </linearGradient>
      </defs>
      <g filter="url(#floatShadow5)">
        <path d="M36 20 H92 C94 20 96 22 96 24 V100 C96 102 94 104 92 104 H36 C34 104 32 102 32 100 V24 C32 22 34 20 36 20 Z" fill="#fff" opacity="0.4" transform="translate(8, -8)"/>
        <path d="M36 20 H92 C94 20 96 22 96 24 V100 C96 102 94 104 92 104 H36 C34 104 32 102 32 100 V24 C32 22 34 20 36 20 Z" fill="#fff" opacity="0.6" transform="translate(4, -4)"/>
        <path d="M32 24 H80 L100 44 V108 C100 112 96 116 92 116 H32 C28 116 24 112 24 108 V32 C24 28 28 24 32 24 Z" fill="url(#paperGrad5)" stroke="#D7DDE6" strokeWidth="1.5"/>
        <path d="M80 24 V44 H100" fill="#CBD2D9" opacity="0.6"/>
        <rect x="40" y="50" width="48" height="8" rx="4" fill="#875A7B" opacity="0.8"/>
        <rect x="40" y="62" width="35" height="4" rx="2" fill="#9AA5B1" opacity="0.3"/>
        <rect x="40" y="70" width="42" height="4" rx="2" fill="#9AA5B1" opacity="0.3"/>
        <rect x="40" y="80" width="48" height="20" rx="3" fill="rgba(123, 192, 67, 0.1)" stroke="#7BC043" strokeWidth="1"/>
        <line x1="40" y1="88" x2="88" y2="88" stroke="#7BC043" strokeWidth="1"/>
      </g>
      <g transform="translate(44, 76)">
        <rect x="0" y="0" width="78" height="36" rx="10" fill="#7BC043" fillOpacity="0.95" stroke="rgba(255,255,255,0.5)" strokeWidth="1.5" filter="url(#floatShadow5)"/>
        <path d="M4 10 Q 39 36 74 10" stroke="white" strokeWidth="12" strokeOpacity="0.15" strokeLinecap="round" transform="translate(0, -4)"/>
        <text x="39" y="24" fontFamily="Arial, sans-serif" fontSize="14" fontWeight="900" fill="white" textAnchor="middle" letterSpacing="1">QUOTE</text>
      </g>
      <path d="M26 32 V106 Q 26 114 34 114 H90" fill="none" stroke="white" strokeWidth="2.5" strokeOpacity="0.7"/>
    </svg>
  )
}

function ReconIcon() {
  return (
    <svg width="180" height="180" viewBox="0 0 128 128" fill="none">
      <defs>
        <filter id="floatShadow6" x="-50%" y="-50%" width="200%" height="200%">
          <feGaussianBlur in="SourceAlpha" stdDeviation="8" />
          <feOffset dx="0" dy="12"/>
          <feComponentTransfer><feFuncA type="linear" slope="0.5" /></feComponentTransfer>
          <feMerge><feMergeNode /><feMergeNode in="SourceGraphic" /></feMerge>
        </filter>
        <linearGradient id="paperGrad6" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#F5F7FA" />
          <stop offset="100%" stopColor="#E4E7EB" />
        </linearGradient>
      </defs>
      <g filter="url(#floatShadow6)">
        <path d="M36 20 H92 C94 20 96 22 96 24 V100 C96 102 94 104 92 104 H36 C34 104 32 102 32 100 V24 C32 22 34 20 36 20 Z" fill="#fff" opacity="0.4" transform="translate(8, -8)"/>
        <path d="M36 20 H92 C94 20 96 22 96 24 V100 C96 102 94 104 92 104 H36 C34 104 32 102 32 100 V24 C32 22 34 20 36 20 Z" fill="#fff" opacity="0.6" transform="translate(4, -4)"/>
        <path d="M32 24 H80 L100 44 V108 C100 112 96 116 92 116 H32 C28 116 24 112 24 108 V32 C24 28 28 24 32 24 Z" fill="url(#paperGrad6)" stroke="#D7DDE6" strokeWidth="1.5"/>
        <path d="M80 24 V44 H100" fill="#CBD2D9" opacity="0.6"/>
        <rect x="38" y="52" width="52" height="50" rx="3" fill="white" stroke="#D7DDE6" strokeWidth="1"/>
        <line x1="38" y1="62" x2="90" y2="62" stroke="#D7DDE6" strokeWidth="1"/>
        <line x1="58" y1="52" x2="58" y2="102" stroke="#D7DDE6" strokeWidth="1"/>
        <line x1="70" y1="52" x2="70" y2="102" stroke="#D7DDE6" strokeWidth="1"/>
        <rect x="71" y="70" width="18" height="10" fill="#FFF3E0"/>
        <text x="80" y="78" fontFamily="monospace" fontSize="7" fontWeight="bold" fill="#F57C00" textAnchor="middle">+$550</text>
      </g>
      <g transform="translate(40, 76)">
        <rect x="0" y="0" width="86" height="36" rx="10" fill="#F6C445" fillOpacity="0.95" stroke="rgba(255,255,255,0.5)" strokeWidth="1.5" filter="url(#floatShadow6)"/>
        <path d="M4 10 Q 43 36 82 10" stroke="white" strokeWidth="12" strokeOpacity="0.15" strokeLinecap="round" transform="translate(0, -4)"/>
        <text x="43" y="24" fontFamily="Arial, sans-serif" fontSize="13" fontWeight="900" fill="white" textAnchor="middle" letterSpacing="1">RECON</text>
      </g>
      <path d="M26 32 V106 Q 26 114 34 114 H90" fill="none" stroke="white" strokeWidth="2.5" strokeOpacity="0.7"/>
    </svg>
  )
}
