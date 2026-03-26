import express from "express";
import path from "path";
import { createServer as createViteServer } from "vite";

// --- CTA Action Types (mirrors client ChatCtaAction) ---

type ChatCtaAction =
  | { type: 'send_prompt'; label: string; prompt: string; analytics_id?: string }
  | { type: 'navigate'; label: string; href: string; new_tab?: boolean; analytics_id?: string }
  | { type: 'open_scheduler'; label: string; href: string; analytics_id?: string }
  | { type: 'open_contact'; label: string; page?: string; analytics_id?: string };

interface PulserResponse {
  reply: string;
  sourceLabel: string;
  ctas: ChatCtaAction[];
}

const DEMO_URL = 'https://insightpulseai.zohobookings.com/';

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

// --- Foundry Agent Service ---

const FOUNDRY_CONFIG = {
  endpoint: process.env.AZURE_AI_FOUNDRY_OPENAI_ENDPOINT || '',
  apiKey: process.env.AZURE_AI_FOUNDRY_API_KEY || '',
  agentId: process.env.AZURE_AI_FOUNDRY_AGENT_ID || '',
  apiVersion: '2024-10-01-preview',
};

const SYSTEM_PROMPT = `You are Pulser, the InsightPulseAI product assistant on the public marketing website.

Rules:
- You answer from approved public sources only: product docs, architecture, pricing, FAQs.
- You CANNOT access any ERP data, tenant data, company data, or user records.
- You CANNOT perform any actions, create records, or modify anything.
- You are in public advisory mode only.
- Use canonical naming: InsightPulseAI (one word), Pulser (not Copilot), Odoo on Cloud, Cloud Operations, Analytics & Dashboards.
- Never say "Odoo Copilot", "IPAI Copilot", or "Copilot" as your name.
- Keep answers concise (2-4 sentences).
- If asked about pricing, say plans are custom and suggest booking a demo.
- If asked about implementation, suggest talking to a specialist.

Product stack:
- Odoo on Cloud: modular ERP (Finance, CRM, Sales, Inventory, Projects, HR) hosted on Azure
- Pulser: AI-native intelligence layer for Odoo workflows (operational guidance, context summaries, exception detection)
- Cloud Operations: managed delivery, security, backups, governance
- Analytics & Dashboards: real-time KPIs, drill-down reporting, AI-assisted insights (Databricks + Power BI)
- Architecture: Azure Container Apps, Entra ID (auth), Azure AI Foundry (agent runtime), Document Intelligence (OCR)

Industries: Marketing, Media & Entertainment, Retail, Financial Services.`;

// Thread store (in-memory, per-session)
const threads = new Map<string, string>();

async function foundryChat(message: string, conversationId: string | null): Promise<{ reply: string; threadId: string }> {
  const { endpoint, apiKey, agentId, apiVersion } = FOUNDRY_CONFIG;
  const baseUrl = `${endpoint}/openai`;
  const headers = {
    'api-key': apiKey,
    'Content-Type': 'application/json',
  };

  // Get or create thread
  let threadId = conversationId ? threads.get(conversationId) : null;

  if (!threadId) {
    const threadRes = await fetch(`${baseUrl}/threads?api-version=${apiVersion}`, {
      method: 'POST',
      headers,
      body: JSON.stringify({}),
    });
    if (!threadRes.ok) throw new Error(`Thread creation failed: ${threadRes.status}`);
    const threadData = await threadRes.json();
    threadId = threadData.id;
  }

  // Add user message
  await fetch(`${baseUrl}/threads/${threadId}/messages?api-version=${apiVersion}`, {
    method: 'POST',
    headers,
    body: JSON.stringify({ role: 'user', content: message }),
  });

  // Create run with agent
  const runRes = await fetch(`${baseUrl}/threads/${threadId}/runs?api-version=${apiVersion}`, {
    method: 'POST',
    headers,
    body: JSON.stringify({
      assistant_id: agentId,
      instructions: SYSTEM_PROMPT,
    }),
  });
  if (!runRes.ok) throw new Error(`Run creation failed: ${runRes.status}`);
  const run = await runRes.json();

  // Poll for completion (max 30s)
  const deadline = Date.now() + 30000;
  let status = run.status;
  while (status === 'queued' || status === 'in_progress') {
    if (Date.now() > deadline) throw new Error('Foundry timeout');
    await new Promise(r => setTimeout(r, 500));
    const pollRes = await fetch(`${baseUrl}/threads/${threadId}/runs/${run.id}?api-version=${apiVersion}`, { headers });
    const pollData = await pollRes.json();
    status = pollData.status;
  }

  if (status !== 'completed') throw new Error(`Run failed: ${status}`);

  // Get latest assistant message
  const msgsRes = await fetch(`${baseUrl}/threads/${threadId}/messages?api-version=${apiVersion}&order=desc&limit=1`, { headers });
  const msgsData = await msgsRes.json();
  const assistantMsg = msgsData.data?.find((m: any) => m.role === 'assistant');
  const reply = assistantMsg?.content?.[0]?.text?.value || 'I apologize, I was unable to generate a response. Please try again.';

  return { reply, threadId: threadId! };
}

function isFoundryConfigured(): boolean {
  return !!(FOUNDRY_CONFIG.endpoint && FOUNDRY_CONFIG.apiKey && FOUNDRY_CONFIG.agentId);
}

// --- CTA inference from response ---

function inferCtas(message: string, reply: string): ChatCtaAction[] {
  const lower = (message + ' ' + reply).toLowerCase();
  const ctas: ChatCtaAction[] = [];

  if (lower.includes('demo') || lower.includes('book') || lower.includes('trial')) {
    ctas.push({ type: 'open_scheduler', label: 'Book a demo', href: DEMO_URL, analytics_id: 'chat_book_demo' });
  }
  if (lower.includes('pricing') || lower.includes('cost') || lower.includes('plan')) {
    ctas.push({ type: 'navigate', label: 'See pricing', href: '#pricing', analytics_id: 'chat_nav_pricing' });
    ctas.push(HANDOFF_CTA);
  }
  if (lower.includes('contact') || lower.includes('specialist') || lower.includes('talk to')) {
    ctas.push(HANDOFF_CTA);
  }
  if (lower.includes('module') || lower.includes('finance') || lower.includes('crm') || lower.includes('inventory')) {
    ctas.push({ type: 'navigate', label: 'View products', href: '#products', analytics_id: 'chat_nav_products' });
  }
  if (lower.includes('marketing') || lower.includes('media') || lower.includes('retail')) {
    ctas.push({ type: 'navigate', label: 'View solutions', href: '#solutions', analytics_id: 'chat_nav_solutions' });
  }
  if (lower.includes('architecture') || lower.includes('security') || lower.includes('azure')) {
    ctas.push({ type: 'navigate', label: 'Trust Center', href: '#trust', analytics_id: 'chat_nav_trust' });
  }

  // Always offer at least one follow-up
  if (ctas.length === 0) {
    ctas.push(...DEFAULT_FOLLOWUP_CTAS);
  }

  // Deduplicate by label
  const seen = new Set<string>();
  return ctas.filter(c => {
    if (seen.has(c.label)) return false;
    seen.add(c.label);
    return true;
  }).slice(0, 4);
}

// --- Mock fallback (used when Foundry is not configured) ---

async function buildMockResponse(message: string): Promise<PulserResponse> {
  const lowerMsg = message.toLowerCase();

  if (lowerMsg.includes("what is pulser")) {
    return {
      reply: "Pulser is the intelligent assistant family by InsightPulseAI. It helps teams navigate ERP workflows, summarize records, and make faster operational decisions — all built on Odoo CE and Azure.",
      sourceLabel: "Product Docs",
      ctas: inferCtas(message, "pulser intelligence"),
    };
  }
  if (lowerMsg.includes("core modules") || lowerMsg.includes("what modules")) {
    return {
      reply: "Odoo on Cloud includes Finance & Accounting, CRM & Sales, Inventory & Purchasing, Project Management, and HR & Operations. Each module runs in a secure Azure environment with Pulser assistance available across workflows.",
      sourceLabel: "Product Docs",
      ctas: inferCtas(message, "modules finance crm"),
    };
  }
  if (lowerMsg.includes("odoo") && lowerMsg.includes("cloud")) {
    return {
      reply: "Odoo on Cloud is a modern, modular ERP platform hosted in a secure Azure environment. It allows you to run finance, CRM, inventory, and more without managing your own servers. Pulser adds operational intelligence on top.",
      sourceLabel: "Product Docs",
      ctas: inferCtas(message, "odoo cloud modules"),
    };
  }
  if (lowerMsg.includes("industr")) {
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
  if (lowerMsg.includes("pricing") || lowerMsg.includes("cost") || lowerMsg.includes("plan")) {
    return {
      reply: "InsightPulseAI offers Launch, Growth, and Enterprise plans. Each is shaped by your operating model, workflow scope, and support needs. I'd recommend speaking with our team for a conversation tailored to your requirements.",
      sourceLabel: "Pricing",
      ctas: inferCtas(message, "pricing plan cost"),
    };
  }
  if (lowerMsg.includes("demo") || lowerMsg.includes("trial") || lowerMsg.includes("get started")) {
    return {
      reply: "I'd be happy to connect you with our team. You can book a demo directly or reach out to discuss your specific requirements.",
      sourceLabel: "Product Docs",
      ctas: inferCtas(message, "demo book"),
    };
  }
  if (lowerMsg.includes("architecture") || lowerMsg.includes("how does it work")) {
    return {
      reply: "InsightPulseAI runs on Azure Container Apps with Odoo CE 19 as the ERP backbone, Databricks for analytics, and Azure AI Foundry for the Pulser agent runtime. All services use managed identity and Key Vault for secrets.",
      sourceLabel: "Architecture",
      ctas: inferCtas(message, "architecture azure security"),
    };
  }
  if (lowerMsg.includes("security") || lowerMsg.includes("compliance")) {
    return {
      reply: "InsightPulseAI uses Azure managed identity, Key Vault for secrets, role-based access, and encrypted data at rest and in transit. The platform is hosted in Azure Southeast Asia with managed certificates for TLS.",
      sourceLabel: "Architecture",
      ctas: inferCtas(message, "security azure trust"),
    };
  }

  return {
    reply: "Pulser helps teams unify operations and automate execution across ERP, analytics, and workflows. I can walk you through the platform or connect you with a specialist.",
    sourceLabel: "Product Docs",
    ctas: [...DEFAULT_FOLLOWUP_CTAS, HANDOFF_CTA],
  };
}

// --- Main server ---

async function startServer() {
  const app = express();
  const PORT = 3000;

  app.use(express.json());

  const foundryEnabled = isFoundryConfigured();
  console.log(`Pulser backend: ${foundryEnabled ? 'Azure AI Foundry Agent Service' : 'mock responses (set AZURE_AI_FOUNDRY_* env vars to enable Foundry)'}`);

  // DEPRECATED: /api/copilot/chat — Remove after 2026-04-30
  app.post("/api/copilot/chat", handleChat);
  app.post("/api/pulser/chat", handleChat);

  async function handleChat(req: express.Request, res: express.Response) {
    const { message, sessionId, conversationId, context } = req.body;

    if (context?.surface !== "landing_page") {
      return res.status(403).json({ error: "Unauthorized surface" });
    }

    try {
      let result: PulserResponse;

      if (foundryEnabled) {
        // --- Foundry Agent Service ---
        const { reply, threadId } = await foundryChat(message, conversationId);
        const newConvId = conversationId || "pulser-thread-" + Math.random().toString(36).substring(7);
        threads.set(newConvId, threadId);

        result = {
          reply,
          sourceLabel: 'Pulser',
          ctas: inferCtas(message, reply),
        };

        return res.json({
          conversationId: newConvId,
          reply: result.reply,
          sourceLabel: result.sourceLabel,
          ctas: result.ctas,
          citations: [],
          mode: "public_advisory",
        });
      } else {
        // --- Mock fallback ---
        result = await buildMockResponse(message);

        return res.json({
          conversationId: conversationId || "pulser-thread-" + Math.random().toString(36).substring(7),
          reply: result.reply,
          sourceLabel: result.sourceLabel,
          ctas: result.ctas,
          citations: [],
          mode: "public_advisory",
        });
      }
    } catch (error) {
      console.error("Gateway error:", error);

      // Fallback to mock on Foundry failure
      if (foundryEnabled) {
        try {
          const fallback = await buildMockResponse(message);
          return res.json({
            conversationId: conversationId || "pulser-thread-" + Math.random().toString(36).substring(7),
            reply: fallback.reply,
            sourceLabel: fallback.sourceLabel + ' (fallback)',
            ctas: fallback.ctas,
            citations: [],
            mode: "public_advisory",
          });
        } catch { /* fall through to error */ }
      }

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

startServer();
