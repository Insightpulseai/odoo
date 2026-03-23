import { useState, useEffect, useRef } from 'react';
import { 
  Search, ChevronRight, LayoutDashboard, Smartphone, Database, Factory, Box, Globe, X, 
  Cpu, Cloud, BarChart3, Users, Settings, Briefcase, ShieldCheck, CheckCircle2, 
  ArrowRight, PlayCircle, BookOpen, MessageSquare, Newspaper, Zap, Lock, BarChart,
  Target, Tv, ShoppingBag, Landmark, TrendingUp, HelpCircle, Mail, MapPin, ExternalLink
} from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';
import { AIChatCopilot } from './components/AIChatCopilot';

// --- Types ---
type PageId = 'home' | 'products' | 'solutions' | 'marketing' | 'media' | 'retail' | 'finance' | 'resources' | 'pricing' | 'company';

// --- Shared Components ---

const Navbar = ({ currentPage, setPage }: { currentPage: PageId, setPage: (p: PageId) => void }) => {
  const [isSolutionsOpen, setIsSolutionsOpen] = useState(false);

  return (
    <nav className="fixed top-0 left-0 right-0 h-24 bg-white/90 backdrop-blur-md z-50 px-6 md:px-12 flex items-center justify-between border-b border-gray-100">
      <div className="flex items-center gap-12">
        <button onClick={() => setPage('home')} className="flex items-center gap-3 group">
          <img src="/logo.png" alt="InsightPulse AI" className="w-10 h-10 rounded-lg group-hover:scale-105 transition-transform" />
          <span className="text-2xl font-black tracking-tighter uppercase">insightpulse<span className="text-brand-primary">ai</span></span>
        </button>
        
        <div className="hidden xl:flex items-center gap-8 text-[14px] font-bold text-gray-800">
          <button onClick={() => setPage('products')} className={`hover:text-brand-primary transition-colors ${currentPage === 'products' ? 'text-brand-primary' : ''}`}>Products</button>
          
          <div className="relative" onMouseEnter={() => setIsSolutionsOpen(true)} onMouseLeave={() => setIsSolutionsOpen(false)}>
            <button 
              onClick={() => setPage('solutions')} 
              className={`flex items-center gap-1 hover:text-brand-primary transition-colors ${['solutions', 'marketing', 'media', 'retail', 'finance'].includes(currentPage) ? 'text-brand-primary' : ''}`}
            >
              Solutions <ChevronRight size={14} className={`transition-transform ${isSolutionsOpen ? 'rotate-90' : ''}`} />
            </button>
            
            <AnimatePresence>
              {isSolutionsOpen && (
                <motion.div 
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: 10 }}
                  className="absolute top-full left-0 w-72 bg-white shadow-2xl rounded-2xl border border-gray-100 p-4 mt-2"
                >
                  <div className="grid gap-2">
                    <button onClick={() => {setPage('marketing'); setIsSolutionsOpen(false)}} className="flex items-center gap-3 p-3 hover:bg-brand-light rounded-xl transition-colors text-left">
                      <Target size={18} className="text-brand-primary" />
                      <div>
                        <p className="font-bold text-sm">Marketing Operations</p>
                        <p className="text-[11px] text-gray-500">Unified customer & campaign data</p>
                      </div>
                    </button>
                    <button onClick={() => {setPage('media'); setIsSolutionsOpen(false)}} className="flex items-center gap-3 p-3 hover:bg-brand-light rounded-xl transition-colors text-left">
                      <Tv size={18} className="text-brand-primary" />
                      <div>
                        <p className="font-bold text-sm">Media & Entertainment</p>
                        <p className="text-[11px] text-gray-500">Audience & monetization workflows</p>
                      </div>
                    </button>
                    <button onClick={() => {setPage('retail'); setIsSolutionsOpen(false)}} className="flex items-center gap-3 p-3 hover:bg-brand-light rounded-xl transition-colors text-left">
                      <ShoppingBag size={18} className="text-brand-primary" />
                      <div>
                        <p className="font-bold text-sm">Retail Operations</p>
                        <p className="text-[11px] text-gray-500">Inventory & supply-chain resilience</p>
                      </div>
                    </button>
                    <button onClick={() => {setPage('finance'); setIsSolutionsOpen(false)}} className="flex items-center gap-3 p-3 hover:bg-brand-light rounded-xl transition-colors text-left">
                      <Landmark size={18} className="text-brand-primary" />
                      <div>
                        <p className="font-bold text-sm">Financial Operations</p>
                        <p className="text-[11px] text-gray-500">Controls, risk & AI-driven decisions</p>
                      </div>
                    </button>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          <button onClick={() => setPage('resources')} className={`hover:text-brand-primary transition-colors ${currentPage === 'resources' ? 'text-brand-primary' : ''}`}>Resources</button>
          <button onClick={() => setPage('pricing')} className={`hover:text-brand-primary transition-colors ${currentPage === 'pricing' ? 'text-brand-primary' : ''}`}>Pricing</button>
          <button onClick={() => setPage('company')} className={`hover:text-brand-primary transition-colors ${currentPage === 'company' ? 'text-brand-primary' : ''}`}>Company</button>
        </div>
      </div>

      <div className="flex items-center gap-4">
        <button className="p-2.5 hover:bg-gray-100 rounded-full transition-colors hidden sm:block">
          <Search size={20} />
        </button>
        <button className="hidden sm:block px-6 py-2.5 text-[14px] font-bold text-gray-800 hover:text-brand-primary transition-colors">
          Log In
        </button>
        <button className="px-6 py-2.5 text-[14px] font-extrabold bg-brand-primary text-black rounded-full hover:bg-cyan-400 transition-all shadow-lg shadow-brand-primary/20">
          Get Started
        </button>
      </div>
    </nav>
  );
};

const Footer = ({ setPage }: { setPage: (p: PageId) => void }) => (
  <footer className="bg-brand-dark text-white pt-24 pb-12 px-6 md:px-12">
    <div className="max-w-7xl mx-auto">
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-12 mb-20">
        <div className="col-span-2 lg:col-span-1">
          <div className="flex items-center gap-2 mb-8">
            <div className="relative w-8 h-8 flex items-center justify-center">
              <div className="absolute inset-0 bg-brand-primary/40 rounded-full blur-sm"></div>
              <div className="relative w-6 h-3 bg-brand-primary rounded-full"></div>
            </div>
            <span className="text-xl font-black tracking-tighter uppercase">insightpulse<span className="text-brand-primary">ai</span></span>
          </div>
          <p className="text-gray-400 text-sm leading-relaxed mb-8">
            Modern operations that put you in control. Run Odoo in the cloud with AI assistance, analytics, and scalable workflows built for growth.
          </p>
          <div className="flex gap-4">
            <button className="w-10 h-10 rounded-full bg-white/5 flex items-center justify-center hover:bg-brand-primary hover:text-black transition-all">
              <Globe size={18} />
            </button>
            <button className="w-10 h-10 rounded-full bg-white/5 flex items-center justify-center hover:bg-brand-primary hover:text-black transition-all">
              <Mail size={18} />
            </button>
          </div>
        </div>

        <div>
          <h4 className="font-bold mb-6 text-sm uppercase tracking-widest text-brand-primary">Products</h4>
          <ul className="space-y-4 text-gray-400 text-sm">
            <li><button onClick={() => setPage('products')} className="hover:text-white transition-colors">Odoo on Cloud</button></li>
            <li><button onClick={() => setPage('products')} className="hover:text-white transition-colors">Odoo Copilot</button></li>
            <li><button onClick={() => setPage('products')} className="hover:text-white transition-colors">Analytics</button></li>
            <li><button onClick={() => setPage('products')} className="hover:text-white transition-colors">Automations</button></li>
            <li><button onClick={() => setPage('products')} className="hover:text-white transition-colors">Managed Operations</button></li>
          </ul>
        </div>

        <div>
          <h4 className="font-bold mb-6 text-sm uppercase tracking-widest text-brand-primary">Capabilities</h4>
          <ul className="space-y-4 text-gray-400 text-sm">
            <li><button className="hover:text-white transition-colors">Workflow Automation</button></li>
            <li><button className="hover:text-white transition-colors">Dashboards and Reporting</button></li>
            <li><button className="hover:text-white transition-colors">Multi-Company Operations</button></li>
            <li><button className="hover:text-white transition-colors">Controls and Approvals</button></li>
            <li><button className="hover:text-white transition-colors">Integrations</button></li>
            <li><button className="hover:text-white transition-colors">AI Assistance</button></li>
          </ul>
        </div>

        <div>
          <h4 className="font-bold mb-6 text-sm uppercase tracking-widest text-brand-primary">Resources</h4>
          <ul className="space-y-4 text-gray-400 text-sm">
            <li><button onClick={() => setPage('resources')} className="hover:text-white transition-colors">Learning Center</button></li>
            <li><button onClick={() => setPage('resources')} className="hover:text-white transition-colors">Blog</button></li>
            <li><button onClick={() => setPage('resources')} className="hover:text-white transition-colors">Webinars</button></li>
            <li><button onClick={() => setPage('resources')} className="hover:text-white transition-colors">Support</button></li>
            <li><button onClick={() => setPage('pricing')} className="hover:text-white transition-colors">Pricing</button></li>
          </ul>
        </div>

        <div>
          <h4 className="font-bold mb-6 text-sm uppercase tracking-widest text-brand-primary">Company</h4>
          <ul className="space-y-4 text-gray-400 text-sm">
            <li><button onClick={() => setPage('company')} className="hover:text-white transition-colors">Overview</button></li>
            <li><button onClick={() => setPage('company')} className="hover:text-white transition-colors">Careers</button></li>
            <li><button onClick={() => setPage('company')} className="hover:text-white transition-colors">Newsroom</button></li>
            <li><button onClick={() => setPage('company')} className="hover:text-white transition-colors">Contact</button></li>
          </ul>
        </div>
      </div>

      <div className="pt-12 border-t border-white/10 flex flex-col md:flex-row justify-between items-center gap-6 text-xs text-gray-500">
        <p>© 2026 InsightPulseAI. All rights reserved.</p>
        <div className="flex gap-8">
          <a href="#" className="hover:text-white transition-colors">Legal Agreements</a>
          <a href="#" className="hover:text-white transition-colors">Privacy</a>
          <a href="#" className="hover:text-white transition-colors">Cookies</a>
          <a href="#" className="hover:text-white transition-colors">Your Privacy Choices</a>
        </div>
      </div>
    </div>
  </footer>
);

const GlobalCTA = () => (
  <section className="py-24 px-6 md:px-12">
    <div className="max-w-7xl mx-auto bg-brand-primary rounded-[60px] p-12 md:p-24 text-center relative overflow-hidden shadow-2xl">
      <div className="absolute inset-0 grid-pattern opacity-20"></div>
      <div className="relative z-10">
        <h2 className="text-4xl md:text-6xl font-black text-black mb-8 tracking-tight">
          Ready to run Odoo in the cloud with AI built in?
        </h2>
        <p className="text-xl text-black/80 mb-12 max-w-3xl mx-auto font-medium">
          Move from fragmented tools and manual work to one connected operating system with InsightPulseAI.
        </p>
        <div className="flex flex-col sm:flex-row justify-center gap-4">
          <button className="px-12 py-6 bg-black text-white font-extrabold rounded-full hover:bg-gray-900 transition-all shadow-xl">
            Get Started
          </button>
          <button className="px-12 py-6 bg-white text-black font-extrabold rounded-full hover:bg-gray-100 transition-all shadow-xl">
            Request a Demo
          </button>
        </div>
      </div>
    </div>
  </section>
);

// --- Page Components ---

const HomePage = ({ setPage }: { setPage: (p: PageId) => void }) => (
  <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
    {/* Hero */}
    <section className="pt-40 pb-20 px-6 md:px-12">
      <div className="max-w-7xl mx-auto bg-brand-dark rounded-[60px] p-12 md:p-24 relative overflow-hidden min-h-[700px] flex flex-col justify-center shadow-3xl border border-white/10">
        <div className="absolute inset-0 grid-pattern opacity-10"></div>
        <div className="relative z-10 max-w-4xl">
          <motion.div 
            initial={{ y: 20, opacity: 0 }} 
            animate={{ y: 0, opacity: 1 }} 
            transition={{ delay: 0.2 }}
          >
            <h1 className="text-5xl md:text-8xl font-bold text-white leading-[1.05] mb-10 tracking-tight">
              AI-native operations for marketing, media, retail, and financial services
            </h1>
            <p className="text-xl md:text-2xl text-gray-300 leading-relaxed mb-12 font-medium max-w-3xl">
              InsightPulseAI combines <span className="text-brand-primary">Odoo on Cloud</span>, <span className="text-brand-primary">Odoo Copilot</span>, and modern data workflows to help teams unify operations, automate execution, and scale with stronger control.
            </p>
            <div className="flex flex-col sm:flex-row gap-6">
              <button className="px-10 py-5 bg-brand-primary text-black font-extrabold rounded-full hover:bg-cyan-400 transition-all shadow-lg hover:shadow-brand-primary/30 text-lg">
                Get Started
              </button>
              <button className="px-10 py-5 bg-white/10 text-white font-bold rounded-full hover:bg-white/20 transition-all border border-white/10 text-lg backdrop-blur-sm">
                Watch Demo
              </button>
            </div>
          </motion.div>
        </div>
      </div>
    </section>

    {/* Trusted By */}
    <section className="py-12 px-6 md:px-12 border-b border-gray-100">
      <div className="max-w-7xl mx-auto flex flex-wrap justify-center items-center gap-12 md:gap-24 opacity-40 grayscale">
        <span className="text-2xl font-black tracking-tighter uppercase">GlobalMedia</span>
        <span className="text-2xl font-black tracking-tighter uppercase">RetailPulse</span>
        <span className="text-2xl font-black tracking-tighter uppercase">FinFlow</span>
        <span className="text-2xl font-black tracking-tighter uppercase">MarketLogic</span>
        <span className="text-2xl font-black tracking-tighter uppercase">OpsScale</span>
      </div>
    </section>

    {/* Industry Focus */}
    <section className="py-24 px-6 md:px-12 max-w-7xl mx-auto">
      <div className="mb-20">
        <h2 className="text-4xl md:text-6xl font-bold mb-8 tracking-tight">Built for data-heavy, workflow-heavy industries</h2>
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
            className="group bg-brand-light p-12 rounded-[48px] border border-gray-100 text-left hover:bg-brand-dark hover:text-white transition-all duration-500 shadow-sm hover:shadow-2xl"
          >
            <div className="mb-8 group-hover:scale-110 transition-transform duration-500 origin-left">{item.icon}</div>
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
        <div className="mb-20 text-center">
          <h2 className="text-4xl md:text-6xl font-bold mb-8 tracking-tight">One intelligent operating system</h2>
          <p className="text-gray-400 text-xl max-w-3xl mx-auto">Start with what you need. Scale with AI-assisted cloud operations.</p>
        </div>
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
          {[
            { icon: <Cloud size={32} />, title: "Odoo on Cloud", desc: "Run ERP, CRM, sales, inventory, projects, HR, finance, and operations from one hosted platform." },
            { icon: <Cpu size={32} />, title: "Odoo Copilot", desc: "Use AI assistance to reduce manual work, guide users, summarize activity, and improve decision-making." },
            { icon: <ShieldCheck size={32} />, title: "Cloud Operations", desc: "Deploy, govern, monitor, and evolve Odoo with a more reliable cloud delivery model." },
            { icon: <BarChart size={32} />, title: "Analytics", desc: "Turn operational data into real-time executive and team-level visibility." }
          ].map((p, i) => (
            <div key={i} className="bg-white/5 p-10 rounded-[40px] border border-white/10 hover:bg-white/10 transition-all group">
              <div className="mb-8 text-brand-primary group-hover:scale-110 transition-transform duration-500 origin-left">{p.icon}</div>
              <h3 className="text-xl font-bold mb-4">{p.title}</h3>
              <p className="text-gray-400 text-sm leading-relaxed mb-8">{p.desc}</p>
              <button onClick={() => setPage('products')} className="text-brand-primary font-bold text-sm flex items-center gap-2">
                Learn More <ChevronRight size={16} />
              </button>
            </div>
          ))}
        </div>
      </div>
    </section>

    {/* Use Cases */}
    <section className="py-24 px-6 md:px-12 max-w-7xl mx-auto">
      <div className="mb-20">
        <h2 className="text-4xl md:text-5xl font-bold mb-8 tracking-tight">Shared cross-industry pillars</h2>
        <p className="text-gray-600 text-lg">The reusable abstractions that sit underneath our vertical solutions.</p>
      </div>
      <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
        {[
          "Customer and account intelligence", "Workflow orchestration", "Campaign / content / execution operations",
          "Performance measurement and reporting", "Risk, controls, and exception handling", "Multi-entity visibility",
          "AI-assisted decision support"
        ].map((use, i) => (
          <div key={i} className="p-8 rounded-[32px] bg-brand-light border border-gray-100 flex items-start gap-4">
            <CheckCircle2 className="text-brand-primary flex-shrink-0" size={24} />
            <span className="font-bold text-gray-800">{use}</span>
          </div>
        ))}
      </div>
    </section>

    <GlobalCTA />
  </motion.div>
);

const ProductsPage = () => (
  <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="pt-40 pb-24 px-6 md:px-12 max-w-7xl mx-auto">
    <div className="mb-24">
      <h1 className="text-5xl md:text-7xl font-bold mb-10 tracking-tight">The InsightPulseAI Platform</h1>
      <p className="text-xl text-gray-600 max-w-3xl leading-relaxed">
        Combine modular ERP, cloud delivery, automation, and practical AI assistance to improve speed, accuracy, and control across the business.
      </p>
    </div>

    <div className="space-y-32">
      {[
        {
          title: "Odoo on Cloud",
          desc: "Run your entire business from one secure, hosted environment. Odoo on Cloud gives growing companies a flexible platform with anywhere access, centralized data, and faster rollout across teams.",
          features: ["Finance & Accounting", "CRM & Sales", "Inventory & Purchasing", "Project Management", "HR & Operations"],
          icon: <Cloud size={48} className="text-brand-primary" />,
          image: "https://picsum.photos/seed/odoo/800/600"
        },
        {
          title: "Odoo Copilot",
          desc: "An AI-powered assistance layer that helps teams move faster with less manual work. It helps users navigate processes, draft updates, summarize records, and surface exceptions.",
          features: ["Guided Approvals", "Record Summarization", "Exception Detection", "Workflow Acceleration", "AI Reporting"],
          icon: <Cpu size={48} className="text-brand-primary" />,
          image: "https://picsum.photos/seed/copilot/800/600"
        },
        {
          title: "Cloud Operations",
          desc: "Deploy, govern, and evolve Odoo with a reliable cloud delivery model. We handle the technical complexity so you can focus on business outcomes.",
          features: ["Automated Backups", "Security Monitoring", "Performance Optimization", "Governance Controls", "Scalable Infrastructure"],
          icon: <ShieldCheck size={48} className="text-brand-primary" />,
          image: "https://picsum.photos/seed/ops/800/600"
        },
        {
          title: "Analytics & Dashboards",
          desc: "Turn operational data into real-time executive and team-level visibility. Get a clear view of performance, exceptions, and business health.",
          features: ["Real-time KPIs", "Custom Dashboards", "Drill-down Reporting", "AI-assisted Insights", "Cross-functional Views"],
          icon: <BarChart size={48} className="text-brand-primary" />,
          image: "https://picsum.photos/seed/analytics/800/600"
        }
      ].map((p, i) => (
        <div key={i} className={`grid lg:grid-cols-2 gap-24 items-center ${i % 2 === 1 ? 'lg:flex-row-reverse' : ''}`}>
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
          <div className={`bg-brand-light rounded-[60px] p-8 ${i % 2 === 1 ? 'lg:order-1' : ''}`}>
            <img src={p.image} alt={p.title} className="rounded-[40px] shadow-2xl w-full aspect-video object-cover" referrerPolicy="no-referrer" />
          </div>
        </div>
      ))}
    </div>
  </motion.div>
);

const MarketingPage = () => (
  <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
    <section className="pt-40 pb-24 px-6 md:px-12 bg-brand-dark text-white">
      <div className="max-w-7xl mx-auto grid lg:grid-cols-2 gap-24 items-center">
        <div>
          <span className="text-brand-primary font-bold uppercase tracking-widest text-sm mb-6 block">Solutions / Marketing</span>
          <h1 className="text-5xl md:text-7xl font-bold mb-10 tracking-tight leading-[1.1]">
            Marketing operations that connect planning, execution, and insight
          </h1>
          <p className="text-xl text-gray-400 leading-relaxed mb-12">
            Run campaign workflows, content operations, approvals, reporting, budgets, and performance visibility from one AI-assisted operating system.
          </p>
          <button className="px-10 py-5 bg-brand-primary text-black font-extrabold rounded-full hover:bg-cyan-400 transition-all">
            Get Started
          </button>
        </div>
        <div className="bg-white/5 rounded-[60px] p-12 aspect-square flex items-center justify-center border border-white/10 relative overflow-hidden">
          <div className="absolute inset-0 grid-pattern opacity-10"></div>
          <Target size={200} className="text-brand-primary/20" />
        </div>
      </div>
    </section>

    <section className="py-24 px-6 md:px-12 max-w-7xl mx-auto">
      <div className="grid md:grid-cols-3 gap-12">
        {[
          { title: "Unified customer and campaign operations", desc: "Connect your customer data with campaign execution for a true 360-degree view." },
          { title: "AI-assisted planning and execution", desc: "Use Odoo Copilot to draft briefs, summarize results, and guide workflows." },
          { title: "Better measurement and visibility", desc: "Real-time dashboards that show exactly where your marketing spend is going." }
        ].map((v, i) => (
          <div key={i} className="p-10 rounded-[40px] bg-brand-light border border-gray-100">
            <h3 className="text-xl font-bold mb-4">{v.title}</h3>
            <p className="text-gray-600 text-sm leading-relaxed">{v.desc}</p>
          </div>
        ))}
      </div>
    </section>

    <section className="py-24 px-6 md:px-12 max-w-7xl mx-auto border-t border-gray-100">
      <div className="grid lg:grid-cols-2 gap-24 items-center">
        <div>
          <h2 className="text-4xl font-bold mb-10 tracking-tight">From fragmented martech workflows to one operational command layer</h2>
          <div className="space-y-6 text-gray-600 text-lg leading-relaxed">
            <p>
              InsightPulseAI translates unified data into business operations: campaign briefs, approvals, budgets, timelines, content delivery, asset workflows, KPI tracking, and executive reporting.
            </p>
            <p>
              Everything is coordinated inside Odoo on Cloud with Copilot assistance, ensuring your marketing team spends less time on coordination and more time on strategy.
            </p>
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          {["Campaign Briefs", "Approvals", "Budgets", "Timelines", "Content Delivery", "Asset Workflows", "KPI Tracking", "Executive Reporting"].map((item, i) => (
            <div key={i} className="p-6 bg-white rounded-2xl border border-gray-100 shadow-sm font-bold text-gray-800 flex items-center gap-3">
              <div className="w-2 h-2 bg-brand-primary rounded-full"></div>
              {item}
            </div>
          ))}
        </div>
      </div>
    </section>
    <GlobalCTA />
  </motion.div>
);

const MediaPage = () => (
  <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
    <section className="pt-40 pb-24 px-6 md:px-12 bg-brand-dark text-white">
      <div className="max-w-7xl mx-auto grid lg:grid-cols-2 gap-24 items-center">
        <div>
          <span className="text-brand-primary font-bold uppercase tracking-widest text-sm mb-6 block">Solutions / Media & Entertainment</span>
          <h1 className="text-5xl md:text-7xl font-bold mb-10 tracking-tight leading-[1.1]">
            Run audience, content, and monetization workflows with speed
          </h1>
          <p className="text-xl text-gray-400 leading-relaxed mb-12">
            InsightPulseAI helps media, entertainment, publishing, and platform teams manage the operational layer behind audience growth and commercial reporting.
          </p>
          <button className="px-10 py-5 bg-brand-primary text-black font-extrabold rounded-full hover:bg-cyan-400 transition-all">
            Get Started
          </button>
        </div>
        <div className="bg-white/5 rounded-[60px] p-12 aspect-square flex items-center justify-center border border-white/10 relative overflow-hidden">
          <div className="absolute inset-0 grid-pattern opacity-10"></div>
          <Tv size={200} className="text-brand-primary/20" />
        </div>
      </div>
    </section>

    <section className="py-24 px-6 md:px-12 max-w-7xl mx-auto">
      <div className="grid md:grid-cols-3 gap-12">
        {[
          { title: "Audience and partner visibility", desc: "Track audience growth and partner performance in one connected system." },
          { title: "Content and campaign operations", desc: "Manage the entire content supply chain from creation to delivery." },
          { title: "Monetization support workflows", desc: "Automate the commercial workflows that drive your revenue." }
        ].map((v, i) => (
          <div key={i} className="p-10 rounded-[40px] bg-brand-light border border-gray-100">
            <h3 className="text-xl font-bold mb-4">{v.title}</h3>
            <p className="text-gray-600 text-sm leading-relaxed">{v.desc}</p>
          </div>
        ))}
      </div>
    </section>

    <section className="py-24 px-6 md:px-12 max-w-7xl mx-auto border-t border-gray-100">
      <div className="grid lg:grid-cols-2 gap-24 items-center">
        <div>
          <h2 className="text-4xl font-bold mb-10 tracking-tight">From disconnected teams to coordinated audience operations</h2>
          <p className="text-gray-600 text-lg leading-relaxed mb-8">
            Turn audience identity and growth into operational reality: campaign traffic, partner onboarding, creator/vendor workflows, and performance visibility.
          </p>
          <div className="space-y-4">
            {["Partner Onboarding", "Creator Workflows", "Content Release Tracking", "Issue Handling", "Monetization Operations"].map((item, i) => (
              <div key={i} className="flex items-center gap-4 text-gray-800 font-bold">
                <CheckCircle2 className="text-brand-primary" size={24} />
                {item}
              </div>
            ))}
          </div>
        </div>
        <div className="bg-brand-light rounded-[60px] p-12 aspect-video flex items-center justify-center">
          <PlayCircle size={100} className="text-brand-primary/20" />
        </div>
      </div>
    </section>
    <GlobalCTA />
  </motion.div>
);

const RetailPage = () => (
  <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
    <section className="pt-40 pb-24 px-6 md:px-12 bg-brand-dark text-white">
      <div className="max-w-7xl mx-auto grid lg:grid-cols-2 gap-24 items-center">
        <div>
          <span className="text-brand-primary font-bold uppercase tracking-widest text-sm mb-6 block">Solutions / Retail</span>
          <h1 className="text-5xl md:text-7xl font-bold mb-10 tracking-tight leading-[1.1]">
            Retail operations that connect CX, inventory, and fulfillment
          </h1>
          <p className="text-xl text-gray-400 leading-relaxed mb-12">
            Bring merchandising, promotions, operational workflows, inventory visibility, and team execution together in one cloud operating system.
          </p>
          <button className="px-10 py-5 bg-brand-primary text-black font-extrabold rounded-full hover:bg-cyan-400 transition-all">
            Get Started
          </button>
        </div>
        <div className="bg-white/5 rounded-[60px] p-12 aspect-square flex items-center justify-center border border-white/10 relative overflow-hidden">
          <div className="absolute inset-0 grid-pattern opacity-10"></div>
          <ShoppingBag size={200} className="text-brand-primary/20" />
        </div>
      </div>
    </section>

    <section className="py-24 px-6 md:px-12 max-w-7xl mx-auto">
      <div className="grid md:grid-cols-3 gap-12">
        {[
          { title: "Inventory and purchasing visibility", desc: "Real-time stock visibility across all branches and warehouses." },
          { title: "Store and entity operations", desc: "Manage multi-entity retail operations from one central command layer." },
          { title: "Supply-chain resilience", desc: "Automate replenishment and vendor coordination to reduce risk." }
        ].map((v, i) => (
          <div key={i} className="p-10 rounded-[40px] bg-brand-light border border-gray-100">
            <h3 className="text-xl font-bold mb-4">{v.title}</h3>
            <p className="text-gray-600 text-sm leading-relaxed">{v.desc}</p>
          </div>
        ))}
      </div>
    </section>

    <section className="py-24 px-6 md:px-12 max-w-7xl mx-auto border-t border-gray-100">
      <div className="grid lg:grid-cols-2 gap-24 items-center">
        <div>
          <h2 className="text-4xl font-bold mb-10 tracking-tight">From siloed operations to one retail operating layer</h2>
          <p className="text-gray-600 text-lg leading-relaxed mb-8">
            Map retail strategy to ERP workflow reality: stock visibility, replenishment operations, promotion workflows, and branch reporting.
          </p>
          <div className="grid grid-cols-2 gap-4">
            {["Stock Visibility", "Replenishment", "Promotion Workflows", "Branch Reporting", "Inventory Exceptions", "Vendor Coordination"].map((item, i) => (
              <div key={i} className="p-6 bg-brand-light rounded-2xl font-bold text-gray-800 flex items-center gap-3">
                <div className="w-2 h-2 bg-brand-primary rounded-full"></div>
                {item}
              </div>
            ))}
          </div>
        </div>
        <div className="bg-brand-dark rounded-[60px] p-12 aspect-video flex items-center justify-center">
          <Box size={100} className="text-brand-primary/20" />
        </div>
      </div>
    </section>
    <GlobalCTA />
  </motion.div>
);

const FinancePage = () => (
  <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
    <section className="pt-40 pb-24 px-6 md:px-12 bg-brand-dark text-white">
      <div className="max-w-7xl mx-auto grid lg:grid-cols-2 gap-24 items-center">
        <div>
          <span className="text-brand-primary font-bold uppercase tracking-widest text-sm mb-6 block">Solutions / Financial Services</span>
          <h1 className="text-5xl md:text-7xl font-bold mb-10 tracking-tight leading-[1.1]">
            Financial operations with stronger controls and faster decisions
          </h1>
          <p className="text-xl text-gray-400 leading-relaxed mb-12">
            Support approvals, reconciliations, issue tracking, compliance workflows, and operational visibility with AI-assisted Odoo in the cloud.
          </p>
          <button className="px-10 py-5 bg-brand-primary text-black font-extrabold rounded-full hover:bg-cyan-400 transition-all">
            Get Started
          </button>
        </div>
        <div className="bg-white/5 rounded-[60px] p-12 aspect-square flex items-center justify-center border border-white/10 relative overflow-hidden">
          <div className="absolute inset-0 grid-pattern opacity-10"></div>
          <Landmark size={200} className="text-brand-primary/20" />
        </div>
      </div>
    </section>

    <section className="py-24 px-6 md:px-12 max-w-7xl mx-auto">
      <div className="grid md:grid-cols-3 gap-12">
        {[
          { title: "Stronger approval workflows", desc: "Automate and govern approvals across all business processes." },
          { title: "Fraud and risk visibility", desc: "AI-assisted detection of exceptions and risk patterns." },
          { title: "Multi-entity control", desc: "Unified oversight for complex, distributed financial operations." }
        ].map((v, i) => (
          <div key={i} className="p-10 rounded-[40px] bg-brand-light border border-gray-100">
            <h3 className="text-xl font-bold mb-4">{v.title}</h3>
            <p className="text-gray-600 text-sm leading-relaxed">{v.desc}</p>
          </div>
        ))}
      </div>
    </section>

    <section className="py-24 px-6 md:px-12 max-w-7xl mx-auto border-t border-gray-100">
      <div className="grid lg:grid-cols-2 gap-24 items-center">
        <div>
          <h2 className="text-4xl font-bold mb-10 tracking-tight">From fragmented finance processes to governed operations</h2>
          <p className="text-gray-600 text-lg leading-relaxed mb-8">
            Focus on workflow orchestration: close tasks, reconciliations, approvals, compliance tasks, and escalation paths.
          </p>
          <div className="space-y-4">
            {["Close Tasks", "Reconciliations", "Approvals", "Compliance Tasks", "Escalation Paths", "Executive Dashboards"].map((item, i) => (
              <div key={i} className="flex items-center gap-4 text-gray-800 font-bold">
                <ShieldCheck className="text-brand-primary" size={24} />
                {item}
              </div>
            ))}
          </div>
        </div>
        <div className="bg-brand-light rounded-[60px] p-12 aspect-video flex items-center justify-center">
          <TrendingUp size={100} className="text-brand-primary/20" />
        </div>
      </div>
    </section>
    <GlobalCTA />
  </motion.div>
);

const ResourcesPage = () => (
  <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="pt-40 pb-24 px-6 md:px-12 max-w-7xl mx-auto">
    <div className="mb-20">
      <h1 className="text-5xl md:text-7xl font-bold mb-8 tracking-tight">Resource Hub</h1>
      <p className="text-xl text-gray-600 max-w-3xl leading-relaxed">
        Your one place for guides, insights, case studies, implementation advice, and the latest thinking on Odoo, AI copilots, and cloud operations.
      </p>
    </div>

    <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8 mb-24">
      {[
        { icon: <Newspaper />, title: "Blog", desc: "The latest ideas, lessons, and best practices for modern ERP and AI.", link: "Read the Blog" },
        { icon: <BookOpen />, title: "Learning Center", desc: "Explore deeper guides on Odoo, automation, and implementation.", link: "Go to the Learning Center" },
        { icon: <Users />, title: "Customer Stories", desc: "See how teams modernize operations with InsightPulseAI.", link: "Read Customer Stories" },
        { icon: <PlayCircle />, title: "Webinars", desc: "Practical sessions on ERP modernization and AI copilots.", link: "Explore Webinars" },
        { icon: <HelpCircle />, title: "Support and FAQs", desc: "Need implementation help or product guidance?", link: "Get Support" },
        { icon: <Globe />, title: "Partners", desc: "Work with us as an implementation or technology partner.", link: "Explore Partnerships" }
      ].map((card, i) => (
        <div key={i} className="p-10 rounded-[40px] bg-brand-light border border-gray-100 hover:shadow-xl transition-all group">
          <div className="mb-8 text-brand-primary group-hover:scale-110 transition-transform duration-500 origin-left">{card.icon}</div>
          <h3 className="text-xl font-bold mb-4">{card.title}</h3>
          <p className="text-gray-600 text-sm leading-relaxed mb-8">{card.desc}</p>
          <button className="text-black font-bold text-sm flex items-center gap-2 group-hover:text-brand-primary transition-colors">
            {card.link} <ArrowRight size={16} />
          </button>
        </div>
      ))}
    </div>

    <div className="mb-24">
      <h2 className="text-3xl font-bold mb-12 tracking-tight">Featured Resources</h2>
      <div className="grid lg:grid-cols-2 gap-8">
        <div className="bg-brand-dark text-white rounded-[48px] p-12 flex flex-col justify-between min-h-[400px]">
          <div>
            <span className="text-brand-primary font-bold uppercase tracking-widest text-xs mb-6 block">Learning Center</span>
            <h3 className="text-3xl font-bold mb-6 tracking-tight">Odoo on Cloud: Architecture, modules, and implementation guide</h3>
            <p className="text-gray-400 text-lg leading-relaxed mb-8">A practical guide to choosing modules, structuring deployment, and scaling with confidence.</p>
          </div>
          <button className="flex items-center gap-2 font-bold text-brand-primary hover:text-white transition-colors">
            Explore the Guide <ArrowRight size={20} />
          </button>
        </div>
        <div className="bg-brand-primary text-black rounded-[48px] p-12 flex flex-col justify-between min-h-[400px]">
          <div>
            <span className="text-black/60 font-bold uppercase tracking-widest text-xs mb-6 block">Customer Story</span>
            <h3 className="text-3xl font-bold mb-6 tracking-tight">How fast-growing teams use Odoo on Cloud to reduce friction</h3>
            <p className="text-black/70 text-lg leading-relaxed mb-8">See how a modern cloud operating model improves visibility, consistency, and execution.</p>
          </div>
          <button className="flex items-center gap-2 font-bold text-black hover:text-white transition-colors">
            Read the Story <ArrowRight size={20} />
          </button>
        </div>
      </div>
    </div>
  </motion.div>
);

const PricingPage = () => (
  <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="pt-40 pb-24 px-6 md:px-12 max-w-7xl mx-auto">
    <div className="mb-20 text-center">
      <h1 className="text-5xl md:text-7xl font-bold mb-8 tracking-tight">Pricing and Plans</h1>
      <p className="text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
        Our pricing is designed to grow with your business. Start with the foundation you need today, then expand as complexity grows.
      </p>
    </div>

    <div className="grid lg:grid-cols-3 gap-8 mb-24">
      {[
        {
          title: "Launch",
          price: "$99/month",
          features: ["Hosted Odoo environment", "Core module setup", "Role-based user access", "Standard reporting setup", "Baseline support", "Upgrade-ready foundation"],
          cta: "Contact Sales",
          highlight: false
        },
        {
          title: "Growth",
          price: "Custom",
          features: ["Multi-workflow automation", "Enhanced reporting & dashboards", "Odoo Copilot assistance", "Integration support", "Sandbox & rollout guidance", "Expanded operational support"],
          cta: "Contact Sales",
          highlight: true
        },
        {
          title: "Enterprise",
          price: "Custom",
          features: ["Multi-company architecture", "Advanced governance & controls", "Priority support", "Deeper integrations", "AI-assisted operations rollout", "Tailored cloud operating model"],
          cta: "Contact Sales",
          highlight: false
        }
      ].map((tier, i) => (
        <div key={i} className={`p-12 rounded-[48px] border ${tier.highlight ? 'bg-brand-dark text-white border-brand-dark shadow-2xl' : 'bg-brand-light border-gray-100'}`}>
          <h3 className="text-2xl font-bold mb-4">{tier.title}</h3>
          <div className={`text-4xl font-black mb-10 ${tier.highlight ? 'text-brand-primary' : 'text-black'}`}>{tier.price}</div>
          <ul className="space-y-4 mb-12">
            {tier.features.map((f, j) => (
              <li key={j} className="flex items-start gap-3 text-sm">
                <CheckCircle2 className={tier.highlight ? 'text-brand-primary' : 'text-gray-400'} size={18} />
                <span className={tier.highlight ? 'text-gray-300' : 'text-gray-600'}>{f}</span>
              </li>
            ))}
          </ul>
          <button className={`w-full py-5 rounded-full font-extrabold transition-all ${tier.highlight ? 'bg-brand-primary text-black hover:bg-cyan-400' : 'bg-black text-white hover:bg-gray-800'}`}>
            {tier.cta}
          </button>
        </div>
      ))}
    </div>

    <div className="bg-brand-light rounded-[60px] p-12 md:p-24 text-center">
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

const CompanyPage = () => (
  <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
    <section className="pt-40 pb-24 px-6 md:px-12 max-w-7xl mx-auto">
      <div className="mb-24">
        <h1 className="text-5xl md:text-8xl font-bold mb-10 tracking-tight leading-[1.05]">
          The most ambitious operators choose systems that can scale
        </h1>
        <p className="text-xl md:text-2xl text-gray-600 max-w-4xl leading-relaxed">
          InsightPulseAI helps growing businesses modernize operations with Odoo on Cloud, AI copilots, analytics, and automation that reduce friction across the business.
        </p>
      </div>

      <div className="grid lg:grid-cols-2 gap-24 items-center mb-32">
        <div>
          <h2 className="text-4xl font-bold mb-8 tracking-tight">It started with a simple problem: operations moved faster than systems could keep up</h2>
          <p className="text-gray-600 text-lg leading-relaxed mb-10">
            Businesses were being slowed down by fragmented tools, manual workflows, and ERP environments that were too rigid to evolve. InsightPulseAI was built to close that gap with a more adaptive operating model powered by Odoo, cloud delivery, and AI assistance.
          </p>
          <div className="grid sm:grid-cols-3 gap-8">
            <div>
              <p className="text-4xl font-black text-brand-primary mb-2">100%</p>
              <p className="text-xs font-bold uppercase tracking-widest text-gray-500">Modern Architecture</p>
            </div>
            <div>
              <p className="text-4xl font-black text-brand-primary mb-2">Cloud</p>
              <p className="text-xs font-bold uppercase tracking-widest text-gray-500">First Delivery</p>
            </div>
            <div>
              <p className="text-4xl font-black text-brand-primary mb-2">AI</p>
              <p className="text-xs font-bold uppercase tracking-widest text-gray-500">Assisted Ops</p>
            </div>
          </div>
        </div>
        <div className="bg-brand-dark rounded-[60px] p-12 aspect-square flex items-center justify-center relative overflow-hidden">
          <div className="absolute inset-0 grid-pattern opacity-10"></div>
          <span className="text-brand-primary text-9xl font-black opacity-20">IPAI</span>
        </div>
      </div>

      <div className="mb-32">
        <h2 className="text-4xl font-bold mb-16 tracking-tight">What Sets Us Apart</h2>
        <div className="grid md:grid-cols-3 gap-12">
          {[
            { title: "Who We Are", desc: "InsightPulseAI is an operations and ERP modernization company focused on helping teams run better with Odoo on Cloud and AI copilots." },
            { title: "What We Do", desc: "We design, deploy, and evolve cloud-based Odoo environments with modern workflows, automation, and analytics." },
            { title: "Why We're Different", desc: "We combine implementation thinking, architecture, automation, and AI into one coherent operating model." }
          ].map((item, i) => (
            <div key={i} className="p-10 rounded-[40px] bg-brand-light border border-gray-100">
              <h3 className="text-xl font-bold mb-6">{item.title}</h3>
              <p className="text-gray-600 leading-relaxed">{item.desc}</p>
            </div>
          ))}
        </div>
      </div>

      <div className="bg-brand-dark text-white rounded-[60px] p-12 md:p-24 flex flex-col lg:flex-row items-center justify-between gap-12">
        <div className="max-w-xl">
          <h2 className="text-4xl font-bold mb-8 tracking-tight">Join Our Team</h2>
          <p className="text-gray-400 text-lg leading-relaxed">
            We're building the future of practical AI-assisted business operations. If you care about execution, systems, and meaningful outcomes, we'd love to hear from you.
          </p>
        </div>
        <button className="px-12 py-6 bg-brand-primary text-black font-extrabold rounded-full hover:bg-cyan-400 transition-all whitespace-nowrap">
          See Careers
        </button>
      </div>
    </section>
    <GlobalCTA />
  </motion.div>
);

// --- Main App ---

export default function App() {
  const [currentPage, setCurrentPage] = useState<PageId>('home');

  useEffect(() => {
    window.scrollTo(0, 0);
  }, [currentPage]);

  const renderPage = () => {
    switch (currentPage) {
      case 'home': return <HomePage setPage={setCurrentPage} />;
      case 'products': return <ProductsPage />;
      case 'marketing': return <MarketingPage />;
      case 'media': return <MediaPage />;
      case 'retail': return <RetailPage />;
      case 'finance': return <FinancePage />;
      case 'resources': return <ResourcesPage />;
      case 'pricing': return <PricingPage />;
      case 'company': return <CompanyPage />;
      case 'solutions': return <HomePage setPage={setCurrentPage} />; // Default to home for solutions overview for now
      default: return <HomePage setPage={setCurrentPage} />;
    }
  };

  return (
    <div className="min-h-screen bg-white selection:bg-brand-primary/30">
      <Navbar currentPage={currentPage} setPage={setCurrentPage} />
      <AnimatePresence mode="wait">
        {renderPage()}
      </AnimatePresence>
      <Footer setPage={setCurrentPage} />
      <AIChatCopilot />
    </div>
  );
}
