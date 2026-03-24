import express from "express";
import path from "path";
import { createServer as createViteServer } from "vite";

// --- CTA Action Types (mirrors client ChatCtaAction) ---

type ChatCtaAction =
  | { type: 'send_prompt'; label: string; prompt: string; analytics_id?: string }
  | { type: 'navigate'; label: string; href: string; new_tab?: boolean; analytics_id?: string }
  | { type: 'open_scheduler'; label: string; href: string; analytics_id?: string }
  | { type: 'open_contact'; label: string; page?: string; analytics_id?: string };

const DEMO_URL = 'https://calendar.google.com/calendar/appointments';

// --- Default follow-up CTAs ---

const DEFAULT_FOLLOWUP_CTAS: ChatCtaAction[] = [
  { type: 'send_prompt', label: 'Show me the core modules', prompt: 'Show me the core modules in Odoo on Cloud.', analytics_id: 'chat_core_modules' },
  { type: 'send_prompt', label: 'How does Odoo on Cloud work?', prompt: 'How does Odoo on Cloud work?', analytics_id: 'chat_odoo_on_cloud' },
  { type: 'open_scheduler', label: 'Book a demo', href: DEMO_URL, analytics_id: 'chat_book_demo' },
];

const HANDOFF_CTA: ChatCtaAction = {
  type: 'open_contact',
  label: 'Talk to a specialist',
  page: 'contact',
  analytics_id: 'chat_talk_to_specialist',
};

async function startServer() {
  const app = express();
  const PORT = 3000;

  app.use(express.json());

  // --- Pulser Chat Gateway ---
  // DEPRECATED: /api/copilot/chat — Remove after 2026-04-30
  app.post("/api/copilot/chat", handleChat);
  app.post("/api/pulser/chat", handleChat);

  async function handleChat(req: express.Request, res: express.Response) {
    const { message, sessionId, conversationId, context } = req.body;

    if (context?.surface !== "landing_page") {
      return res.status(403).json({ error: "Unauthorized surface" });
    }

    try {
      const result = await buildPulserResponse(message);

      res.json({
        conversationId: conversationId || "pulser-thread-" + Math.random().toString(36).substring(7),
        reply: result.reply,
        sourceLabel: result.sourceLabel,
        ctas: result.ctas,
        citations: [],
        mode: "public_advisory",
      });
    } catch (error) {
      console.error("Gateway error:", error);
      res.status(500).json({ error: "Failed to reach Pulser service" });
    }
  }

  // Vite middleware for development
  if (process.env.NODE_ENV !== "production") {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: "spa",
    });
    app.use(vite.middlewares);
  } else {
    const distPath = path.join(process.cwd(), 'dist');
    app.use(express.static(distPath));
    app.get('*', (req, res) => {
      res.sendFile(path.join(distPath, 'index.html'));
    });
  }

  app.listen(PORT, "0.0.0.0", () => {
    console.log(`Server running on http://localhost:${PORT}`);
  });
}

// --- Response builder (replace with Foundry in production) ---

interface PulserResponse {
  reply: string;
  sourceLabel: string;
  ctas: ChatCtaAction[];
}

async function buildPulserResponse(message: string): Promise<PulserResponse> {
  const lowerMsg = message.toLowerCase();

  if (lowerMsg.includes("what is pulser")) {
    return {
      reply: "Pulser is the intelligent assistant family by InsightPulseAI. It helps teams navigate ERP workflows, summarize records, and make faster operational decisions — all built on Odoo CE and Azure.",
      sourceLabel: "Product Docs",
      ctas: [
        { type: 'send_prompt', label: 'How does it work with Odoo?', prompt: 'How does Pulser work with Odoo on Cloud?', analytics_id: 'chat_pulser_odoo' },
        { type: 'navigate', label: 'View products', href: '#products', analytics_id: 'chat_nav_products' },
        { type: 'open_scheduler', label: 'Book a demo', href: DEMO_URL, analytics_id: 'chat_book_demo' },
      ],
    };
  }

  if (lowerMsg.includes("core modules") || lowerMsg.includes("what modules")) {
    return {
      reply: "Odoo on Cloud includes Finance & Accounting, CRM & Sales, Inventory & Purchasing, Project Management, and HR & Operations. Each module runs in a secure Azure environment with Pulser assistance available across workflows.",
      sourceLabel: "Product Docs",
      ctas: [
        { type: 'send_prompt', label: 'Tell me about analytics', prompt: 'What analytics and dashboards are available?', analytics_id: 'chat_analytics' },
        { type: 'navigate', label: 'See pricing', href: '#pricing', analytics_id: 'chat_nav_pricing' },
        { type: 'open_contact', label: 'Talk to a specialist', page: 'contact', analytics_id: 'chat_talk_to_specialist' },
      ],
    };
  }

  if (lowerMsg.includes("what is odoo") || lowerMsg.includes("odoo on cloud")) {
    return {
      reply: "Odoo on Cloud is a modern, modular ERP platform hosted in a secure Azure environment. It allows you to run finance, CRM, inventory, and more without managing your own servers. Pulser adds intelligent assistance on top.",
      sourceLabel: "Product Docs",
      ctas: [
        { type: 'send_prompt', label: 'Show me the core modules', prompt: 'Show me the core modules in Odoo on Cloud.', analytics_id: 'chat_core_modules' },
        { type: 'navigate', label: 'View architecture', href: '#trust', analytics_id: 'chat_nav_trust' },
        { type: 'open_scheduler', label: 'Book a demo', href: DEMO_URL, analytics_id: 'chat_book_demo' },
      ],
    };
  }

  if (lowerMsg.includes("industries") || lowerMsg.includes("who is this for")) {
    return {
      reply: "We specialize in Marketing, Media & Entertainment, Retail, and Financial Services operations.",
      sourceLabel: "Product Docs",
      ctas: [
        { type: 'navigate', label: 'Marketing solutions', href: '#marketing', analytics_id: 'chat_nav_marketing' },
        { type: 'navigate', label: 'Media solutions', href: '#media', analytics_id: 'chat_nav_media' },
        { type: 'navigate', label: 'Retail solutions', href: '#retail', analytics_id: 'chat_nav_retail' },
        { type: 'navigate', label: 'Finance solutions', href: '#finance', analytics_id: 'chat_nav_finance' },
      ],
    };
  }

  if (lowerMsg.includes("analytics") || lowerMsg.includes("dashboard")) {
    return {
      reply: "InsightPulseAI provides real-time KPI dashboards, drill-down reporting, AI-assisted insights, and cross-functional views. Analytics are powered by Databricks and surfaced through Power BI and custom dashboards.",
      sourceLabel: "Product Docs",
      ctas: [
        { type: 'navigate', label: 'View products', href: '#products', analytics_id: 'chat_nav_products' },
        { type: 'open_scheduler', label: 'Book a demo', href: DEMO_URL, analytics_id: 'chat_book_demo' },
      ],
    };
  }

  if (lowerMsg.includes("architecture") || lowerMsg.includes("how does it work")) {
    return {
      reply: "InsightPulseAI runs on Azure Container Apps with Odoo CE 19 as the ERP backbone, Databricks for analytics, and Azure AI Foundry for the Pulser assistant runtime. All services are behind Azure Front Door with managed identity and Key Vault for secrets.",
      sourceLabel: "Architecture",
      ctas: [
        { type: 'navigate', label: 'Trust & readiness', href: '#trust', analytics_id: 'chat_nav_trust' },
        { type: 'send_prompt', label: 'What about security?', prompt: 'How does InsightPulseAI handle security and data protection?', analytics_id: 'chat_security' },
      ],
    };
  }

  if (lowerMsg.includes("pricing") || lowerMsg.includes("cost") || lowerMsg.includes("plan")) {
    return {
      reply: "InsightPulseAI offers Starter, Growth, and Scale plans. Each includes Odoo on Cloud, Pulser assistant access, and cloud operations. I'd recommend speaking with our team for a pricing conversation tailored to your needs.",
      sourceLabel: "Pricing",
      ctas: [
        { type: 'navigate', label: 'See pricing details', href: '#pricing', analytics_id: 'chat_nav_pricing' },
        HANDOFF_CTA,
        { type: 'open_scheduler', label: 'Book a demo', href: DEMO_URL, analytics_id: 'chat_book_demo' },
      ],
    };
  }

  if (lowerMsg.includes("demo") || lowerMsg.includes("trial") || lowerMsg.includes("get started")) {
    return {
      reply: "I'd be happy to connect you with our team. You can book a demo directly or reach out to discuss your specific requirements.",
      sourceLabel: "Product Docs",
      ctas: [
        { type: 'open_scheduler', label: 'Book a demo', href: DEMO_URL, analytics_id: 'chat_book_demo' },
        HANDOFF_CTA,
      ],
    };
  }

  if (lowerMsg.includes("security") || lowerMsg.includes("compliance") || lowerMsg.includes("data protection")) {
    return {
      reply: "InsightPulseAI uses Azure managed identity, Key Vault for secrets, role-based access, and encrypted data at rest and in transit. The platform is hosted in Azure Southeast Asia with Front Door edge protection.",
      sourceLabel: "Architecture",
      ctas: [
        { type: 'navigate', label: 'Trust & readiness', href: '#trust', analytics_id: 'chat_nav_trust' },
        HANDOFF_CTA,
      ],
    };
  }

  // Default fallback
  return {
    reply: "Pulser helps teams unify operations and automate execution across ERP, analytics, and creative workflows. I can walk you through the platform or connect you with a specialist.",
    sourceLabel: "Product Docs",
    ctas: [...DEFAULT_FOLLOWUP_CTAS, HANDOFF_CTA],
  };
}

startServer();
