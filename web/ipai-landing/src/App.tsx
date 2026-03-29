import { useState, useEffect, useRef, useCallback } from 'react';
import {
  Search, ChevronRight, ChevronDown, LayoutDashboard, Smartphone, Database, Factory, Box, Globe, X,
  Cpu, Cloud, BarChart3, Users, Settings, Briefcase, ShieldCheck, CheckCircle2,
  ArrowRight, PlayCircle, BookOpen, MessageSquare, Newspaper, Zap, Lock, BarChart,
  Target, Tv, ShoppingBag, Landmark, TrendingUp, HelpCircle, Mail, MapPin, ExternalLink,
  Layers, FileText, Phone, Calendar, Lightbulb, Palette, PenTool, Eye, Quote, Menu
} from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';
import { AskPulser } from './components/AskPulser';

// --- Types ---
type PageId = 'home' | 'products' | 'solutions' | 'marketing' | 'media' | 'retail' | 'finance' | 'resources' | 'pricing' | 'company' | 'docs' | 'trust' | 'contact' | 'marketing_use_cases' | 'media_reference_patterns' | 'privacy' | 'terms' | 'careers' | 'newsroom' | 'login';

// --- External URLs ---
const EXTERNAL_URLS = {
  demo: 'https://insightpulseai.zohobookings.com/',  // Zoho Bookings — set up at bookings.zoho.com
  login: 'https://erp.insightpulseai.com/web/login',
  github: 'https://github.com/InsightPulseAI',
  email: 'mailto:business@insightpulseai.com',
  mail: 'mailto:business@insightpulseai.com',
  support: 'mailto:support@insightpulseai.com',
} as const;

// Hash <-> PageId mapping for URL sync
const VALID_PAGES: PageId[] = ['home','products','solutions','marketing','media','retail','finance','resources','pricing','company','docs','trust','contact','marketing_use_cases','media_reference_patterns','privacy','terms','careers','newsroom','login'];

function pageIdFromHash(hash: string): PageId {
  const raw = hash.replace('#', '').replace(/^\//, '');
  if (raw === '' || raw === 'home') return 'home';
  if (VALID_PAGES.includes(raw as PageId)) return raw as PageId;
  return 'home';
}

function hashFromPageId(page: PageId): string {
  return page === 'home' ? '' : `#${page}`;
}

// --- Shared Components ---

// Fluent 2 design tokens — exact values from @fluentui/tokens
// Sources: fluent2.microsoft.design/motion, /elevation, /typography, /iconography, /material
// Principles: Natural on Every Platform, Built for Focus, One for All, Unmistakably [Brand]
const MOTION = {
  // Durations (seconds for framer-motion)
  durationUltraFast: 0.05,   // 50ms  — tooltips, micro-feedback
  durationFaster: 0.1,       // 100ms — hover states, toggles
  durationFast: 0.15,        // 150ms — menus, dropdowns, chips
  durationNormal: 0.2,       // 200ms — page transitions, modals
  durationGentle: 0.25,      // 250ms — hero reveals, large panels
  durationSlow: 0.3,         // 300ms — reserved
  // Curves (cubic-bezier arrays for framer-motion)
  curveDecelerateMid: [0, 0, 0, 1] as const,        // enter: fast out, slow in
  curveAccelerateMid: [1, 0, 1, 1] as const,        // exit: slow out, fast in
  curveEasyEase: [0.33, 0, 0.67, 1] as const,       // symmetric ease
  curveDecelerateMin: [0.33, 0, 0.1, 1] as const,   // gentle enter
};
// Elevation: shadow tokens (light theme, from @fluentui/tokens webLightTheme)
const SHADOW = {
  shadow4: '0 0 2px rgba(0,0,0,0.12), 0 2px 4px rgba(0,0,0,0.14)',      // cards at rest
  shadow8: '0 0 2px rgba(0,0,0,0.12), 0 4px 8px rgba(0,0,0,0.14)',      // hover cards, FABs
  shadow16: '0 0 2px rgba(0,0,0,0.12), 0 8px 16px rgba(0,0,0,0.14)',    // raised cards, menus
  shadow28: '0 0 8px rgba(0,0,0,0.12), 0 14px 28px rgba(0,0,0,0.14)',   // panels, side nav
  shadow64: '0 0 8px rgba(0,0,0,0.12), 0 32px 64px rgba(0,0,0,0.14)',   // dialogs
};
// Fluent shadow hover handlers (card rest → hover elevation)
const fluentCardShadow = {
  style: { boxShadow: SHADOW.shadow4 } as React.CSSProperties,
  onMouseEnter: (e: React.MouseEvent<HTMLElement>) => { e.currentTarget.style.boxShadow = SHADOW.shadow8; },
  onMouseLeave: (e: React.MouseEvent<HTMLElement>) => { e.currentTarget.style.boxShadow = SHADOW.shadow4; },
};

const PAGE_TRANSITION = {
  initial: { opacity: 0 },
  animate: { opacity: 1 },
  exit: { opacity: 0 },
  transition: { duration: MOTION.durationNormal, ease: MOTION.curveDecelerateMid },
};

const MegaMenuPanel = ({ children, isOpen, align = 'center' }: { children: React.ReactNode, isOpen: boolean, align?: 'left' | 'center' | 'right' }) => (
  <AnimatePresence>
    {isOpen && (
      <motion.div
        initial={{ opacity: 0, y: 6 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: 6 }}
        transition={{ duration: MOTION.durationFast, ease: MOTION.curveDecelerateMid }}
        style={{ boxShadow: SHADOW.shadow16 }}
        className={`absolute top-full bg-white rounded-2xl border border-gray-100 mt-2 overflow-hidden ${
          align === 'left' ? 'left-0' : align === 'right' ? 'right-0' : 'left-1/2 -translate-x-1/2'
        }`}
      >
        {children}
      </motion.div>
    )}
  </AnimatePresence>
);

const Navbar = ({ currentPage, setPage }: { currentPage: PageId, setPage: (p: PageId) => void }) => {
  const [openMenu, setOpenMenu] = useState<string | null>(null);
  const [mobileOpen, setMobileOpen] = useState(false);
  const [mobileSection, setMobileSection] = useState<string | null>(null);
  const closeTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  const open = (menu: string) => {
    if (closeTimer.current) clearTimeout(closeTimer.current);
    setOpenMenu(menu);
  };
  const scheduleClose = () => {
    closeTimer.current = setTimeout(() => setOpenMenu(null), 150);
  };
  const cancelClose = () => {
    if (closeTimer.current) clearTimeout(closeTimer.current);
  };

  const mobilNav = (page: PageId) => {
    setPage(page);
    setMobileOpen(false);
    setMobileSection(null);
  };

  // Close mobile menu on escape
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === 'Escape') { setMobileOpen(false); setOpenMenu(null); }
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, []);

  // Lock body scroll when mobile menu is open
  useEffect(() => {
    document.body.style.overflow = mobileOpen ? 'hidden' : '';
    return () => { document.body.style.overflow = ''; };
  }, [mobileOpen]);

  return (
    <>
    <nav className="fixed top-0 left-0 right-0 h-16 bg-white/90 backdrop-blur-md z-50 px-6 md:px-12 flex items-center justify-between border-b border-gray-100">
      <div className="flex items-center gap-12">
        <button onClick={() => { setPage('home'); setMobileOpen(false); }} className="flex items-center gap-3 group" aria-label="Home">
          <img src="/logo.png" alt="InsightPulseAI" className="w-12 h-12 rounded-lg group-hover:scale-105 transition-transform" />
        </button>

        <div className="hidden xl:flex items-center gap-8 text-[14px] font-bold text-gray-800">

          {/* Products mega-menu */}
          <div className="relative" onMouseEnter={() => open('products')} onMouseLeave={scheduleClose}>
            <button onClick={() => { setPage('products'); setOpenMenu(null); }}
              className={`flex items-center gap-1 py-2 hover:text-brand-primary transition-colors duration-[150ms] ${currentPage === 'products' ? 'text-brand-primary' : ''}`}>
              Products <ChevronDown size={13} className={`transition-transform duration-[150ms] ${openMenu === 'products' ? 'rotate-180' : ''}`} />
            </button>
            <MegaMenuPanel isOpen={openMenu === 'products'} align="left">
              <div className="w-[560px] p-6" onMouseEnter={cancelClose} onMouseLeave={scheduleClose}>
                <div className="grid grid-cols-2 gap-2">
                  {[
                    { icon: <Cloud size={20} />, title: "Odoo on Cloud", desc: "Hosted ERP, CRM, finance, inventory", page: 'products' as PageId },
                    { icon: <Cpu size={20} />, title: "Pulser", desc: "AI guidance inside your workflows", page: 'products' as PageId },
                    { icon: <ShieldCheck size={20} />, title: "Cloud Operations", desc: "Deploy, govern, monitor, evolve", page: 'products' as PageId },
                    { icon: <BarChart size={20} />, title: "Analytics & Dashboards", desc: "Operational dashboards & reporting", page: 'products' as PageId },
                    { icon: <BookOpen size={20} />, title: "PrismaLab", desc: "Systematic reviews & meta-analysis", page: 'products' as PageId },
                  ].map((item, i) => (
                    <button key={i} onClick={() => { setPage(item.page); setOpenMenu(null); }}
                      className="flex items-start gap-3 p-3 hover:bg-brand-light rounded-xl transition-colors text-left">
                      <div className="text-brand-primary mt-0.5">{item.icon}</div>
                      <div>
                        <p className="font-bold text-sm">{item.title}</p>
                        <p className="text-xs text-gray-500 font-normal">{item.desc}</p>
                      </div>
                    </button>
                  ))}
                </div>
                <div className="mt-4 pt-4 border-t border-gray-100">
                  <button onClick={() => { setPage('products'); setOpenMenu(null); }}
                    className="text-xs font-bold text-brand-primary flex items-center gap-1 hover:gap-2 transition-all">
                    See all products <ArrowRight size={14} />
                  </button>
                </div>
              </div>
            </MegaMenuPanel>
          </div>

          {/* Solutions mega-menu */}
          <div className="relative" onMouseEnter={() => open('solutions')} onMouseLeave={scheduleClose}>
            <button onClick={() => { setPage('solutions'); setOpenMenu(null); }}
              className={`flex items-center gap-1 py-2 hover:text-brand-primary transition-colors duration-[150ms] ${['solutions','marketing','media','retail','finance'].includes(currentPage) ? 'text-brand-primary' : ''}`}>
              Solutions <ChevronDown size={13} className={`transition-transform duration-[150ms] ${openMenu === 'solutions' ? 'rotate-180' : ''}`} />
            </button>
            <MegaMenuPanel isOpen={openMenu === 'solutions'} align="left">
              <div className="w-[620px] p-6" onMouseEnter={cancelClose} onMouseLeave={scheduleClose}>
                <div className="grid grid-cols-2 gap-x-6">
                  <div>
                    <p className="text-[11px] font-bold text-gray-400 uppercase tracking-widest mb-3 px-3">By Industry</p>
                    {[
                      { icon: <Target size={18} />, title: "Marketing Operations", desc: "Unified customer & campaign data", page: 'marketing' as PageId },
                      { icon: <Tv size={18} />, title: "Media & Entertainment", desc: "Audience & monetization workflows", page: 'media' as PageId },
                      { icon: <ShoppingBag size={18} />, title: "Retail Operations", desc: "Inventory & supply-chain resilience", page: 'retail' as PageId },
                      { icon: <Landmark size={18} />, title: "Financial Operations", desc: "Controls, risk & AI decisions", page: 'finance' as PageId },
                    ].map((item, i) => (
                      <button key={i} onClick={() => { setPage(item.page); setOpenMenu(null); }}
                        className="flex items-start gap-3 p-3 hover:bg-brand-light rounded-xl transition-colors text-left w-full">
                        <div className="text-brand-primary mt-0.5">{item.icon}</div>
                        <div>
                          <p className="font-bold text-sm">{item.title}</p>
                          <p className="text-xs text-gray-500 font-normal">{item.desc}</p>
                        </div>
                      </button>
                    ))}
                  </div>
                  <div>
                    <p className="text-[11px] font-bold text-gray-400 uppercase tracking-widest mb-3 px-3">By Use Case</p>
                    {[
                      { icon: <Calendar size={18} />, title: "Campaign Planning", desc: "Plan, execute, measure campaigns", page: 'marketing_use_cases' as PageId },
                      { icon: <FileText size={18} />, title: "Month-End Close", desc: "Automate reconciliation & reporting", page: 'finance' as PageId },
                      { icon: <ShieldCheck size={18} />, title: "Expense & Compliance", desc: "Policy controls & audit trails", page: 'finance' as PageId },
                      { icon: <Box size={18} />, title: "Inventory & Fulfillment", desc: "Real-time stock & order flow", page: 'retail' as PageId },
                    ].map((item, i) => (
                      <button key={i} onClick={() => { setPage(item.page); setOpenMenu(null); }}
                        className="flex items-start gap-3 p-3 hover:bg-brand-light rounded-xl transition-colors text-left w-full">
                        <div className="text-brand-primary mt-0.5">{item.icon}</div>
                        <div>
                          <p className="font-bold text-sm">{item.title}</p>
                          <p className="text-xs text-gray-500 font-normal">{item.desc}</p>
                        </div>
                      </button>
                    ))}
                    <div className="mt-3 pt-3 border-t border-gray-100 px-3">
                      <button onClick={() => { setPage('solutions'); setOpenMenu(null); }}
                        className="text-xs font-bold text-brand-primary flex items-center gap-1 hover:gap-2 transition-all">
                        All solutions <ArrowRight size={14} />
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </MegaMenuPanel>
          </div>

          <button onClick={() => setPage('pricing')} className={`py-2 hover:text-brand-primary transition-colors ${currentPage === 'pricing' ? 'text-brand-primary' : ''}`}>Pricing</button>

          {/* Resources mega-menu */}
          <div className="relative" onMouseEnter={() => open('resources')} onMouseLeave={scheduleClose}>
            <button onClick={() => { setPage('resources'); setOpenMenu(null); }}
              className={`flex items-center gap-1 py-2 hover:text-brand-primary transition-colors duration-[150ms] ${['docs','resources','media_reference_patterns'].includes(currentPage) ? 'text-brand-primary' : ''}`}>
              Resources <ChevronDown size={13} className={`transition-transform duration-[150ms] ${openMenu === 'resources' ? 'rotate-180' : ''}`} />
            </button>
            <MegaMenuPanel isOpen={openMenu === 'resources'} align="left">
              <div className="w-[520px] p-6" onMouseEnter={cancelClose} onMouseLeave={scheduleClose}>
                <div className="grid grid-cols-2 gap-x-6">
                  <div>
                    <p className="text-[11px] font-bold text-gray-400 uppercase tracking-widest mb-3 px-3">Learn</p>
                    {[
                      { icon: <BookOpen size={18} />, title: "Documentation", desc: "Technical guides & API reference", page: 'docs' as PageId },
                      { icon: <FileText size={18} />, title: "Resource Library", desc: "Whitepapers, webinars, templates", page: 'resources' as PageId },
                      { icon: <Tv size={18} />, title: "Media Patterns", desc: "Reference architecture patterns", page: 'media_reference_patterns' as PageId },
                    ].map((item, i) => (
                      <button key={i} onClick={() => { setPage(item.page); setOpenMenu(null); }}
                        className="flex items-start gap-3 p-3 hover:bg-brand-light rounded-xl transition-colors text-left w-full">
                        <div className="text-brand-primary mt-0.5">{item.icon}</div>
                        <div>
                          <p className="font-bold text-sm">{item.title}</p>
                          <p className="text-xs text-gray-500 font-normal">{item.desc}</p>
                        </div>
                      </button>
                    ))}
                  </div>
                  <div>
                    <p className="text-[11px] font-bold text-gray-400 uppercase tracking-widest mb-3 px-3">Explore</p>
                    {[
                      { icon: <Target size={18} />, title: "Marketing Use Cases", desc: "Real-world campaign workflows", page: 'marketing_use_cases' as PageId },
                      { icon: <ShieldCheck size={18} />, title: "Trust Center", desc: "Security, compliance, SLAs", page: 'trust' as PageId },
                      { icon: <HelpCircle size={18} />, title: "Support & FAQs", desc: "Get help and answers fast", page: 'resources' as PageId },
                    ].map((item, i) => (
                      <button key={i} onClick={() => { setPage(item.page); setOpenMenu(null); }}
                        className="flex items-start gap-3 p-3 hover:bg-brand-light rounded-xl transition-colors text-left w-full">
                        <div className="text-brand-primary mt-0.5">{item.icon}</div>
                        <div>
                          <p className="font-bold text-sm">{item.title}</p>
                          <p className="text-xs text-gray-500 font-normal">{item.desc}</p>
                        </div>
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            </MegaMenuPanel>
          </div>

          <button onClick={() => setPage('company')} className={`py-2 hover:text-brand-primary transition-colors ${currentPage === 'company' ? 'text-brand-primary' : ''}`}>Company</button>
        </div>
      </div>

      <div className="flex items-center gap-4">
        <a href={EXTERNAL_URLS.login} target="_blank" rel="noopener noreferrer" className="hidden sm:block px-6 py-2.5 text-[14px] font-bold text-gray-800 hover:text-brand-primary transition-colors">
          Log In
        </a>
        <a href={EXTERNAL_URLS.demo} target="_blank" rel="noopener noreferrer" className="hidden sm:block px-6 py-2.5 text-[14px] font-bold bg-brand-primary text-black rounded-lg hover:bg-cyan-400 transition-all" style={{ boxShadow: SHADOW.shadow8 }}>
          Book Demo
        </a>
        {/* Mobile hamburger */}
        <button onClick={() => setMobileOpen(!mobileOpen)} className="xl:hidden p-2.5 hover:bg-gray-100 rounded-full transition-colors" aria-label="Toggle menu">
          {mobileOpen ? <X size={24} /> : <Menu size={24} />}
        </button>
      </div>
    </nav>

    {/* Mobile nav drawer */}
    <AnimatePresence>
      {mobileOpen && (
        <motion.div
          initial={{ opacity: 0, y: -8 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -8 }}
          transition={{ duration: MOTION.durationFast }}
          className="fixed inset-0 top-16 z-40 bg-white overflow-y-auto"
        >
          <div className="px-6 py-6 space-y-1">
            {/* Products section */}
            <div>
              <button onClick={() => setMobileSection(mobileSection === 'products' ? null : 'products')}
                className="flex items-center justify-between w-full py-3 text-lg font-bold text-gray-800">
                Products <ChevronDown size={16} className={`transition-transform ${mobileSection === 'products' ? 'rotate-180' : ''}`} />
              </button>
              {mobileSection === 'products' && (
                <div className="pl-4 pb-3 space-y-1">
                  <button onClick={() => mobilNav('products')} className="block w-full text-left py-2 text-sm text-gray-600 hover:text-brand-primary">Odoo on Cloud</button>
                  <button onClick={() => mobilNav('products')} className="block w-full text-left py-2 text-sm text-gray-600 hover:text-brand-primary">Pulser</button>
                  <button onClick={() => mobilNav('products')} className="block w-full text-left py-2 text-sm text-gray-600 hover:text-brand-primary">Analytics</button>
                  <button onClick={() => mobilNav('products')} className="block w-full text-left py-2 text-sm text-gray-600 hover:text-brand-primary">Cloud Operations</button>
                  <a href="https://prismalab.insightpulseai.com" target="_blank" rel="noopener noreferrer" className="block w-full text-left py-2 text-sm text-gray-600 hover:text-brand-primary">PrismaLab</a>
                </div>
              )}
            </div>
            {/* Solutions section */}
            <div>
              <button onClick={() => setMobileSection(mobileSection === 'solutions' ? null : 'solutions')}
                className="flex items-center justify-between w-full py-3 text-lg font-bold text-gray-800">
                Solutions <ChevronDown size={16} className={`transition-transform ${mobileSection === 'solutions' ? 'rotate-180' : ''}`} />
              </button>
              {mobileSection === 'solutions' && (
                <div className="pl-4 pb-3 space-y-1">
                  <button onClick={() => mobilNav('solutions')} className="block w-full text-left py-2 text-sm text-gray-600 hover:text-brand-primary">Solutions Overview</button>
                  <button onClick={() => mobilNav('marketing')} className="block w-full text-left py-2 text-sm text-gray-600 hover:text-brand-primary">Marketing Operations</button>
                  <button onClick={() => mobilNav('media')} className="block w-full text-left py-2 text-sm text-gray-600 hover:text-brand-primary">Media & Entertainment</button>
                  <button onClick={() => mobilNav('retail')} className="block w-full text-left py-2 text-sm text-gray-600 hover:text-brand-primary">Retail Operations</button>
                  <button onClick={() => mobilNav('finance')} className="block w-full text-left py-2 text-sm text-gray-600 hover:text-brand-primary">Financial Operations</button>
                </div>
              )}
            </div>
            <button onClick={() => mobilNav('pricing')} className="block w-full text-left py-3 text-lg font-bold text-gray-800 hover:text-brand-primary">Pricing</button>
            {/* Resources section */}
            <div>
              <button onClick={() => setMobileSection(mobileSection === 'resources' ? null : 'resources')}
                className="flex items-center justify-between w-full py-3 text-lg font-bold text-gray-800">
                Resources <ChevronDown size={16} className={`transition-transform ${mobileSection === 'resources' ? 'rotate-180' : ''}`} />
              </button>
              {mobileSection === 'resources' && (
                <div className="pl-4 pb-3 space-y-1">
                  <button onClick={() => mobilNav('docs')} className="block w-full text-left py-2 text-sm text-gray-600 hover:text-brand-primary">Documentation</button>
                  <button onClick={() => mobilNav('resources')} className="block w-full text-left py-2 text-sm text-gray-600 hover:text-brand-primary">Resource Library</button>
                  <button onClick={() => mobilNav('marketing_use_cases')} className="block w-full text-left py-2 text-sm text-gray-600 hover:text-brand-primary">Marketing Use Cases</button>
                  <button onClick={() => mobilNav('trust')} className="block w-full text-left py-2 text-sm text-gray-600 hover:text-brand-primary">Trust Center</button>
                  <button onClick={() => mobilNav('media_reference_patterns')} className="block w-full text-left py-2 text-sm text-gray-600 hover:text-brand-primary">Media Patterns</button>
                </div>
              )}
            </div>
            {/* Company section */}
            <div>
              <button onClick={() => setMobileSection(mobileSection === 'company' ? null : 'company')}
                className="flex items-center justify-between w-full py-3 text-lg font-bold text-gray-800">
                Company <ChevronDown size={16} className={`transition-transform ${mobileSection === 'company' ? 'rotate-180' : ''}`} />
              </button>
              {mobileSection === 'company' && (
                <div className="pl-4 pb-3 space-y-1">
                  <button onClick={() => mobilNav('company')} className="block w-full text-left py-2 text-sm text-gray-600 hover:text-brand-primary">Overview</button>
                  <button onClick={() => mobilNav('careers')} className="block w-full text-left py-2 text-sm text-gray-600 hover:text-brand-primary">Careers</button>
                  <button onClick={() => mobilNav('newsroom')} className="block w-full text-left py-2 text-sm text-gray-600 hover:text-brand-primary">Newsroom</button>
                  <button onClick={() => mobilNav('contact')} className="block w-full text-left py-2 text-sm text-gray-600 hover:text-brand-primary">Contact</button>
                </div>
              )}
            </div>
            <div className="pt-6 border-t border-gray-100 space-y-3">
              <a href={EXTERNAL_URLS.login} target="_blank" rel="noopener noreferrer" className="block w-full text-center py-3 text-sm font-bold text-gray-800 border border-gray-200 rounded-lg hover:border-brand-primary hover:text-brand-primary transition-all">
                Log In
              </a>
              <a href={EXTERNAL_URLS.demo} target="_blank" rel="noopener noreferrer" className="block w-full text-center py-3 text-sm font-bold bg-brand-primary text-black rounded-lg hover:bg-cyan-400 transition-all">
                Book Demo
              </a>
            </div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
    </>
  );
};

const Footer = ({ setPage }: { setPage: (p: PageId) => void }) => (
  <footer className="bg-brand-dark text-white pt-24 pb-12 px-6 md:px-12">
    <div className="max-w-7xl mx-auto">
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-12 mb-16">
        <div className="col-span-2 lg:col-span-1">
          <div className="flex items-center gap-2 mb-8">
            <button onClick={() => setPage('home')} aria-label="Home">
              <img src="/logo.png" alt="InsightPulseAI" className="w-12 h-12 rounded-lg" />
            </button>
          </div>
          <p className="text-gray-400 text-sm leading-relaxed mb-8">
            Modern operations that put you in control. Run Odoo in the cloud with operational intelligence, analytics, and scalable workflows built for growth.
          </p>
          <div className="flex gap-4">
            <a href={EXTERNAL_URLS.github} target="_blank" rel="noopener noreferrer" className="w-10 h-10 rounded-full bg-white/5 flex items-center justify-center hover:bg-brand-primary hover:text-black transition-all" aria-label="GitHub">
              <Globe size={18} />
            </a>
            <a href={EXTERNAL_URLS.email} className="w-10 h-10 rounded-full bg-white/5 flex items-center justify-center hover:bg-brand-primary hover:text-black transition-all" aria-label="Email">
              <Mail size={18} />
            </a>
          </div>
        </div>

        <div>
          <h4 className="font-bold mb-6 text-sm uppercase tracking-widest text-brand-primary">Products</h4>
          <ul className="space-y-5 text-gray-400 text-sm">
            <li><button onClick={() => setPage('products')} className="hover:text-white transition-colors">Odoo on Cloud</button></li>
            <li><button onClick={() => setPage('products')} className="hover:text-white transition-colors">Pulser</button></li>
            <li><button onClick={() => setPage('products')} className="hover:text-white transition-colors">Analytics</button></li>
            <li><button onClick={() => setPage('products')} className="hover:text-white transition-colors">Cloud Operations</button></li>
            <li><a href="https://prismalab.insightpulseai.com" target="_blank" rel="noopener noreferrer" className="hover:text-white transition-colors">PrismaLab</a></li>
          </ul>
        </div>

        <div>
          <h4 className="font-bold mb-6 text-sm uppercase tracking-widest text-brand-primary">Solutions</h4>
          <ul className="space-y-5 text-gray-400 text-sm">
            <li><button onClick={() => setPage('solutions')} className="hover:text-white transition-colors">Solutions Overview</button></li>
            <li><button onClick={() => setPage('marketing')} className="hover:text-white transition-colors">Marketing Operations</button></li>
            <li><button onClick={() => setPage('media')} className="hover:text-white transition-colors">Media & Entertainment</button></li>
            <li><button onClick={() => setPage('retail')} className="hover:text-white transition-colors">Retail Operations</button></li>
            <li><button onClick={() => setPage('finance')} className="hover:text-white transition-colors">Financial Operations</button></li>
          </ul>
        </div>

        <div>
          <h4 className="font-bold mb-6 text-sm uppercase tracking-widest text-brand-primary">Resources</h4>
          <ul className="space-y-5 text-gray-400 text-sm">
            <li><button onClick={() => setPage('docs')} className="hover:text-white transition-colors">Docs</button></li>
            <li><button onClick={() => setPage('marketing_use_cases')} className="hover:text-white transition-colors">Marketing Use Cases</button></li>
            <li><button onClick={() => setPage('docs')} className="hover:text-white transition-colors">Architecture</button></li>
            <li><button onClick={() => setPage('resources')} className="hover:text-white transition-colors">Learning Center</button></li>
            <li><button onClick={() => setPage('resources')} className="hover:text-white transition-colors">Webinars</button></li>
            <li><button onClick={() => setPage('resources')} className="hover:text-white transition-colors">Support & FAQs</button></li>
          </ul>
        </div>

        <div>
          <h4 className="font-bold mb-6 text-sm uppercase tracking-widest text-brand-primary">Company</h4>
          <ul className="space-y-5 text-gray-400 text-sm">
            <li><button onClick={() => setPage('company')} className="hover:text-white transition-colors">Overview</button></li>
            <li><button onClick={() => setPage('careers')} className="hover:text-white transition-colors">Careers</button></li>
            <li><button onClick={() => setPage('newsroom')} className="hover:text-white transition-colors">Newsroom</button></li>
            <li><button onClick={() => setPage('contact')} className="hover:text-white transition-colors">Contact</button></li>
          </ul>
        </div>
      </div>

      <div className="pt-12 border-t border-white/10 flex flex-col md:flex-row justify-between items-center gap-6 text-xs text-gray-500">
        <div>
          <p>&copy; 2026 InsightPulseAI. All rights reserved.</p>
          <p className="mt-2 text-gray-600">Dataverse IT Consultancy &middot; La Fuerza Plaza, 2241 Chino Roces Ave, Makati City 1231, Philippines</p>
        </div>
        <div className="flex gap-8">
          <button onClick={() => setPage('trust')} className="hover:text-white transition-colors">Trust Center</button>
          <button onClick={() => setPage('privacy')} className="hover:text-white transition-colors">Privacy</button>
          <button onClick={() => setPage('terms')} className="hover:text-white transition-colors">Terms</button>
          <button onClick={() => setPage('contact')} className="hover:text-white transition-colors">Contact</button>
        </div>
      </div>
    </div>
  </footer>
);

const GlobalCTA = ({ setPage }: { setPage: (p: PageId) => void }) => (
  <section className="py-24 px-6 md:px-12">
    <div className="max-w-7xl mx-auto bg-brand-primary rounded-2xl p-8 md:p-16 text-center relative overflow-hidden" style={{ boxShadow: SHADOW.shadow28 }}>
      <div className="absolute inset-0 grid-pattern opacity-20"></div>
      <div className="relative z-10">
        <h2 className="text-4xl md:text-4xl font-bold text-black mb-8 tracking-tight">
          Ready to run Odoo in the cloud with intelligence built in?
        </h2>
        <p className="text-xl text-black/80 mb-12 max-w-3xl mx-auto font-medium">
          Move from fragmented tools and manual work to one connected operating model with InsightPulseAI.
        </p>
        <div className="flex flex-col sm:flex-row justify-center gap-4">
          <a href={EXTERNAL_URLS.demo} target="_blank" rel="noopener noreferrer" className="px-10 py-4 bg-black text-white font-bold rounded-lg hover:bg-gray-900 transition-all inline-block" style={{ boxShadow: SHADOW.shadow8 }}>
            Book Demo
          </a>
          <button onClick={() => setPage('contact')} className="px-10 py-4 bg-white text-black font-bold rounded-lg hover:bg-gray-100 transition-all" style={{ boxShadow: SHADOW.shadow8 }}>
            Contact Sales
          </button>
        </div>
      </div>
    </div>
  </section>
);

// --- Page Components ---

const HomePage = ({ setPage }: { setPage: (p: PageId) => void }) => (
  <motion.div {...PAGE_TRANSITION}>
    {/* Hero */}
    <section className="pt-40 pb-24 px-6 md:px-12 bg-brand-dark text-white relative overflow-hidden">
      <div className="absolute inset-0 z-0">
        <video autoPlay muted loop playsInline className="w-full h-full object-cover">
          <source src="/hero-home.mp4" type="video/mp4" />
        </video>
        <div className="absolute inset-0" style={{ background: 'linear-gradient(to right, rgba(10,15,28,0.92) 0%, rgba(10,15,28,0.75) 45%, rgba(10,15,28,0.3) 75%, rgba(10,15,28,0.1) 100%)' }}></div>
      </div>
      <div className="max-w-7xl mx-auto relative z-10">
        <motion.div
          initial={{ y: 12, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.1, duration: MOTION.durationGentle, ease: MOTION.curveDecelerateMin }}
        >
          <h1 className="text-6xl md:text-8xl font-bold leading-[1.05] mb-10 tracking-tight max-w-4xl">
            AI-native operations for marketing, media, retail, and financial services
          </h1>
          <p className="text-xl text-gray-400 leading-relaxed mb-12 max-w-3xl">
            InsightPulseAI combines Odoo on Cloud, Pulser, and modern data workflows to help teams unify operations, automate execution, and scale with stronger control.
          </p>
          <div className="flex flex-wrap gap-4">
            <a href={EXTERNAL_URLS.demo} target="_blank" rel="noopener noreferrer" className="px-10 py-5 bg-brand-primary text-black font-extrabold rounded-full hover:bg-cyan-400 transition-all inline-block">Book Demo</a>
            <button onClick={() => setPage('contact')} className="px-10 py-5 bg-white/10 text-white font-extrabold rounded-full border border-white/20 hover:bg-white/20 transition-all">Contact Sales</button>
          </div>
        </motion.div>
      </div>
    </section>

    {/* Trusted By — Continuous Marquee */}
    <section className="py-10 border-b border-gray-100 overflow-hidden">
      <div className="flex animate-marquee whitespace-nowrap opacity-30 grayscale hover:opacity-50 transition-opacity">
        {[...Array(2)].map((_, setIndex) => (
          <div key={setIndex} className="flex items-center gap-16 px-8 shrink-0">
            {["GlobalMedia", "RetailPulse", "FinFlow", "MarketLogic", "OpsScale", "DataBridge", "CloudOps", "InsightCore"].map((name, i) => (
              <span key={i} className="text-xl font-bold tracking-tighter uppercase shrink-0">{name}</span>
            ))}
          </div>
        ))}
      </div>
    </section>

    {/* Industry Focus */}
    <section className="py-24 px-6 md:px-12 max-w-7xl mx-auto">
      <div className="mb-16">
        <h2 className="text-3xl md:text-4xl font-bold mb-8 tracking-tight">Built for data-heavy, workflow-heavy industries</h2>
        <p className="text-gray-600 text-xl max-w-4xl leading-relaxed">
          InsightPulseAI is purpose-built for organizations that need more than a generic ERP. We help teams in marketing, media, retail, and finance unify workflows, automate repetitive execution, and turn fragmented business signals into action.
        </p>
      </div>
      <div className="grid md:grid-cols-2 gap-8">
        {[
          {
            id: 'marketing' as PageId,
            icon: <Target size={40} className="text-brand-primary" />,
            title: "Marketing",
            desc: "Unify customer and campaign data, improve segmentation, accelerate planning, measure performance more clearly, and optimize spend with better operational visibility."
          },
          {
            id: 'media' as PageId,
            icon: <Tv size={40} className="text-brand-primary" />,
            title: "Media & Entertainment",
            desc: "Support audience intelligence, customer growth, monetization, content operations, and player or fan engagement from one operating layer."
          },
          {
            id: 'retail' as PageId,
            icon: <ShoppingBag size={40} className="text-brand-primary" />,
            title: "Retail",
            desc: "Connect merchandising, inventory, customer experience, marketing growth, workforce productivity, and supply-chain resilience in one system."
          },
          {
            id: 'finance' as PageId,
            icon: <Landmark size={40} className="text-brand-primary" />,
            title: "Financial Services",
            desc: "Strengthen decisioning, controls, efficiency, and customer operations with AI-assisted workflows and better data visibility."
          }
        ].map((item, i) => (
          <button
            key={i}
            onClick={() => setPage(item.id)}
            className="group bg-brand-light p-8 rounded-2xl border border-gray-100 text-left hover:bg-brand-dark hover:text-white transition-all duration-[150ms]"
            style={{ boxShadow: SHADOW.shadow4 }}
            onMouseEnter={e => (e.currentTarget.style.boxShadow = SHADOW.shadow16)}
            onMouseLeave={e => (e.currentTarget.style.boxShadow = SHADOW.shadow4)}
          >
            <div className="mb-8 group-hover:scale-110 transition-transform duration-[150ms] origin-left">{item.icon}</div>
            <h3 className="text-3xl font-bold mb-6 tracking-tight">{item.title}</h3>
            <p className="text-gray-600 group-hover:text-gray-400 leading-relaxed text-lg mb-8">{item.desc}</p>
            <div className="flex items-center gap-2 font-bold group-hover:text-brand-primary transition-colors">
              Explore {item.title} <ArrowRight size={20} className="group-hover:translate-x-2 transition-transform" />
            </div>
          </button>
        ))}
      </div>
    </section>

    {/* Products */}
    <section className="py-24 px-6 md:px-12 bg-brand-dark text-white">
      <div className="max-w-7xl mx-auto">
        <div className="mb-16 text-center">
          <h2 className="text-3xl md:text-4xl font-bold mb-8 tracking-tight">One intelligent operating system</h2>
          <p className="text-gray-400 text-xl max-w-3xl mx-auto">Start with what you need. Scale with AI-assisted cloud operations.</p>
        </div>
        <div className="grid md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-6">
          {[
            { icon: <Cloud size={32} />, title: "Odoo on Cloud", desc: "Run ERP, CRM, sales, inventory, projects, HR, finance, and operations from one hosted platform." },
            { icon: <Cpu size={32} />, title: "Pulser", desc: "Operational intelligence that surfaces what matters, summarizes context, and accelerates action across workflows." },
            { icon: <ShieldCheck size={32} />, title: "Cloud Operations", desc: "Deploy, govern, monitor, and evolve Odoo with a more reliable cloud delivery model." },
            { icon: <BarChart size={32} />, title: "Analytics & Dashboards", desc: "Turn operational data into real-time executive and team-level visibility." },
            { icon: <BookOpen size={32} />, title: "PrismaLab", desc: "PRISMA-aligned systematic reviews and meta-analysis support for research teams.", href: "https://prismalab.insightpulseai.com" }
          ].map((p, i) => (
            <div key={i} className="bg-white/5 p-8 rounded-2xl border border-white/10 hover:bg-white/10 transition-all group">
              <div className="mb-8 text-brand-primary group-hover:scale-110 transition-transform duration-[150ms] origin-left">{p.icon}</div>
              <h3 className="text-xl font-bold mb-4">{p.title}</h3>
              <p className="text-gray-400 text-sm leading-relaxed mb-8">{p.desc}</p>
              {(p as any).href ? (
                <a href={(p as any).href} target="_blank" rel="noopener noreferrer" className="text-brand-primary font-bold text-sm flex items-center gap-2">
                  Visit PrismaLab <ChevronRight size={16} />
                </a>
              ) : (
                <button onClick={() => setPage('products')} className="text-brand-primary font-bold text-sm flex items-center gap-2">
                  Learn More <ChevronRight size={16} />
                </button>
              )}
            </div>
          ))}
        </div>
      </div>
    </section>

    {/* How It Works */}
    <section className="py-24 px-6 md:px-12 max-w-7xl mx-auto">
      <div className="mb-16">
        <h2 className="text-3xl md:text-4xl font-bold mb-8 tracking-tight">How InsightPulseAI modernizes operations</h2>
        <p className="text-gray-600 text-xl max-w-4xl leading-relaxed">
          Adopt the platform in three layers: establish the operational system of record, add operational intelligence where work slows down, and turn business activity into timely dashboards and decisions.
        </p>
      </div>
      <div className="grid md:grid-cols-3 gap-8">
        {[
          {
            icon: <Cloud size={40} className="text-brand-primary" />,
            title: "Run the core in Odoo on Cloud",
            desc: "Centralize finance, CRM, inventory, projects, approvals, and operational workflows in one hosted environment."
          },
          {
            icon: <Cpu size={40} className="text-brand-primary" />,
            title: "Add AI where work stalls",
            desc: "Use Pulser to guide users, summarize records, surface exceptions, and accelerate repetitive execution."
          },
          {
            icon: <BarChart3 size={40} className="text-brand-primary" />,
            title: "Measure and improve continuously",
            desc: "Turn activity into dashboards, management views, and operational reporting that support faster decisions."
          }
        ].map((card, i) => (
          <div key={i} className="p-10 rounded-2xl bg-brand-light border border-gray-100 transition-all group" {...fluentCardShadow}>
            <div className="mb-8 group-hover:scale-110 transition-transform duration-[150ms] origin-left">{card.icon}</div>
            <h3 className="text-xl font-bold mb-4">{card.title}</h3>
            <p className="text-gray-600 text-sm leading-relaxed">{card.desc}</p>
          </div>
        ))}
      </div>
    </section>

    {/* Use Cases */}
    <section className="py-24 px-6 md:px-12 max-w-7xl mx-auto">
      <div className="mb-16">
        <h2 className="text-4xl md:text-4xl font-bold mb-8 tracking-tight">Shared cross-industry pillars</h2>
        <p className="text-gray-600 text-lg">The reusable abstractions that sit underneath our vertical solutions.</p>
      </div>
      <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
        {[
          "Customer and account intelligence", "Workflow orchestration", "Campaign / content / execution operations",
          "Performance measurement and reporting", "Risk, controls, and exception handling", "Multi-entity visibility",
          "AI-assisted decision support"
        ].map((use, i) => (
          <div key={i} className="p-8 rounded-2xl bg-brand-light border border-gray-100 flex items-start gap-4">
            <CheckCircle2 className="text-brand-primary flex-shrink-0" size={24} />
            <span className="font-bold text-gray-800">{use}</span>
          </div>
        ))}
      </div>
    </section>

    {/* Works With Your Stack — Color Logo Marquee */}
    <section className="py-16 px-6 md:px-12 border-y border-gray-100 bg-gray-50/50 overflow-hidden">
      <div className="max-w-7xl mx-auto">
        <p className="text-center text-sm font-bold text-gray-400 uppercase tracking-widest mb-10">Works with your existing stack</p>
        <div className="flex animate-marquee whitespace-nowrap">
          {[...Array(3)].map((_, setIndex) => (
            <div key={setIndex} className="flex items-center gap-16 px-8 shrink-0">
              {[
                { name: "Microsoft Azure", src: "/logos/azure.svg" },
                { name: "GitHub", src: "/logos/github.svg" },
                { name: "Databricks", src: "/logos/databricks.svg" },
                { name: "Odoo", src: "/logos/odoo.svg" },
                { name: "Zoho Mail", src: "/logos/zoho.svg" },
                { name: "Slack", src: "/logos/slack.svg" },
                { name: "Power BI", src: "/logos/powerbi.svg" },
              ].map((logo, i) => (
                <img key={i} src={logo.src} alt={logo.name} title={logo.name} className="h-8 shrink-0" />
              ))}
            </div>
          ))}
        </div>
      </div>
    </section>

    {/* Customer Story Rail */}
    <section className="py-24 px-6 md:px-12 max-w-7xl mx-auto">
      <div className="mb-12">
        <h2 className="text-3xl md:text-4xl font-bold mb-6 tracking-tight">Real results from real operations</h2>
        <p className="text-gray-600 text-lg max-w-3xl">Teams using InsightPulseAI consolidate fragmented tools, reduce manual work, and gain operational visibility they didn't have before.</p>
      </div>
      <div className="grid lg:grid-cols-5 gap-8">
        {/* Featured story */}
        <div className="lg:col-span-3 bg-brand-light rounded-2xl p-10 border border-gray-100 relative overflow-hidden">
          <Quote size={48} className="text-brand-primary/20 absolute top-6 right-6" />
          <div className="relative z-10">
            <p className="text-lg text-gray-800 leading-relaxed mb-8 italic">
              "We went from four disconnected spreadsheets to one operational view. Our month-end close dropped from twelve days to five, and the finance team actually trusts the numbers now."
            </p>
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-full bg-brand-primary/20 flex items-center justify-center">
                <span className="text-brand-primary font-bold text-lg">MR</span>
              </div>
              <div>
                <p className="font-bold text-gray-900">Maria Reyes</p>
                <p className="text-sm text-gray-500">VP Finance, Regional Wholesale Distributor</p>
              </div>
            </div>
          </div>
        </div>
        {/* Metrics strip */}
        <div className="lg:col-span-2 grid grid-cols-2 gap-4">
          {[
            { metric: "58%", label: "Faster month-end close" },
            { metric: "4→1", label: "Consolidated tools" },
            { metric: "3x", label: "Report turnaround improvement" },
            { metric: "100%", label: "Team adoption in 6 weeks" },
          ].map((stat, i) => (
            <div key={i} className="bg-white rounded-2xl border border-gray-100 p-6 flex flex-col justify-center text-center transition-shadow"
              style={{ boxShadow: SHADOW.shadow4 }}
              onMouseEnter={e => (e.currentTarget.style.boxShadow = SHADOW.shadow8)}
              onMouseLeave={e => (e.currentTarget.style.boxShadow = SHADOW.shadow4)}>
              <p className="text-3xl font-bold text-brand-primary mb-2">{stat.metric}</p>
              <p className="text-xs font-medium text-gray-500">{stat.label}</p>
            </div>
          ))}
        </div>
      </div>
    </section>

    {/* Architecture */}
    <section className="py-24 px-6 md:px-12 bg-brand-dark text-white">
      <div className="max-w-7xl mx-auto">
        <div className="mb-16">
          <h2 className="text-3xl md:text-4xl font-bold mb-8 tracking-tight">A controlled architecture, not another layer of sprawl</h2>
          <p className="text-gray-400 text-xl max-w-4xl leading-relaxed">
            InsightPulseAI combines operational system of record, operational intelligence, analytics, and managed cloud operations into one coherent operating model.
          </p>
        </div>
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
          {[
            { icon: <Cloud size={32} />, title: "Odoo on Cloud", desc: "Business workflows and system of record" },
            { icon: <Cpu size={32} />, title: "Pulser", desc: "Operational intelligence, guided workflows, and safe handoff paths" },
            { icon: <BarChart3 size={32} />, title: "Analytics & Dashboards", desc: "Performance visibility and executive reporting" },
            { icon: <Settings size={32} />, title: "Cloud Operations", desc: "Deployment, reliability, upgrades, and governance" }
          ].map((block, i) => (
            <div key={i} className="bg-white/5 p-8 rounded-2xl border border-white/10">
              <div className="mb-6 text-brand-primary">{block.icon}</div>
              <h3 className="text-lg font-bold mb-3">{block.title}</h3>
              <p className="text-gray-400 text-sm leading-relaxed">{block.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>

    {/* Trust & Governance */}
    <section className="py-24 px-6 md:px-12 max-w-7xl mx-auto">
      <div className="mb-16">
        <h2 className="text-3xl md:text-4xl font-bold mb-8 tracking-tight">Trust, governance, and current product posture</h2>
      </div>
      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
        {[
          "Role-based access and workflow-aware permissions",
          "Approval and exception handling patterns",
          "Operational visibility across teams and entities",
          "Cloud reliability, backup discipline, and lifecycle support",
          "Current Pulser posture: internal beta, trusted users, read-only advisory"
        ].map((item, i) => (
          <div key={i} className="p-8 rounded-2xl bg-brand-light border border-gray-100 flex items-start gap-4">
            <ShieldCheck className="text-brand-primary flex-shrink-0" size={24} />
            <span className="font-bold text-gray-800">{item}</span>
          </div>
        ))}
      </div>
    </section>

    {/* FAQ */}
    <section className="py-24 px-6 md:px-12 bg-gray-50">
      <div className="max-w-7xl mx-auto">
        <div className="mb-16">
          <h2 className="text-3xl md:text-4xl font-bold mb-8 tracking-tight">Frequently asked questions</h2>
        </div>
        <div className="space-y-6">
          {[
            { q: "What is Odoo on Cloud?", a: "A hosted operating platform built around Odoo, modern cloud delivery, and operational support." },
            { q: "What is Pulser?", a: "An AI-assisted workflow layer that helps users understand, navigate, and accelerate work inside the platform." },
            { q: "Can the website assistant access my ERP?", a: "No. The landing-page assistant is public and documentation-grounded only." },
            { q: "Is Pulser generally available?", a: "Not yet. Current launch posture is internal beta for trusted users with read-only advisory behavior." },
            { q: "Which industries are the best fit?", a: "Marketing, media, retail, and financial operations are the clearest starting lanes in the current site structure." }
          ].map((faq, i) => (
            <div key={i} className="p-8 rounded-2xl bg-white border border-gray-100" style={{ boxShadow: SHADOW.shadow4 }}>
              <h3 className="text-lg font-bold mb-3 text-gray-900">{faq.q}</h3>
              <p className="text-gray-600 leading-relaxed">{faq.a}</p>
            </div>
          ))}
        </div>
      </div>
    </section>

    <GlobalCTA setPage={setPage} />
  </motion.div>
);

const ProductsPage = ({ setPage }: { setPage: (p: PageId) => void }) => (
  <motion.div {...PAGE_TRANSITION} className="pt-28 pb-24 px-6 md:px-12 max-w-7xl mx-auto">
    <div className="mb-24">
      <h1 className="text-3xl md:text-4xl font-bold mb-10 tracking-tight">The InsightPulseAI Platform</h1>
      <p className="text-xl text-gray-600 max-w-3xl leading-relaxed">
        Combine modular ERP, cloud delivery, operational intelligence, and automation to improve speed, accuracy, and control across the business.
      </p>
    </div>

    <div className="space-y-20">
      {[
        {
          title: "Odoo on Cloud",
          desc: "Run your entire business from one secure, hosted environment. Odoo on Cloud gives growing companies a flexible platform with anywhere access, centralized data, and faster rollout across teams.",
          features: ["Finance & Accounting", "CRM & Sales", "Inventory & Purchasing", "Project Management", "HR & Operations"],
          icon: <Cloud size={48} className="text-brand-primary" />,
          image: "/images/product-odoo-cloud.png"
        },
        {
          title: "Pulser",
          desc: "An AI-native intelligence layer that runs across workflows, records, and operational activity. Pulser surfaces what matters, summarizes context, detects exceptions, and accelerates action across the business.",
          features: ["Operational Guidance", "Context Summaries", "Exception Detection", "Workflow Acceleration", "AI Reporting"],
          icon: <Cpu size={48} className="text-brand-primary" />,
          image: "/images/product-copilot.png"
        },
        {
          title: "Cloud Operations",
          desc: "Deploy, govern, and evolve Odoo with a reliable cloud delivery model. We handle the technical complexity so you can focus on business outcomes.",
          features: ["Automated Backups", "Security Monitoring", "Performance Optimization", "Governance Controls", "Scalable Infrastructure"],
          icon: <ShieldCheck size={48} className="text-brand-primary" />,
          image: "/images/product-cloud-ops.png"
        },
        {
          title: "Analytics & Dashboards",
          desc: "Turn operational data into real-time executive and team-level visibility. Get a clear view of performance, exceptions, and business health.",
          features: ["Real-time KPIs", "Custom Dashboards", "Drill-down Reporting", "AI-assisted Insights", "Cross-functional Views"],
          icon: <BarChart size={48} className="text-brand-primary" />,
          image: "/images/product-analytics.png"
        },
        {
          title: "PrismaLab",
          desc: "PRISMA-aligned systematic review and meta-analysis support for academic, clinical, and advisory teams. PrismaLab helps researchers deliver rigorous evidence synthesis with structured methodology and publication-ready clarity.",
          features: ["Systematic Reviews", "Meta-Analysis", "Scoping & Rapid Reviews", "Research Writing Support", "PRISMA 2020 Compliance"],
          icon: <BookOpen size={48} className="text-brand-primary" />,
          image: "/images/product-analytics.png"
        }
      ].map((p, i) => (
        <div key={i} className={`grid lg:grid-cols-2 gap-16 items-center ${i % 2 === 1 ? 'lg:flex-row-reverse' : ''}`}>
          <div className={i % 2 === 1 ? 'lg:order-2' : ''}>
            <div className="mb-8">{p.icon}</div>
            <h2 className="text-4xl font-bold mb-8 tracking-tight">{p.title}</h2>
            <p className="text-gray-600 text-lg leading-relaxed mb-10">{p.desc}</p>
            <div className="grid sm:grid-cols-2 gap-4">
              {p.features.map((f, j) => (
                <div key={j} className="flex items-center gap-3 text-gray-800 font-bold">
                  <div className="w-1.5 h-1.5 bg-brand-primary rounded-full"></div>
                  {f}
                </div>
              ))}
            </div>
          </div>
          <div className={i % 2 === 1 ? 'lg:order-1' : ''}>
            <div className="rounded-lg overflow-hidden border border-gray-200" style={{ boxShadow: SHADOW.shadow8 }}>
              <img src={p.image} alt={p.title} className="w-full aspect-[16/9] object-cover block" />
            </div>
          </div>
        </div>
      ))}
    </div>
  </motion.div>
);

const SolutionsPage = ({ setPage }: { setPage: (p: PageId) => void }) => (
  <motion.div {...PAGE_TRANSITION}>
    <section className="pt-28 pb-24 px-6 md:px-12 max-w-7xl mx-auto">
      <div className="mb-24">
        <span className="text-brand-primary font-bold uppercase tracking-widest text-sm mb-6 block">Solutions</span>
        <h1 className="text-3xl md:text-4xl font-bold mb-10 tracking-tight leading-[1.05]">
          Solutions built on one operational core
        </h1>
        <p className="text-xl text-gray-600 max-w-4xl leading-relaxed">
          Each InsightPulseAI solution starts from the same foundation: Odoo on Cloud, AI-assisted workflows, governed operations, and analytics that turn business activity into decisions. Choose the vertical entry point that fits your operating model today, then expand without rebuilding the stack.
        </p>
      </div>

      <div className="mb-24">
        <h2 className="text-3xl font-bold mb-12 tracking-tight">Choose your operating model</h2>
        <div className="grid md:grid-cols-2 gap-8">
          {[
            {
              id: 'marketing' as PageId,
              icon: <Target size={40} className="text-brand-primary" />,
              title: "Marketing Operations",
              desc: "Plan campaigns, manage approvals, coordinate assets, and track performance from one connected operating layer."
            },
            {
              id: 'media' as PageId,
              icon: <Tv size={40} className="text-brand-primary" />,
              title: "Media & Entertainment",
              desc: "Support audience growth, commercial workflows, content operations, and monetization visibility across teams."
            },
            {
              id: 'retail' as PageId,
              icon: <ShoppingBag size={40} className="text-brand-primary" />,
              title: "Retail Operations",
              desc: "Connect inventory, promotions, store execution, and supply-chain workflows with stronger operational visibility."
            },
            {
              id: 'finance' as PageId,
              icon: <Landmark size={40} className="text-brand-primary" />,
              title: "Financial Operations",
              desc: "Improve approvals, controls, reconciliations, and exception handling with AI-assisted workflow support."
            }
          ].map((item, i) => (
            <button
              key={i}
              onClick={() => setPage(item.id)}
              className="group bg-brand-light p-8 rounded-2xl border border-gray-100 text-left hover:bg-brand-dark hover:text-white transition-all duration-[150ms]"
              style={{ boxShadow: SHADOW.shadow4 }}
              onMouseEnter={e => (e.currentTarget.style.boxShadow = SHADOW.shadow16)}
              onMouseLeave={e => (e.currentTarget.style.boxShadow = SHADOW.shadow4)}
            >
              <div className="mb-8 group-hover:scale-110 transition-transform duration-[150ms] origin-left">{item.icon}</div>
              <h3 className="text-2xl font-bold mb-4 tracking-tight">{item.title}</h3>
              <p className="text-gray-600 group-hover:text-gray-400 leading-relaxed mb-8">{item.desc}</p>
              <div className="flex items-center gap-2 font-bold group-hover:text-brand-primary transition-colors">
                Explore <ArrowRight size={20} className="group-hover:translate-x-2 transition-transform" />
              </div>
            </button>
          ))}
        </div>
      </div>

      <div className="mb-24">
        <h2 className="text-3xl font-bold mb-12 tracking-tight">Shared platform capabilities</h2>
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {[
            "Odoo on Cloud deployment and lifecycle management",
            "AI-assisted guidance through Pulser",
            "Dashboards, reporting, and executive visibility",
            "Approvals, controls, and audit-ready workflows",
            "Multi-company and multi-entity operating support",
            "Integration and automation support"
          ].map((cap, i) => (
            <div key={i} className="p-8 rounded-2xl bg-brand-light border border-gray-100 flex items-start gap-4">
              <CheckCircle2 className="text-brand-primary flex-shrink-0" size={24} />
              <span className="font-bold text-gray-800">{cap}</span>
            </div>
          ))}
        </div>
      </div>

      <div className="flex flex-col sm:flex-row gap-4">
        <button onClick={() => setPage('products')} className="px-10 py-4 bg-brand-primary text-black font-bold rounded-lg hover:bg-cyan-400 transition-all" style={{ boxShadow: SHADOW.shadow8 }}>
          Explore Products
        </button>
        <a href={EXTERNAL_URLS.demo} target="_blank" rel="noopener noreferrer" className="px-10 py-4 bg-white text-black font-bold rounded-lg border border-gray-200 hover:border-brand-primary hover:text-brand-primary transition-all inline-block">
          Book Demo
        </a>
      </div>
    </section>
    <GlobalCTA setPage={setPage} />
  </motion.div>
);

const DocsPage = ({ setPage }: { setPage: (p: PageId) => void }) => (
  <motion.div {...PAGE_TRANSITION}>
    <section className="pt-28 pb-24 px-6 md:px-12 max-w-7xl mx-auto">
      <div className="mb-16">
        <span className="text-brand-primary font-bold uppercase tracking-widest text-sm mb-6 block">Docs</span>
        <h1 className="text-3xl md:text-4xl font-bold mb-10 tracking-tight leading-[1.05]">
          Documentation for operators, evaluators, and implementation teams
        </h1>
        <p className="text-xl text-gray-600 max-w-4xl leading-relaxed">
          Explore product documentation, architecture guidance, implementation patterns, and operational runbooks for InsightPulseAI, Odoo on Cloud, and Pulser.
        </p>
      </div>

      <div className="flex flex-wrap gap-3 mb-16">
        {["Product Docs", "Architecture", "Implementation Guides", "Security & Trust", "Prompt Packs", "Reference Patterns", "FAQs"].map((chip, i) => (
          <span key={i} className="px-5 py-2.5 bg-brand-light text-gray-800 font-bold text-sm rounded-full border border-gray-100">
            {chip}
          </span>
        ))}
      </div>

      <div className="grid md:grid-cols-2 gap-8 mb-24">
        {[
          {
            icon: <Cloud size={32} className="text-brand-primary" />,
            title: "Odoo on Cloud Overview",
            desc: "What is included, how deployment works, and how teams scale from launch to enterprise operations.",
            page: 'products' as PageId
          },
          {
            icon: <Cpu size={32} className="text-brand-primary" />,
            title: "Pulser Guide",
            desc: "Where Pulser helps, what it can and cannot do, and how public advisory mode differs from authenticated product assistance.",
            page: 'products' as PageId
          },
          {
            icon: <Layers size={32} className="text-brand-primary" />,
            title: "Architecture Overview",
            desc: "How cloud delivery, workflow automation, operational intelligence, and analytics fit together in one system.",
            page: 'trust' as PageId
          },
          {
            icon: <BookOpen size={32} className="text-brand-primary" />,
            title: "Implementation Guide",
            desc: "How teams move from fragmented tools to a governed Odoo operating model.",
            page: 'contact' as PageId
          }
        ].map((card, i) => (
          <button key={i} onClick={() => setPage(card.page)} className="p-10 rounded-2xl bg-brand-light border border-gray-100 transition-all group text-left" {...fluentCardShadow}>
            <div className="mb-8 group-hover:scale-110 transition-transform duration-[150ms] origin-left">{card.icon}</div>
            <h3 className="text-xl font-bold mb-4">{card.title}</h3>
            <p className="text-gray-600 text-sm leading-relaxed mb-8">{card.desc}</p>
            <span className="text-black font-bold text-sm flex items-center gap-2 group-hover:text-brand-primary transition-colors">
              Read More <ArrowRight size={16} />
            </span>
          </button>
        ))}
      </div>

      <div className="p-8 rounded-2xl bg-gray-50 border border-gray-200 mb-24">
        <h3 className="text-lg font-bold mb-3">Public prompt packs vs authenticated assistants</h3>
        <p className="text-gray-600 text-sm leading-relaxed">
          These use cases are public educational resources. They show how AI can support marketing workflows, but they do not imply tenant data access or authenticated product actions from this page.
        </p>
      </div>
    </section>
    <GlobalCTA setPage={setPage} />
  </motion.div>
);

const TrustPage = ({ setPage }: { setPage: (p: PageId) => void }) => (
  <motion.div {...PAGE_TRANSITION}>
    <section className="pt-28 pb-24 px-6 md:px-12 max-w-7xl mx-auto">
      <div className="mb-24">
        <span className="text-brand-primary font-bold uppercase tracking-widest text-sm mb-6 block">Trust Center</span>
        <h1 className="text-3xl md:text-4xl font-bold mb-10 tracking-tight leading-[1.05]">
          Built for operational trust, with product readiness clearly stated
        </h1>
        <p className="text-xl text-gray-600 max-w-4xl leading-relaxed">
          InsightPulseAI is designed for teams that need governed workflows, clear operational boundaries, and role-aware assistance. Public product guidance and authenticated Pulser are separate surfaces, and current Pulser launch posture remains internal beta for trusted users.
        </p>
      </div>

      <div className="grid md:grid-cols-2 gap-8 mb-24">
        {[
          {
            icon: <Users size={32} className="text-brand-primary" />,
            title: "Role-aware access",
            desc: "Permissions and workflow roles help keep actions visible and controlled."
          },
          {
            icon: <ShieldCheck size={32} className="text-brand-primary" />,
            title: "Governed approvals",
            desc: "Approval and exception workflows support stronger operational control."
          },
          {
            icon: <Cloud size={32} className="text-brand-primary" />,
            title: "Read-only advisory launch posture",
            desc: "Current Pulser posture is internal beta, trusted users, and fail-closed write behavior by default."
          },
          {
            icon: <Lock size={32} className="text-brand-primary" />,
            title: "AI boundary clarity",
            desc: "Public assistants answer from approved public knowledge only; authenticated Pulser is a separate product surface."
          }
        ].map((pillar, i) => (
          <div key={i} className="p-10 rounded-2xl bg-brand-light border border-gray-100">
            <div className="mb-8">{pillar.icon}</div>
            <h3 className="text-xl font-bold mb-4">{pillar.title}</h3>
            <p className="text-gray-600 text-sm leading-relaxed">{pillar.desc}</p>
          </div>
        ))}
      </div>

      <div className="mb-24">
        <h2 className="text-3xl font-bold mb-12 tracking-tight">Current Pulser readiness</h2>
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {[
            "Foundation complete",
            "Azure wiring complete",
            "Marketplace readiness blocked",
            "Write actions remain gated",
            "Docs corpus and eval pack still expanding"
          ].map((item, i) => (
            <div key={i} className="p-6 rounded-xl bg-brand-light border border-gray-100 flex items-start gap-3">
              <CheckCircle2 className="text-brand-primary flex-shrink-0" size={20} />
              <span className="font-bold text-gray-800 text-sm">{item}</span>
            </div>
          ))}
        </div>
      </div>

      <div className="mb-24">
        <h2 className="text-3xl font-bold mb-12 tracking-tight">Common questions</h2>
        <div className="space-y-6">
          {[
            {
              q: "Can the landing-page assistant access my ERP?",
              a: "No. The public assistant does not access tenant or company data from this page."
            },
            {
              q: "Is Pulser generally available?",
              a: "Not yet. Current launch posture is internal beta / trusted users / read-only advisory."
            },
            {
              q: "Can Pulser execute write actions today?",
              a: "Write actions remain gated until evaluation, SLO, and readiness thresholds are completed."
            }
          ].map((faq, i) => (
            <div key={i} className="p-8 rounded-2xl bg-white border border-gray-100" style={{ boxShadow: SHADOW.shadow4 }}>
              <h3 className="text-lg font-bold mb-3 text-gray-900">{faq.q}</h3>
              <p className="text-gray-600 leading-relaxed">{faq.a}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
    <GlobalCTA setPage={setPage} />
  </motion.div>
);

const ContactPage = ({ setPage }: { setPage: (p: PageId) => void }) => (
  <motion.div {...PAGE_TRANSITION}>
    <section className="pt-28 pb-24 px-6 md:px-12 max-w-7xl mx-auto">
      <div className="mb-24">
        <span className="text-brand-primary font-bold uppercase tracking-widest text-sm mb-6 block">Contact</span>
        <h1 className="text-3xl md:text-4xl font-bold mb-10 tracking-tight leading-[1.05]">
          Talk to the team behind InsightPulseAI
        </h1>
        <p className="text-xl text-gray-600 max-w-4xl leading-relaxed">
          Whether you are evaluating Odoo on Cloud, planning an AI-assisted operating model, or looking for implementation support, we can help you map the right entry point.
        </p>
      </div>

      <div className="grid md:grid-cols-2 gap-8 mb-24">
        {[
          {
            icon: <PlayCircle size={32} className="text-brand-primary" />,
            title: "Book a Demo",
            desc: "See the platform in action across operations, analytics, and AI-assisted workflows.",
            href: EXTERNAL_URLS.demo
          },
          {
            icon: <MessageSquare size={32} className="text-brand-primary" />,
            title: "Talk to Sales",
            desc: "Get guidance on plans, scope, and rollout approach.",
            href: EXTERNAL_URLS.email
          },
          {
            icon: <Layers size={32} className="text-brand-primary" />,
            title: "Architecture Review",
            desc: "Discuss deployment model, integrations, governance, and operating fit.",
            href: EXTERNAL_URLS.demo
          },
          {
            icon: <HelpCircle size={32} className="text-brand-primary" />,
            title: "Support & Questions",
            desc: "Get answers on implementation, onboarding, or product boundaries.",
            href: EXTERNAL_URLS.email
          }
        ].map((card, i) => (
          <a key={i} href={card.href} target="_blank" rel="noopener noreferrer" className="p-10 rounded-2xl bg-brand-light border border-gray-100 transition-all group block" {...fluentCardShadow}>
            <div className="mb-8 group-hover:scale-110 transition-transform duration-[150ms] origin-left">{card.icon}</div>
            <h3 className="text-xl font-bold mb-4">{card.title}</h3>
            <p className="text-gray-600 text-sm leading-relaxed mb-8">{card.desc}</p>
            <span className="text-black font-bold text-sm flex items-center gap-2 group-hover:text-brand-primary transition-colors">
              Get in Touch <ArrowRight size={16} />
            </span>
          </a>
        ))}
      </div>

      <div className="p-10 rounded-2xl bg-gray-50 border border-gray-100 mb-24">
        <h3 className="text-lg font-bold mb-6">Office</h3>
        <div className="grid md:grid-cols-2 gap-8">
          <div className="flex items-start gap-4">
            <MapPin size={20} className="text-brand-primary mt-1 shrink-0" />
            <div>
              <p className="font-semibold text-sm mb-1">Dataverse IT Consultancy</p>
              <p className="text-sm text-gray-600 leading-relaxed">La Fuerza Plaza, 2241 Chino Roces Ave<br />Makati City, Metro Manila 1231<br />Philippines</p>
            </div>
          </div>
          <div className="flex items-start gap-4">
            <Mail size={20} className="text-brand-primary mt-1 shrink-0" />
            <div>
              <p className="text-sm text-gray-600 mb-2"><a href="mailto:business@insightpulseai.com" className="hover:text-brand-primary transition-colors">business@insightpulseai.com</a></p>
              <p className="text-sm text-gray-600"><a href="mailto:admin@insightpulseai.com" className="hover:text-brand-primary transition-colors">admin@insightpulseai.com</a></p>
            </div>
          </div>
        </div>
      </div>
    </section>
    <GlobalCTA setPage={setPage} />
  </motion.div>
);

const MarketingPage = ({ setPage }: { setPage: (p: PageId) => void }) => (
  <motion.div {...PAGE_TRANSITION}>
    <section className="pt-28 pb-24 px-6 md:px-12 bg-brand-dark text-white">
      <div className="max-w-7xl mx-auto grid lg:grid-cols-2 gap-16 items-center">
        <div>
          <span className="text-brand-primary font-bold uppercase tracking-widest text-sm mb-6 block">Solutions / Marketing</span>
          <h1 className="text-3xl md:text-4xl font-bold mb-8 tracking-tight leading-[1.1]">
            Marketing operations that connect planning, execution, and insight
          </h1>
          <p className="text-xl text-gray-400 leading-relaxed mb-12">
            Run campaign workflows, content operations, approvals, reporting, budgets, and performance visibility from one AI-assisted operating system.
          </p>
          <button onClick={() => setPage('contact')} className="px-8 py-4 bg-brand-primary text-black font-bold rounded-full hover:bg-cyan-400 transition-all">
            Book Demo
          </button>
        </div>
        <div className="rounded-lg overflow-hidden border border-white/10" style={{ boxShadow: SHADOW.shadow28 }}>
          <img src="/images/marketing-hero.png" alt="Marketing operations dashboard" className="w-full aspect-[16/9] object-cover block" />
        </div>
      </div>
    </section>

    <section className="py-24 px-6 md:px-12 max-w-7xl mx-auto">
      <div className="grid md:grid-cols-3 gap-8">
        {[
          { title: "Unified customer and campaign operations", desc: "Connect your customer data with campaign execution for a true 360-degree view." },
          { title: "AI-assisted planning and execution", desc: "Use Pulser to draft briefs, summarize results, and guide workflows." },
          { title: "Better measurement and visibility", desc: "Real-time dashboards that show exactly where your marketing spend is going." }
        ].map((v, i) => (
          <div key={i} className="p-10 rounded-2xl bg-brand-light border border-gray-100">
            <h3 className="text-xl font-bold mb-4">{v.title}</h3>
            <p className="text-gray-600 text-sm leading-relaxed">{v.desc}</p>
          </div>
        ))}
      </div>
    </section>

    <section className="py-24 px-6 md:px-12 max-w-7xl mx-auto border-t border-gray-100">
      <div className="grid lg:grid-cols-2 gap-16 items-center">
        <div>
          <h2 className="text-4xl font-bold mb-10 tracking-tight">From fragmented martech workflows to one operational command layer</h2>
          <p className="text-gray-600 text-lg leading-relaxed mb-8">
            InsightPulseAI translates unified data into business operations: campaign briefs, approvals, budgets, timelines, content delivery, asset workflows, KPI tracking, and executive reporting.
          </p>
          <div className="grid grid-cols-2 gap-4">
            {["Campaign Briefs", "Approvals", "Budgets", "Timelines", "Content Delivery", "Asset Workflows", "KPI Tracking", "Executive Reporting"].map((item, i) => (
              <div key={i} className="p-5 bg-white rounded-2xl border border-gray-100 font-bold text-gray-800 flex items-center gap-3" style={{ boxShadow: SHADOW.shadow4 }}>
                <div className="w-2 h-2 bg-brand-primary rounded-full"></div>
                {item}
              </div>
            ))}
          </div>
        </div>
        <div className="rounded-lg overflow-hidden border border-gray-200" style={{ boxShadow: SHADOW.shadow8 }}>
          <img src="/images/marketing-workflows.png" alt="Campaign workflow dashboard" className="w-full aspect-[16/9] object-cover block" />
        </div>
      </div>
    </section>
    <GlobalCTA setPage={setPage} />
  </motion.div>
);

const MediaPage = ({ setPage }: { setPage: (p: PageId) => void }) => (
  <motion.div {...PAGE_TRANSITION}>
    {/* Hero */}
    <section className="pt-28 pb-24 px-6 md:px-12 bg-brand-dark text-white">
      <div className="max-w-7xl mx-auto grid lg:grid-cols-2 gap-16 items-center">
        <div>
          <span className="text-brand-primary font-bold uppercase tracking-widest text-sm mb-6 block">Solutions / Media & Entertainment</span>
          <h1 className="text-3xl md:text-4xl font-bold mb-8 tracking-tight leading-[1.1]">
            Media intelligence and operations that grow audiences, improve yield, and accelerate content execution
          </h1>
          <p className="text-xl text-gray-400 leading-relaxed mb-12">
            InsightPulseAI helps media and entertainment teams unify audience, campaign, content, and monetization signals into one governed operating layer. Use lakehouse-driven intelligence to improve acquisition, engagement, retention, pricing, inventory planning, and downstream content workflows.
          </p>
          <div className="flex flex-col sm:flex-row gap-4">
            <a href={EXTERNAL_URLS.demo} target="_blank" rel="noopener noreferrer" className="px-8 py-4 bg-brand-primary text-black font-bold rounded-full hover:bg-cyan-400 transition-all inline-block text-center">
              Book Demo
            </a>
            <a href={EXTERNAL_URLS.demo} target="_blank" rel="noopener noreferrer" className="px-8 py-4 bg-white/10 text-white font-bold rounded-lg hover:bg-white/20 transition-all border border-white/10 backdrop-blur-sm inline-block text-center">
              Book Demo
            </a>
          </div>
        </div>
        <div className="rounded-lg overflow-hidden border border-white/10" style={{ boxShadow: SHADOW.shadow28 }}>
          <img src="/images/media-hero.png" alt="Media command center" className="w-full aspect-[16/9] object-cover block" />
        </div>
      </div>
    </section>

    {/* Use case proof strip */}
    <section className="py-8 px-6 md:px-12 border-b border-gray-100 bg-gray-50/50">
      <div className="max-w-7xl mx-auto">
        <p className="text-center text-[11px] font-bold text-gray-400 uppercase tracking-widest mb-5">Media intelligence use cases supported by the governed lakehouse</p>
        <div className="flex flex-wrap justify-center gap-2">
          {["Customer 360", "Campaign Metrics", "Cohort / LTV Analysis", "Sentiment Analysis", "Subscriber Metrics", "Site / App Metrics"].map((chip, i) => (
            <span key={i} className="px-4 py-1.5 bg-white border border-gray-200 rounded-full text-xs font-bold text-gray-600">
              {chip}
            </span>
          ))}
        </div>
      </div>
    </section>

    {/* Four intelligence cards with images */}
    <section className="py-24 px-6 md:px-12 max-w-7xl mx-auto">
      <div className="grid md:grid-cols-2 gap-8">
        {[
          {
            icon: <Users size={36} className="text-brand-primary" />,
            title: "Audience Growth & Retention",
            desc: "Use audience intelligence, churn signals, and Customer 360 patterns to identify who to engage, retain, and win back.",
            image: "/images/media-audience.png"
          },
          {
            icon: <Lightbulb size={36} className="text-brand-primary" />,
            title: "Content & Recommendation Intelligence",
            desc: "Connect affinity, engagement, and recommendation signals to content planning, packaging, and next-best-content decisions.",
            image: "/images/media-content.png"
          },
          {
            icon: <TrendingUp size={36} className="text-brand-primary" />,
            title: "Ad Yield & Inventory Intelligence",
            desc: "Forecast inventory, improve pricing decisions, and connect audience value to monetization outcomes.",
            image: "/images/media-monetization.png"
          },
          {
            icon: <Target size={36} className="text-brand-primary" />,
            title: "Campaign & Attribution Intelligence",
            desc: "Measure campaign impact across channels and use attribution and return-on-ad-spend analysis to optimize media and marketing decisions.",
            image: "/images/media-hero.png"
          }
        ].map((card, i) => (
          <div key={i} className="rounded-2xl bg-white border border-gray-100 overflow-hidden transition-all group" {...fluentCardShadow}>
            <div className="overflow-hidden">
              <img src={card.image} alt={card.title} className="w-full aspect-[16/9] object-cover block group-hover:scale-[1.02] transition-transform duration-[200ms]" />
            </div>
            <div className="p-8">
              <div className="flex items-center gap-3 mb-4">
                {card.icon}
                <h3 className="text-xl font-bold">{card.title}</h3>
              </div>
              <p className="text-gray-600 leading-relaxed">{card.desc}</p>
            </div>
          </div>
        ))}
      </div>
    </section>

    {/* Governed intelligence layer */}
    <section className="py-24 px-6 md:px-12 max-w-7xl mx-auto border-t border-gray-100">
      <div className="grid lg:grid-cols-2 gap-16 items-start">
        <div>
          <h2 className="text-3xl md:text-4xl font-bold mb-10 tracking-tight">From fragmented media signals to one governed intelligence and execution layer</h2>
          <p className="text-gray-600 text-lg leading-relaxed mb-6">
            Media organizations generate audience, engagement, campaign, subscription, advertising, and content data across both structured and unstructured systems. The lakehouse pattern brings those sources together so teams can move faster across quality of experience, churn reduction, recommendation, personalization, attribution, pricing, and inventory planning.
          </p>
          <p className="text-gray-600 text-lg leading-relaxed mb-10">
            InsightPulseAI uses that intelligence layer to power downstream operational execution in Odoo and downstream creative finishing in Pulser — so audience and monetization signals do not stop at dashboards, but become briefs, workflows, approvals, and publish-ready outputs.
          </p>
          <div className="grid grid-cols-2 gap-4">
            {["Quality of Experience", "Churn / Survivorship", "Next Best Offer", "Content Recommendations", "Yield & Pricing", "Inventory Forecasting"].map((item, i) => (
              <div key={i} className="p-5 bg-white rounded-2xl border border-gray-100 font-bold text-gray-800 flex items-center gap-3" style={{ boxShadow: SHADOW.shadow4 }}>
                <div className="w-2 h-2 bg-brand-primary rounded-full flex-shrink-0"></div>
                <span className="text-sm">{item}</span>
              </div>
            ))}
          </div>
        </div>
        <div className="space-y-6">
          {/* Architecture split */}
          {[
            { role: "Diva", verb: "Decide / Analyze / Route", desc: "Media intelligence shell over the governed lakehouse. Audience, campaign, monetization, and content intelligence.", color: "bg-brand-primary/10 border-brand-primary/20" },
            { role: "Studio", verb: "Create / Polish / Export", desc: "Creative finishing surface. Briefs, content packages, platform variants, brand-formatted outputs.", color: "bg-purple-50 border-purple-200" },
            { role: "Odoo", verb: "Execute / Govern / Track", desc: "Operational execution layer. Workflows, approvals, finance, asset lifecycle, fulfillment.", color: "bg-gray-50 border-gray-200" }
          ].map((layer, i) => (
            <div key={i} className={`p-6 rounded-xl border ${layer.color}`}>
              <div className="flex items-center gap-3 mb-2">
                <span className="font-bold text-lg">{layer.role}</span>
                <span className="text-xs font-bold text-gray-400 uppercase tracking-wider">{layer.verb}</span>
              </div>
              <p className="text-sm text-gray-600 leading-relaxed">{layer.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
    <GlobalCTA setPage={setPage} />
  </motion.div>
);

const RetailPage = ({ setPage }: { setPage: (p: PageId) => void }) => (
  <motion.div {...PAGE_TRANSITION}>
    <section className="pt-28 pb-24 px-6 md:px-12 bg-brand-dark text-white">
      <div className="max-w-7xl mx-auto grid lg:grid-cols-2 gap-16 items-center">
        <div>
          <span className="text-brand-primary font-bold uppercase tracking-widest text-sm mb-6 block">Solutions / Retail Operations</span>
          <h1 className="text-3xl md:text-4xl font-bold mb-8 tracking-tight leading-[1.1]">
            Retail intelligence and operations for real-time inventory, fulfillment, and personalization
          </h1>
          <p className="text-xl text-gray-400 leading-relaxed mb-12">
            InsightPulseAI helps retailers unify transaction, clickstream, customer, inventory, logistics, and merchandising signals into one governed operating layer. Use real-time intelligence to improve product availability, replenishment, forecasting, fulfillment, and customer experience across channels.
          </p>
          <button onClick={() => setPage('contact')} className="px-8 py-4 bg-brand-primary text-black font-bold rounded-full hover:bg-cyan-400 transition-all">
            Book Demo
          </button>
        </div>
        <div className="rounded-lg overflow-hidden border border-white/10" style={{ boxShadow: SHADOW.shadow28 }}>
          <img src="/images/retail-hero.png" alt="Retail intelligence dashboard with polygon boundary map" className="w-full aspect-[16/9] object-cover block" />
        </div>
      </div>
    </section>

    {/* Use-case proof strip */}
    <section className="py-12 px-6 md:px-12 bg-brand-light border-b border-gray-100">
      <div className="max-w-7xl mx-auto">
        <p className="text-sm font-bold text-gray-500 uppercase tracking-widest mb-6">Retail intelligence use cases supported by the governed lakehouse</p>
        <div className="flex flex-wrap gap-3">
          {["Perpetual Inventory", "Fresh Food Forecasting", "Propensity-to-Buy", "Next Best Action", "Customer 360", "Real-Time Applications"].map((chip, i) => (
            <span key={i} className="px-5 py-2 rounded-full bg-white border border-gray-200 text-sm font-semibold text-gray-700">{chip}</span>
          ))}
        </div>
      </div>
    </section>

    <section className="py-24 px-6 md:px-12 max-w-7xl mx-auto">
      <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
        {[
          { title: "Inventory & Availability Intelligence", desc: "Predict out-of-stocks, improve on-shelf availability, and maintain a more accurate real-time view of inventory across stores and channels." },
          { title: "Supply Chain & Fulfillment Intelligence", desc: "Bring supply chain, logistics, warehousing, and delivery signals together to support faster response and better operational decisions." },
          { title: "Omnichannel Customer Intelligence", desc: "Unify POS, clickstream, loyalty, and digital behavior to understand how customers browse, buy, and respond across channels." },
          { title: "Replenishment & Forecasting Intelligence", desc: "Use demand, seasonality, promotions, pricing, and operational signals to improve allocation, replenishment, and forecasting decisions." }
        ].map((v, i) => (
          <div key={i} className="p-8 rounded-2xl bg-white border border-gray-100 transition-all" {...fluentCardShadow}>
            <h3 className="text-lg font-bold mb-4">{v.title}</h3>
            <p className="text-gray-600 text-sm leading-relaxed">{v.desc}</p>
          </div>
        ))}
      </div>
    </section>

    <section className="py-24 px-6 md:px-12 max-w-7xl mx-auto border-t border-gray-100">
      <div className="grid lg:grid-cols-2 gap-16 items-center">
        <div>
          <h2 className="text-4xl font-bold mb-10 tracking-tight">From fragmented retail data to one governed intelligence and execution layer</h2>
          <p className="text-gray-600 text-lg leading-relaxed mb-6">
            Retail organizations generate data continuously across e-commerce, point of sale, clickstream, delivery, loyalty, logistics, and in-store operations. Real-time retail decisions require more than reporting — they require a governed data foundation that can ingest, refine, and operationalize those signals fast enough to affect today's outcomes, not tomorrow's.
          </p>
          <p className="text-gray-600 text-lg leading-relaxed mb-8">
            InsightPulseAI uses that intelligence layer to power downstream operational execution in Odoo and downstream creative or campaign activation where needed — so demand, availability, and customer signals become workflows, approvals, recommendations, and actions.
          </p>
          <div className="grid grid-cols-2 gap-4">
            {["Real-Time Supply Chain Data", "Inventory Allocation", "POS and Clickstream", "On-Shelf Availability", "Recommendation Engines", "Automated Replenishments"].map((item, i) => (
              <div key={i} className="p-6 bg-brand-light rounded-2xl font-bold text-gray-800 flex items-center gap-3">
                <div className="w-2 h-2 bg-brand-primary rounded-full"></div>
                {item}
              </div>
            ))}
          </div>
        </div>
        <div className="rounded-lg overflow-hidden border border-gray-200" style={{ boxShadow: SHADOW.shadow8 }}>
          <img src="/images/retail-inventory.png" alt="Inventory and supply chain dashboard" className="w-full aspect-[16/9] object-cover block" />
        </div>
      </div>
    </section>
    <GlobalCTA setPage={setPage} />
  </motion.div>
);

const FinancePage = ({ setPage }: { setPage: (p: PageId) => void }) => (
  <motion.div {...PAGE_TRANSITION}>
    <section className="pt-28 pb-24 px-6 md:px-12 bg-brand-dark text-white">
      <div className="max-w-7xl mx-auto grid lg:grid-cols-2 gap-16 items-center">
        <div>
          <span className="text-brand-primary font-bold uppercase tracking-widest text-sm mb-6 block">Solutions / Financial Operations</span>
          <h1 className="text-3xl md:text-4xl font-bold mb-8 tracking-tight leading-[1.1]">
            Financial intelligence and operations for growth, control, and efficiency
          </h1>
          <p className="text-xl text-gray-400 leading-relaxed mb-12">
            InsightPulseAI helps financial teams unify customer, risk, fraud, compliance, pricing, and operational signals into one governed operating layer. Use data intelligence to improve growth, protect the firm, and accelerate financial execution across regulated environments.
          </p>
          <button onClick={() => setPage('contact')} className="px-8 py-4 bg-brand-primary text-black font-bold rounded-full hover:bg-cyan-400 transition-all">
            Book Demo
          </button>
        </div>
        <div className="rounded-lg overflow-hidden border border-white/10" style={{ boxShadow: SHADOW.shadow28 }}>
          <img src="/images/finance-hero.png" alt="Financial intelligence dashboard" className="w-full object-contain block" />
        </div>
      </div>
    </section>

    {/* Use-case proof strip */}
    <section className="py-12 px-6 md:px-12 bg-brand-light border-b border-gray-100">
      <div className="max-w-7xl mx-auto">
        <p className="text-sm font-bold text-gray-500 uppercase tracking-widest mb-6">Financial intelligence use cases supported by the governed data platform</p>
        <div className="flex flex-wrap gap-3">
          {["Banking & Payments", "Capital Markets", "Insurance", "Fraud Prevention", "Regulatory Compliance", "Operational Efficiency"].map((chip, i) => (
            <span key={i} className="px-5 py-2 rounded-full bg-white border border-gray-200 text-sm font-semibold text-gray-700">{chip}</span>
          ))}
        </div>
      </div>
    </section>

    <section className="py-24 px-6 md:px-12 max-w-7xl mx-auto">
      <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
        {[
          { title: "Growth & Customer Intelligence", desc: "Support customer engagement, personalization, and revenue growth with better visibility into customer behavior and product outcomes." },
          { title: "Fraud, Risk & Protection Intelligence", desc: "Improve fraud detection, risk visibility, and control workflows with more unified signals and faster analysis." },
          { title: "Compliance & Governance Intelligence", desc: "Strengthen auditability, access control, and regulatory readiness with governed data, audit trails, and controlled environments." },
          { title: "Efficiency & Pricing Intelligence", desc: "Accelerate financial operations, model processing, and pricing or underwriting decisions with faster data and better decision support." }
        ].map((v, i) => (
          <div key={i} className="p-8 rounded-2xl bg-white border border-gray-100 transition-all" {...fluentCardShadow}>
            <h3 className="text-lg font-bold mb-4">{v.title}</h3>
            <p className="text-gray-600 text-sm leading-relaxed">{v.desc}</p>
          </div>
        ))}
      </div>
    </section>

    <section className="py-24 px-6 md:px-12 max-w-7xl mx-auto border-t border-gray-100">
      <div className="grid lg:grid-cols-2 gap-16 items-center">
        <div>
          <h2 className="text-4xl font-bold mb-10 tracking-tight">From fragmented financial data to one governed intelligence and execution layer</h2>
          <p className="text-gray-600 text-lg leading-relaxed mb-6">
            Financial institutions operate across customer, transaction, fraud, compliance, market, and operational data domains — all under high regulatory scrutiny. A governed data-intelligence platform brings these sources together so organizations can drive growth, protect the firm, and improve efficiency without fragmenting analytics, AI, and governance across disconnected systems.
          </p>
          <p className="text-gray-600 text-lg leading-relaxed mb-8">
            InsightPulseAI uses that intelligence layer to power downstream execution in Odoo and downstream specialist workflows where needed — so fraud signals, pricing insights, compliance findings, and customer engagement signals become tasks, approvals, workflows, and operational action.
          </p>
          <div className="grid grid-cols-2 gap-4">
            {["Customer Engagement & Personalization", "Fraud Detection", "Risk & Compliance", "Pricing & Underwriting", "Operational Efficiency", "Audit Trails & Governance"].map((item, i) => (
              <div key={i} className="p-6 bg-brand-light rounded-2xl font-bold text-gray-800 flex items-center gap-3">
                <div className="w-2 h-2 bg-brand-primary rounded-full"></div>
                {item}
              </div>
            ))}
          </div>
        </div>
        <div className="rounded-lg overflow-hidden border border-gray-200" style={{ boxShadow: SHADOW.shadow8 }}>
          <img src="/images/finance-controls.png" alt="Compliance and governance dashboard" className="w-full aspect-[16/9] object-cover block" />
        </div>
      </div>
    </section>
    <GlobalCTA setPage={setPage} />
  </motion.div>
);

const MediaReferencePatternsPage = ({ setPage }: { setPage: (p: PageId) => void }) => (
  <motion.div {...PAGE_TRANSITION}>
    <section className="pt-28 pb-24 px-6 md:px-12 max-w-7xl mx-auto">
      <div className="mb-16">
        <span className="text-brand-primary font-bold uppercase tracking-widest text-sm mb-6 block">Docs / Media Reference Patterns</span>
        <h1 className="text-3xl md:text-4xl font-bold mb-10 tracking-tight leading-[1.05]">
          Reference patterns for media delivery, workflow orchestration, and streaming infrastructure
        </h1>
        <p className="text-xl text-gray-600 max-w-4xl leading-relaxed">
          These reference patterns help implementation teams understand cloud media architecture options, deployment patterns, and adjacent workflow components. They are technical references, not the primary product narrative for InsightPulseAI Media &amp; Entertainment.
        </p>
      </div>

      <div className="p-8 rounded-2xl bg-brand-light border border-gray-100 mb-16">
        <h2 className="text-xl font-bold mb-4">What this page is for</h2>
        <p className="text-gray-600 leading-relaxed">
          Use this page to review infrastructure-oriented examples for media workflows, content delivery, storage, and stream processing. These references are useful during architecture evaluation and implementation planning.
        </p>
      </div>

      <div className="mb-16">
        <h2 className="text-2xl font-bold mb-10 tracking-tight">Relevant Microsoft reference categories</h2>
        <div className="grid md:grid-cols-2 gap-8">
          {[
            {
              icon: <Database size={28} className="text-brand-primary" />,
              title: "Media infrastructure templates",
              desc: "Resource deployment patterns such as media account provisioning and storage-linked media infrastructure."
            },
            {
              icon: <PlayCircle size={28} className="text-brand-primary" />,
              title: "Video portal patterns",
              desc: "Older examples such as Orchard CMS video portal deployment are useful as implementation references, but not as modern product benchmarks."
            },
            {
              icon: <Zap size={28} className="text-brand-primary" />,
              title: "Real-time processing",
              desc: "Streaming and event-processing patterns such as Azure Stream Analytics can still inform real-time media telemetry and workflow automation."
            },
            {
              icon: <Box size={28} className="text-brand-primary" />,
              title: "Storage and archive patterns",
              desc: "Long-term storage, archive, and attachment-retention patterns are relevant to media libraries and governed asset operations."
            }
          ].map((card, i) => (
            <div key={i} className="p-10 rounded-2xl bg-white border border-gray-200 transition-all group" {...fluentCardShadow}>
              <div className="mb-6 group-hover:scale-110 transition-transform duration-[150ms] origin-left">{card.icon}</div>
              <h3 className="text-lg font-bold mb-3">{card.title}</h3>
              <p className="text-gray-600 text-sm leading-relaxed">{card.desc}</p>
            </div>
          ))}
        </div>
      </div>

      <div className="p-8 rounded-2xl bg-amber-50 border border-amber-200 mb-16">
        <h2 className="text-xl font-bold mb-4 text-amber-900">Use with caution</h2>
        <p className="text-amber-800 leading-relaxed">
          Some Microsoft Learn media samples reflect older Azure Media Services-era patterns. Azure Media Services was retired on June 30, 2024. Treat these as technical reference material only, and validate current service status and replacement architecture before adopting them directly.
        </p>
      </div>

      <div className="mb-16">
        <h2 className="text-2xl font-bold mb-6 tracking-tight">What belongs on the public Media &amp; Entertainment solution page instead</h2>
        <p className="text-gray-600 mb-8 leading-relaxed">
          The public-facing Media &amp; Entertainment solution narrative should remain operations-first, not infrastructure-first. The right public abstractions are:
        </p>
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {[
            "Audience operations",
            "Content operations",
            "Monetization workflows",
            "Partner and rights coordination",
            "Campaign and release workflows",
            "Executive visibility and reporting"
          ].map((item, i) => (
            <div key={i} className="flex items-center gap-3 p-4 bg-brand-light rounded-lg border border-gray-100">
              <CheckCircle2 size={18} className="text-brand-primary shrink-0" />
              <span className="font-semibold text-sm">{item}</span>
            </div>
          ))}
        </div>
      </div>
    </section>
    <GlobalCTA setPage={setPage} />
  </motion.div>
);

const MarketingUseCasesPage = ({ setPage }: { setPage: (p: PageId) => void }) => {
  const sections = [
    {
      title: "Campaign planning & strategy",
      icon: <Target size={28} className="text-brand-primary" />,
      cards: [
        "Visualize campaign timeline",
        "Brainstorm campaign ideas",
        "Draft a creative brief",
        "Build a messaging framework",
        "Build a customer journey map"
      ]
    },
    {
      title: "Competitive and market research",
      icon: <Search size={28} className="text-brand-primary" />,
      cards: [
        "Competitive content analysis",
        "Research emerging trends in buyer behavior",
        "Research regional campaign benchmarks",
        "Research industry event competitor presence",
        "Research AI tools for marketers"
      ]
    },
    {
      title: "Content & creative development",
      icon: <PenTool size={28} className="text-brand-primary" />,
      cards: [
        "Draft a product launch email",
        "Generate ad copy variations",
        "Create a social post series",
        "Create a customer spotlight post",
        "Create an explainer video script"
      ]
    },
    {
      title: "Data analysis & optimization",
      icon: <BarChart3 size={28} className="text-brand-primary" />,
      cards: [
        "Identify top-performing marketing channels",
        "Uncover customer churn patterns",
        "Summarize survey results",
        "Forecast next quarter's lead volume",
        "Optimize campaign budget allocation"
      ]
    },
    {
      title: "Visual & brand communication",
      icon: <Palette size={28} className="text-brand-primary" />,
      cards: [
        "Develop a brand style guide outline",
        "Conceptualize visual storytelling",
        "Create visual campaign moodboard",
        "Evaluate brand consistency",
        "Refresh brand identity concepts"
      ]
    }
  ];

  return (
    <motion.div {...PAGE_TRANSITION}>
      <section className="pt-28 pb-24 px-6 md:px-12 max-w-7xl mx-auto">
        <div className="mb-16">
          <span className="text-brand-primary font-bold uppercase tracking-widest text-sm mb-6 block">Resources / Marketing Use Cases</span>
          <h1 className="text-3xl md:text-4xl font-bold mb-10 tracking-tight leading-[1.05]">
            Practical AI workflows for modern marketing teams
          </h1>
          <p className="text-xl text-gray-600 max-w-4xl leading-relaxed">
            Explore structured prompt patterns for campaign strategy, competitive research, content creation, analytics, and brand communication. This public resource surface is designed for marketers who need practical starting points, not vague inspiration.
          </p>
        </div>

        <div className="p-6 rounded-xl bg-cyan-50 border border-cyan-200 mb-16">
          <p className="text-sm text-cyan-800 leading-relaxed">
            <strong>Public educational resource.</strong> These use cases show how AI can support marketing workflows. They do not imply tenant data access or authenticated product actions from this page. For in-product assistance, sign in to your Odoo workspace.
          </p>
        </div>

        {sections.map((section, i) => (
          <div key={i} className="mb-20">
            <div className="flex items-center gap-4 mb-10">
              {section.icon}
              <h2 className="text-2xl font-bold tracking-tight">{section.title}</h2>
            </div>
            <div className="grid sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4">
              {section.cards.map((card, j) => (
                <div key={j} className="p-6 rounded-2xl bg-brand-light border border-gray-100 hover:border-brand-primary/30 transition-all group cursor-pointer" {...fluentCardShadow}>
                  <div className="flex items-start gap-3">
                    <Zap size={16} className="text-brand-primary mt-0.5 shrink-0" />
                    <p className="text-sm font-semibold text-gray-800 group-hover:text-brand-primary transition-colors leading-snug">{card}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </section>
      <GlobalCTA setPage={setPage} />
    </motion.div>
  );
};

const ResourcesPage = ({ setPage }: { setPage: (p: PageId) => void }) => (
  <motion.div {...PAGE_TRANSITION} className="pt-28 pb-24 px-6 md:px-12 max-w-7xl mx-auto">
    <div className="mb-16">
      <h1 className="text-3xl md:text-4xl font-bold mb-8 tracking-tight">Resource Hub</h1>
      <p className="text-xl text-gray-600 max-w-3xl leading-relaxed">
        Your one place for guides, insights, case studies, implementation advice, and the latest thinking on Odoo, Pulser, and cloud operations.
      </p>
    </div>

    <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8 mb-24">
      {[
        { icon: <Target />, title: "Marketing Use Cases", desc: "Prompt packs and AI workflows for campaign strategy, market research, content creation, analysis, and brand communication.", link: "Explore Use Cases", page: 'marketing_use_cases' as PageId },
        { icon: <Newspaper />, title: "Blog", desc: "The latest ideas, lessons, and best practices for modern ERP and AI.", link: "Read the Blog", page: 'resources' as PageId },
        { icon: <BookOpen />, title: "Learning Center", desc: "Explore deeper guides on Odoo, automation, and implementation.", link: "Go to the Learning Center", page: 'docs' as PageId },
        { icon: <Users />, title: "Customer Stories", desc: "See how teams modernize operations with InsightPulseAI.", link: "Read Customer Stories", page: 'company' as PageId },
        { icon: <PlayCircle />, title: "Webinars", desc: "Practical sessions on ERP modernization and AI-assisted operations.", link: "Explore Webinars", page: 'resources' as PageId },
        { icon: <HelpCircle />, title: "Support and FAQs", desc: "Need implementation help or product guidance?", link: "Get Support", page: 'contact' as PageId },
        { icon: <Globe />, title: "Partners", desc: "Work with us as an implementation or technology partner.", link: "Explore Partnerships", page: 'contact' as PageId },
        { icon: <Tv />, title: "Media Reference Patterns", desc: "Technical reference patterns for media infrastructure, stream processing, storage, and legacy Azure media deployment examples.", link: "View Reference Patterns", page: 'media_reference_patterns' as PageId }
      ].map((card, i) => (
        <button key={i} onClick={() => setPage(card.page)} className="p-10 rounded-2xl bg-brand-light border border-gray-100 transition-all group text-left" {...fluentCardShadow}>
          <div className="mb-8 text-brand-primary group-hover:scale-110 transition-transform duration-[150ms] origin-left">{card.icon}</div>
          <h3 className="text-xl font-bold mb-4">{card.title}</h3>
          <p className="text-gray-600 text-sm leading-relaxed mb-8">{card.desc}</p>
          <span className="text-black font-bold text-sm flex items-center gap-2 group-hover:text-brand-primary transition-colors">
            {card.link} <ArrowRight size={16} />
          </span>
        </button>
      ))}
    </div>

    <div className="mb-24">
      <h2 className="text-3xl font-bold mb-12 tracking-tight">Featured Resources</h2>
      <div className="grid lg:grid-cols-2 gap-8">
        <button onClick={() => setPage('docs')} className="bg-brand-dark text-white rounded-2xl p-8 flex flex-col justify-between min-h-[400px] text-left">
          <div>
            <span className="text-brand-primary font-bold uppercase tracking-widest text-xs mb-6 block">Learning Center</span>
            <h3 className="text-3xl font-bold mb-6 tracking-tight">Odoo on Cloud: Architecture, modules, and implementation guide</h3>
            <p className="text-gray-400 text-lg leading-relaxed mb-8">A practical guide to choosing modules, structuring deployment, and scaling with confidence.</p>
          </div>
          <span className="flex items-center gap-2 font-bold text-brand-primary hover:text-white transition-colors">
            Explore the Guide <ArrowRight size={20} />
          </span>
        </button>
        <button onClick={() => setPage('company')} className="bg-brand-primary text-black rounded-2xl p-8 flex flex-col justify-between min-h-[400px] text-left">
          <div>
            <span className="text-black/60 font-bold uppercase tracking-widest text-xs mb-6 block">Customer Story</span>
            <h3 className="text-3xl font-bold mb-6 tracking-tight">How fast-growing teams use Odoo on Cloud to reduce friction</h3>
            <p className="text-black/70 text-lg leading-relaxed mb-8">See how a modern cloud operating model improves visibility, consistency, and execution.</p>
          </div>
          <span className="flex items-center gap-2 font-bold text-black hover:text-white transition-colors">
            Read the Story <ArrowRight size={20} />
          </span>
        </button>
      </div>
    </div>
  </motion.div>
);

const PricingPage = ({ setPage }: { setPage: (p: PageId) => void }) => (
  <motion.div {...PAGE_TRANSITION} className="pt-28 pb-24 px-6 md:px-12 max-w-7xl mx-auto">
    <div className="mb-16 text-center">
      <h1 className="text-3xl md:text-4xl font-bold mb-8 tracking-tight">Pricing and Plans</h1>
      <p className="text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
        Every deployment is shaped by your operating model, workflow scope, and support needs. We package InsightPulseAI around rollout complexity, governance requirements, and the level of cloud and AI assistance your team needs.
      </p>
    </div>

    <div className="grid lg:grid-cols-3 gap-8 mb-24">
      {[
        {
          title: "Launch",
          price: "Starting from",
          subtitle: "For teams starting with a focused cloud Odoo rollout.",
          features: ["Odoo on Cloud foundation", "Core workflow setup", "Standard environment configuration", "Baseline reporting", "Guided rollout support", "Upgrade-ready foundation"],
          cta: "Book Demo",
          highlight: false
        },
        {
          title: "Growth",
          price: "Custom",
          subtitle: "For teams expanding workflows, analytics, and AI-assisted operations.",
          features: ["Broader workflow rollout", "Pulser assistance", "Analytics & Dashboards", "Integration support", "Sandbox and rollout guidance", "Expanded operational support"],
          cta: "Book Demo",
          highlight: true
        },
        {
          title: "Enterprise",
          price: "Custom",
          subtitle: "For multi-entity, governed, high-complexity operating models.",
          features: ["Multi-company architecture", "Advanced governance and controls", "Priority support", "Deeper integrations", "AI-assisted operations rollout", "Tailored cloud operating model"],
          cta: "Contact Sales",
          highlight: false
        }
      ].map((tier, i) => (
        <div key={i} className={`p-12 rounded-2xl border ${tier.highlight ? 'bg-brand-dark text-white border-brand-dark' : 'bg-brand-light border-gray-100'}`}
          style={{ boxShadow: tier.highlight ? SHADOW.shadow28 : SHADOW.shadow4 }}>
          <h3 className="text-2xl font-bold mb-2">{tier.title}</h3>
          <div className={`text-4xl font-bold mb-3 ${tier.highlight ? 'text-brand-primary' : 'text-black'}`}>{tier.price}</div>
          {tier.subtitle && <p className={`text-sm mb-8 ${tier.highlight ? 'text-gray-400' : 'text-gray-500'}`}>{tier.subtitle}</p>}
          <ul className="space-y-4 mb-12">
            {tier.features.map((f, j) => (
              <li key={j} className="flex items-start gap-3 text-sm">
                <CheckCircle2 className={tier.highlight ? 'text-brand-primary' : 'text-gray-400'} size={18} />
                <span className={tier.highlight ? 'text-gray-300' : 'text-gray-600'}>{f}</span>
              </li>
            ))}
          </ul>
          {tier.cta === 'Book Demo' ? (
            <a href={EXTERNAL_URLS.demo} target="_blank" rel="noopener noreferrer" className={`block w-full py-5 rounded-lg font-bold text-center transition-all ${tier.highlight ? 'bg-brand-primary text-black hover:bg-cyan-400' : 'bg-black text-white hover:bg-gray-800'}`}>
              {tier.cta}
            </a>
          ) : (
            <button onClick={() => setPage('contact')} className={`w-full py-5 rounded-lg font-bold transition-all ${tier.highlight ? 'bg-brand-primary text-black hover:bg-cyan-400' : 'bg-black text-white hover:bg-gray-800'}`}>
              {tier.cta}
            </button>
          )}
        </div>
      ))}
    </div>

    <p className="text-center text-sm text-gray-400 mb-16 max-w-2xl mx-auto">
      Pricing depends on implementation scope, environment design, support level, integrations, and operating complexity. Final pricing is defined during solution scoping.
    </p>

    <div className="bg-brand-light rounded-2xl p-8 md:p-16 text-center">
      <h2 className="text-4xl font-bold mb-8 tracking-tight">Automation pays</h2>
      <p className="text-gray-600 text-xl max-w-3xl mx-auto leading-relaxed mb-12">
        Manual work, disconnected systems, and weak visibility create avoidable cost and risk. Odoo on Cloud with InsightPulseAI helps teams improve execution and scale with confidence.
      </p>
      <div className="flex flex-wrap justify-center gap-8">
        {["Workflow acceleration", "Better visibility", "Stronger controls", "Scalable model"].map((v, i) => (
          <div key={i} className="flex items-center gap-2 font-bold text-gray-800">
            <Zap className="text-brand-primary" size={20} />
            {v}
          </div>
        ))}
      </div>
    </div>
  </motion.div>
);

const CompanyPage = ({ setPage }: { setPage: (p: PageId) => void }) => (
  <motion.div {...PAGE_TRANSITION}>
    {/* 1. Hero */}
    <section className="pt-40 pb-24 px-6 md:px-12 bg-brand-dark text-white relative overflow-hidden">
      <div className="absolute inset-0 z-0">
        <video autoPlay muted loop playsInline className="w-full h-full object-cover opacity-30">
          <source src="/company-hero.mp4" type="video/mp4" />
        </video>
      </div>
      <div className="max-w-7xl mx-auto relative z-10">
        <span className="text-brand-primary font-bold uppercase tracking-widest text-sm mb-6 block">Company</span>
        <h1 className="text-5xl md:text-7xl font-bold mb-10 tracking-tight leading-[1.1] max-w-4xl">
          We build modern operating models for ambitious businesses
        </h1>
        <p className="text-xl text-gray-400 leading-relaxed mb-12 max-w-3xl">
          InsightPulseAI helps growing companies modernize operations with Odoo on Cloud, Pulser, analytics, and automation. We combine architecture, implementation, and operational support into one scalable operating model.
        </p>
        <div className="flex flex-wrap gap-4">
          <a href={EXTERNAL_URLS.demo} target="_blank" rel="noopener noreferrer" className="px-10 py-5 bg-brand-primary text-black font-extrabold rounded-full hover:bg-cyan-400 transition-all inline-block">Book Demo</a>
          <button onClick={() => setPage('contact')} className="px-10 py-5 bg-white/10 text-white font-extrabold rounded-full border border-white/20 hover:bg-white/20 transition-all">Contact Sales</button>
        </div>
      </div>
    </section>

    {/* 2. Why we exist */}
    <section className="py-24 px-6 md:px-12 max-w-7xl mx-auto">
      <h2 className="text-4xl font-bold mb-10 tracking-tight">Why InsightPulseAI exists</h2>
      <p className="text-gray-600 text-lg leading-relaxed max-w-4xl">
        InsightPulseAI was built around a simple problem: operations often move faster than systems can adapt. Teams outgrow fragmented tools, manual workflows, and ERP environments that are too rigid to evolve with the business. We built InsightPulseAI to close that gap with a more adaptive operating model powered by Odoo, cloud delivery, operational intelligence, and automation.
      </p>
    </section>

    {/* 3. What we do */}
    <section className="py-24 px-6 md:px-12 max-w-7xl mx-auto border-t border-gray-100">
      <h2 className="text-4xl font-bold mb-16 tracking-tight">What we do</h2>
      <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
        {[
          { icon: <Cloud size={32} className="text-brand-primary" />, title: "Odoo on Cloud", desc: "We design, deploy, and evolve cloud-based Odoo environments that give teams a stronger operational core." },
          { icon: <Cpu size={32} className="text-brand-primary" />, title: "Pulser", desc: "We add an intelligence layer where work slows down — helping teams surface context, detect exceptions, reduce friction, and accelerate execution." },
          { icon: <BarChart3 size={32} className="text-brand-primary" />, title: "Analytics & Visibility", desc: "We connect data, reporting, and operational insight so leaders can see what is happening and what should happen next." },
          { icon: <Settings size={32} className="text-brand-primary" />, title: "Cloud Operations", desc: "We support environments over time with practical operating discipline, not just one-time implementation." },
        ].map((item, i) => (
          <div key={i} className="p-8 rounded-2xl bg-brand-light border border-gray-100">
            <div className="mb-6">{item.icon}</div>
            <h3 className="text-lg font-bold mb-4">{item.title}</h3>
            <p className="text-gray-600 text-sm leading-relaxed">{item.desc}</p>
          </div>
        ))}
      </div>
    </section>

    {/* 4. What sets us apart */}
    <section className="py-24 px-6 md:px-12 max-w-7xl mx-auto border-t border-gray-100">
      <h2 className="text-4xl font-bold mb-8 tracking-tight">What sets us apart</h2>
      <p className="text-gray-600 text-lg leading-relaxed mb-16 max-w-3xl">
        We are not just an implementation shop and not just an automation vendor. InsightPulseAI combines four disciplines into one coherent operating model.
      </p>
      <div className="grid md:grid-cols-2 gap-8">
        {[
          { title: "Architecture-led", desc: "We design for scale, governance, and long-term system evolution." },
          { title: "Execution-focused", desc: "We care about operational outcomes, not just project completion." },
          { title: "Intelligence-led", desc: "We use Pulser and automation where they create measurable operational leverage." },
          { title: "Cloud-native", desc: "We modernize delivery, observability, and lifecycle management from the start." },
        ].map((item, i) => (
          <div key={i} className="flex items-start gap-6 p-8 rounded-2xl border border-gray-100">
            <div className="w-3 h-3 bg-brand-primary rounded-full mt-2 shrink-0"></div>
            <div>
              <h3 className="text-lg font-bold mb-2">{item.title}</h3>
              <p className="text-gray-600 text-sm leading-relaxed">{item.desc}</p>
            </div>
          </div>
        ))}
      </div>
    </section>

    {/* 5. How we work */}
    <section className="py-24 px-6 md:px-12 max-w-7xl mx-auto border-t border-gray-100">
      <h2 className="text-4xl font-bold mb-8 tracking-tight">How we work</h2>
      <p className="text-gray-600 text-lg leading-relaxed mb-16 max-w-3xl">
        We partner with teams that need more than disconnected tooling or one-off implementation. Our work is grounded in business workflows, operating realities, and the need to keep systems flexible as the organization grows.
      </p>
      <div className="grid md:grid-cols-3 gap-8">
        {[
          { step: "01", title: "Assess the operating model", desc: "Understand the current state, pain points, and growth trajectory." },
          { step: "02", title: "Design the cloud and workflow foundation", desc: "Architect the Odoo environment, integrations, and delivery model." },
          { step: "03", title: "Evolve with AI, analytics, and automation", desc: "Add Pulser, dashboards, and workflows that compound over time." },
        ].map((item, i) => (
          <div key={i} className="p-8 rounded-2xl bg-brand-dark text-white">
            <span className="text-brand-primary font-bold text-sm mb-4 block">{item.step}</span>
            <h3 className="text-lg font-bold mb-4">{item.title}</h3>
            <p className="text-gray-400 text-sm leading-relaxed">{item.desc}</p>
          </div>
        ))}
      </div>
    </section>

    {/* 6. Careers */}
    <section className="py-24 px-6 md:px-12 max-w-7xl mx-auto border-t border-gray-100">
      <div className="bg-brand-dark text-white rounded-2xl p-8 md:p-16 flex flex-col lg:flex-row items-center justify-between gap-12" style={{ boxShadow: SHADOW.shadow16 }}>
        <div className="max-w-xl">
          <h2 className="text-4xl font-bold mb-8 tracking-tight">Join us</h2>
          <p className="text-gray-400 text-lg leading-relaxed">
            We're building the future of intelligent business operations. If you care about systems, execution, and building tools that help teams work better, we'd love to hear from you.
          </p>
        </div>
        <button onClick={() => setPage('careers')} className="px-12 py-5 bg-brand-primary text-black font-bold rounded-lg hover:bg-cyan-400 transition-all whitespace-nowrap">
          See Careers
        </button>
      </div>
    </section>

    {/* 7. CTA */}
    <GlobalCTA setPage={setPage} />
  </motion.div>
);

// --- New pages: Privacy, Terms, Careers, Newsroom, Login ---

const PrivacyPage = ({ setPage }: { setPage: (p: PageId) => void }) => (
  <motion.div {...PAGE_TRANSITION}>
    <section className="pt-28 pb-24 px-6 md:px-12 max-w-7xl mx-auto">
      <div className="mb-16">
        <span className="text-brand-primary font-bold uppercase tracking-widest text-sm mb-6 block">Legal</span>
        <h1 className="text-3xl md:text-4xl font-bold mb-10 tracking-tight">Privacy Policy</h1>
        <p className="text-gray-600 text-lg leading-relaxed max-w-4xl mb-8">Last updated: March 2026</p>
      </div>
      <div className="prose max-w-4xl space-y-8">
        <div className="p-8 rounded-2xl bg-brand-light border border-gray-100">
          <h2 className="text-xl font-bold mb-4">Information we collect</h2>
          <p className="text-gray-600 leading-relaxed">We collect information you provide directly when you request a demo, create an account, or contact us. This includes name, email address, company name, and job title. We also collect usage data through standard web analytics to improve our services.</p>
        </div>
        <div className="p-8 rounded-2xl bg-brand-light border border-gray-100">
          <h2 className="text-xl font-bold mb-4">How we use your information</h2>
          <p className="text-gray-600 leading-relaxed">We use your information to provide and improve our services, communicate with you about your account or our products, and ensure platform security. We do not sell personal data to third parties.</p>
        </div>
        <div className="p-8 rounded-2xl bg-brand-light border border-gray-100">
          <h2 className="text-xl font-bold mb-4">Data security</h2>
          <p className="text-gray-600 leading-relaxed">All data is encrypted in transit and at rest. Our infrastructure runs on Microsoft Azure with enterprise-grade security controls, managed identities, and role-based access. We follow industry best practices for data protection.</p>
        </div>
        <div className="p-8 rounded-2xl bg-brand-light border border-gray-100">
          <h2 className="text-xl font-bold mb-4">Your rights</h2>
          <p className="text-gray-600 leading-relaxed">You may request access to, correction of, or deletion of your personal data at any time by contacting us. We will respond to all requests within 30 days.</p>
        </div>
        <div className="p-8 rounded-2xl bg-brand-light border border-gray-100">
          <h2 className="text-xl font-bold mb-4">Contact</h2>
          <p className="text-gray-600 leading-relaxed">For privacy-related questions, contact us at <a href={EXTERNAL_URLS.email} className="text-brand-primary hover:underline">business@insightpulseai.com</a> or visit our <button onClick={() => setPage('contact')} className="text-brand-primary hover:underline">contact page</button>.</p>
        </div>
      </div>
    </section>
  </motion.div>
);

const TermsPage = ({ setPage }: { setPage: (p: PageId) => void }) => (
  <motion.div {...PAGE_TRANSITION}>
    <section className="pt-28 pb-24 px-6 md:px-12 max-w-7xl mx-auto">
      <div className="mb-16">
        <span className="text-brand-primary font-bold uppercase tracking-widest text-sm mb-6 block">Legal</span>
        <h1 className="text-3xl md:text-4xl font-bold mb-10 tracking-tight">Terms of Service</h1>
        <p className="text-gray-600 text-lg leading-relaxed max-w-4xl mb-8">Last updated: March 2026</p>
      </div>
      <div className="prose max-w-4xl space-y-8">
        <div className="p-8 rounded-2xl bg-brand-light border border-gray-100">
          <h2 className="text-xl font-bold mb-4">Acceptance of terms</h2>
          <p className="text-gray-600 leading-relaxed">By accessing or using InsightPulseAI services, you agree to be bound by these Terms of Service. If you do not agree, you may not use our services.</p>
        </div>
        <div className="p-8 rounded-2xl bg-brand-light border border-gray-100">
          <h2 className="text-xl font-bold mb-4">Services</h2>
          <p className="text-gray-600 leading-relaxed">InsightPulseAI provides cloud-hosted Odoo ERP environments, Pulser operational intelligence, analytics dashboards, and cloud operations services. Service availability and features may vary by plan.</p>
        </div>
        <div className="p-8 rounded-2xl bg-brand-light border border-gray-100">
          <h2 className="text-xl font-bold mb-4">User responsibilities</h2>
          <p className="text-gray-600 leading-relaxed">You are responsible for maintaining the security of your account credentials, complying with applicable laws, and using our services in accordance with our acceptable use policy.</p>
        </div>
        <div className="p-8 rounded-2xl bg-brand-light border border-gray-100">
          <h2 className="text-xl font-bold mb-4">Limitation of liability</h2>
          <p className="text-gray-600 leading-relaxed">InsightPulseAI shall not be liable for indirect, incidental, or consequential damages arising from use of our services. Our total liability is limited to the fees paid in the preceding 12 months.</p>
        </div>
        <div className="p-8 rounded-2xl bg-brand-light border border-gray-100">
          <h2 className="text-xl font-bold mb-4">Contact</h2>
          <p className="text-gray-600 leading-relaxed">Questions about these terms? Contact us at <a href={EXTERNAL_URLS.email} className="text-brand-primary hover:underline">business@insightpulseai.com</a> or visit our <button onClick={() => setPage('contact')} className="text-brand-primary hover:underline">contact page</button>.</p>
        </div>
      </div>
    </section>
  </motion.div>
);

const CareersPage = ({ setPage }: { setPage: (p: PageId) => void }) => (
  <motion.div {...PAGE_TRANSITION}>
    <section className="pt-28 pb-24 px-6 md:px-12 bg-brand-dark text-white">
      <div className="max-w-7xl mx-auto">
        <span className="text-brand-primary font-bold uppercase tracking-widest text-sm mb-6 block">Careers</span>
        <h1 className="text-4xl md:text-5xl font-bold mb-10 tracking-tight max-w-3xl">Build the future of AI-assisted business operations</h1>
        <p className="text-xl text-gray-400 leading-relaxed max-w-3xl mb-12">
          We are a small, focused team building modern operating systems for ambitious businesses. If you care about systems, execution quality, and practical AI, we want to hear from you.
        </p>
        <a href={EXTERNAL_URLS.email} className="px-10 py-4 bg-brand-primary text-black font-bold rounded-lg hover:bg-cyan-400 transition-all inline-block">
          Send us your resume
        </a>
      </div>
    </section>
    <section className="py-24 px-6 md:px-12 max-w-7xl mx-auto">
      <h2 className="text-3xl font-bold mb-12 tracking-tight">What we value</h2>
      <div className="grid md:grid-cols-3 gap-8 mb-24">
        {[
          { title: "Execution over talk", desc: "We ship working systems, not slide decks. Every team member contributes to real product outcomes." },
          { title: "Systems thinking", desc: "We design for scale, governance, and long-term evolution. Architecture matters as much as features." },
          { title: "Honest engineering", desc: "We state what works, what does not, and what is still in progress. No inflated claims." },
        ].map((v, i) => (
          <div key={i} className="p-8 rounded-2xl bg-brand-light border border-gray-100">
            <h3 className="text-xl font-bold mb-4">{v.title}</h3>
            <p className="text-gray-600 leading-relaxed">{v.desc}</p>
          </div>
        ))}
      </div>
      <h2 className="text-3xl font-bold mb-12 tracking-tight">Areas we hire for</h2>
      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4 mb-24">
        {["Full-stack engineering", "Cloud & DevOps", "AI / ML engineering", "ERP implementation", "Product design", "Technical writing"].map((role, i) => (
          <div key={i} className="p-6 rounded-xl bg-brand-light border border-gray-100 flex items-center gap-3">
            <CheckCircle2 className="text-brand-primary shrink-0" size={20} />
            <span className="font-bold text-gray-800">{role}</span>
          </div>
        ))}
      </div>
      <div className="p-8 rounded-2xl bg-gray-50 border border-gray-200 text-center">
        <p className="text-gray-600 mb-4">Do not see a role that fits? We are always open to conversations with talented people.</p>
        <a href={EXTERNAL_URLS.email} className="text-brand-primary font-bold hover:underline">Reach out at business@insightpulseai.com</a>
      </div>
    </section>
    <GlobalCTA setPage={setPage} />
  </motion.div>
);

const NewsroomPage = ({ setPage }: { setPage: (p: PageId) => void }) => (
  <motion.div {...PAGE_TRANSITION}>
    <section className="pt-28 pb-24 px-6 md:px-12 max-w-7xl mx-auto">
      <div className="mb-16">
        <span className="text-brand-primary font-bold uppercase tracking-widest text-sm mb-6 block">Newsroom</span>
        <h1 className="text-3xl md:text-4xl font-bold mb-10 tracking-tight">Latest from InsightPulseAI</h1>
        <p className="text-xl text-gray-600 max-w-4xl leading-relaxed">
          Product updates, platform announcements, and operational insights from the team.
        </p>
      </div>
      <div className="grid md:grid-cols-2 gap-8 mb-24">
        {[
          { date: "March 2026", title: "InsightPulseAI launches Odoo on Cloud with Pulser", desc: "Our platform combines hosted Odoo ERP, AI-assisted workflows, and cloud operations into one governed operating model for marketing, media, retail, and financial services." },
          { date: "March 2026", title: "Media & Entertainment solution goes live", desc: "Audience intelligence, content operations, and monetization workflows now available as a dedicated vertical solution." },
          { date: "February 2026", title: "Azure infrastructure migration complete", desc: "Full migration from DigitalOcean to Azure Container Apps with Front Door edge, managed PostgreSQL, and enterprise identity readiness." },
          { date: "January 2026", title: "Retail Operations solution announced", desc: "Real-time inventory, supply chain intelligence, and omnichannel customer visibility for retail organizations." },
        ].map((post, i) => (
          <div key={i} className="p-8 rounded-2xl bg-brand-light border border-gray-100" {...fluentCardShadow}>
            <span className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-4 block">{post.date}</span>
            <h3 className="text-xl font-bold mb-4">{post.title}</h3>
            <p className="text-gray-600 leading-relaxed">{post.desc}</p>
          </div>
        ))}
      </div>
      <div className="text-center">
        <p className="text-gray-600 mb-4">For press inquiries, contact us at</p>
        <a href={EXTERNAL_URLS.email} className="text-brand-primary font-bold hover:underline">business@insightpulseai.com</a>
      </div>
    </section>
    <GlobalCTA setPage={setPage} />
  </motion.div>
);

const LoginPage = () => (
  <motion.div {...PAGE_TRANSITION}>
    <section className="pt-28 pb-24 px-6 md:px-12 max-w-7xl mx-auto text-center">
      <div className="max-w-md mx-auto">
        <h1 className="text-3xl font-bold mb-8 tracking-tight">Log In</h1>
        <p className="text-gray-600 mb-12">
          Access your InsightPulseAI workspace through our ERP portal.
        </p>
        <a href={EXTERNAL_URLS.login} target="_blank" rel="noopener noreferrer"
          className="px-10 py-4 bg-brand-primary text-black font-bold rounded-lg hover:bg-cyan-400 transition-all inline-flex items-center gap-2" style={{ boxShadow: SHADOW.shadow8 }}>
          Go to Odoo Login <ExternalLink size={16} />
        </a>
        <p className="text-sm text-gray-400 mt-8">
          You will be redirected to <code className="bg-gray-100 px-2 py-1 rounded text-xs">erp.insightpulseai.com</code>
        </p>
      </div>
    </section>
  </motion.div>
);

// --- Main App ---

export default function App() {
  const [currentPage, setCurrentPageState] = useState<PageId>(() => pageIdFromHash(window.location.hash));

  const setCurrentPage = useCallback((page: PageId) => {
    setCurrentPageState(page);
    const newHash = hashFromPageId(page);
    if (window.location.hash !== newHash && !(page === 'home' && !window.location.hash)) {
      window.history.pushState(null, '', newHash || window.location.pathname);
    }
  }, []);

  // Handle browser back/forward
  useEffect(() => {
    const onPopState = () => {
      setCurrentPageState(pageIdFromHash(window.location.hash));
    };
    window.addEventListener('popstate', onPopState);
    return () => window.removeEventListener('popstate', onPopState);
  }, []);

  useEffect(() => {
    window.scrollTo(0, 0);
  }, [currentPage]);

  const sp = setCurrentPage;

  const renderPage = () => {
    switch (currentPage) {
      case 'home': return <HomePage setPage={sp} />;
      case 'products': return <ProductsPage setPage={sp} />;
      case 'solutions': return <SolutionsPage setPage={sp} />;
      case 'marketing': return <MarketingPage setPage={sp} />;
      case 'media': return <MediaPage setPage={sp} />;
      case 'retail': return <RetailPage setPage={sp} />;
      case 'finance': return <FinancePage setPage={sp} />;
      case 'resources': return <ResourcesPage setPage={sp} />;
      case 'pricing': return <PricingPage setPage={sp} />;
      case 'company': return <CompanyPage setPage={sp} />;
      case 'docs': return <DocsPage setPage={sp} />;
      case 'trust': return <TrustPage setPage={sp} />;
      case 'contact': return <ContactPage setPage={sp} />;
      case 'marketing_use_cases': return <MarketingUseCasesPage setPage={sp} />;
      case 'media_reference_patterns': return <MediaReferencePatternsPage setPage={sp} />;
      case 'privacy': return <PrivacyPage setPage={sp} />;
      case 'terms': return <TermsPage setPage={sp} />;
      case 'careers': return <CareersPage setPage={sp} />;
      case 'newsroom': return <NewsroomPage setPage={sp} />;
      case 'login': return <LoginPage />;
      default: return <HomePage setPage={sp} />;
    }
  };

  return (
    <div className="min-h-screen bg-white selection:bg-brand-primary/30">
      <Navbar currentPage={currentPage} setPage={setCurrentPage} />
      <AnimatePresence mode="wait">
        {renderPage()}
      </AnimatePresence>
      <Footer setPage={setCurrentPage} />
      <AskPulser />
    </div>
  );
}
