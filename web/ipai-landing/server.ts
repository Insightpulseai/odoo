import express from "express";
import path from "path";
import { createServer as createViteServer } from "vite";

async function startServer() {
  const app = express();
  const PORT = 3000;

  app.use(express.json());

  // --- Pulser Chat Gateway ---
  // Secure entry point for the landing page product assistant.
  // Proxies requests to Azure AI Foundry Agent Service.
  // DEPRECATED: Remove after 2026-04-30. Use /api/pulser/chat.
  app.post("/api/copilot/chat", handleChat);
  app.post("/api/pulser/chat", handleChat);

  async function handleChat(req: express.Request, res: express.Response) {
    const { message, sessionId, conversationId, context } = req.body;

    // Security: Validate surface
    if (context?.surface !== "landing_page") {
      return res.status(403).json({ error: "Unauthorized surface" });
    }

    try {
      const { reply, sourceLabel } = await simulatePulserResponse(message);

      res.json({
        conversationId: conversationId || "pulser-thread-" + Math.random().toString(36).substring(7),
        reply: reply,
        sourceLabel: sourceLabel,
        citations: [],
        suggestedPrompts: [
          "Show me the core modules",
          "How does Odoo on Cloud work?",
          "Book a demo"
        ],
        mode: "public_advisory",
        handoff: message.toLowerCase().includes("demo") || message.toLowerCase().includes("price") ? {
          type: "demo_cta",
          label: "Talk to a specialist"
        } : null
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

// Pulser product assistant — mock responses (replace with Foundry in production)
async function simulatePulserResponse(message: string): Promise<{ reply: string; sourceLabel: string }> {
  const lowerMsg = message.toLowerCase();

  if (lowerMsg.includes("what is pulser")) {
    return {
      reply: "Pulser is the intelligent assistant family by InsightPulseAI. It helps teams navigate ERP workflows, summarize records, and make faster operational decisions — all built on Odoo CE and Azure.",
      sourceLabel: "Product Docs"
    };
  }
  if (lowerMsg.includes("what is odoo") || lowerMsg.includes("odoo on cloud")) {
    return {
      reply: "Odoo on Cloud is a modern, modular ERP platform hosted in a secure Azure environment. It allows you to run finance, CRM, inventory, and more without managing your own servers. Pulser adds intelligent assistance on top.",
      sourceLabel: "Product Docs"
    };
  }
  if (lowerMsg.includes("industries")) {
    return {
      reply: "We specialize in Marketing, Media & Entertainment, Retail, and Financial Services operations.",
      sourceLabel: "Product Docs"
    };
  }
  if (lowerMsg.includes("architecture") || lowerMsg.includes("how does it work")) {
    return {
      reply: "InsightPulseAI runs on Azure Container Apps with Odoo CE 19 as the ERP backbone, Databricks for analytics, and Azure AI Foundry for the Pulser assistant runtime. All services are behind Azure Front Door with managed identity and Key Vault for secrets.",
      sourceLabel: "Architecture"
    };
  }
  if (lowerMsg.includes("pricing") || lowerMsg.includes("cost") || lowerMsg.includes("plan")) {
    return {
      reply: "InsightPulseAI offers Starter, Growth, and Scale plans. Each includes Odoo on Cloud, Pulser assistant access, and managed operations. I'd recommend speaking with our team for a pricing conversation tailored to your needs.",
      sourceLabel: "Pricing"
    };
  }

  return {
    reply: "Pulser helps teams unify operations and automate execution across ERP, analytics, and creative workflows. For specific implementation details or a deep dive into your industry, I recommend booking a demo with our specialists.",
    sourceLabel: "Product Docs"
  };
}

startServer();
