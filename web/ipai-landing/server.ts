import express from "express";
import path from "path";
import { createServer as createViteServer } from "vite";

async function startServer() {
  const app = express();
  const PORT = 3000;

  app.use(express.json());

  // --- Backend Chat Gateway ---
  // This route acts as the secure entry point for the landing page chat.
  // It proxies requests to Azure AI Foundry Agent Service.
  app.post("/api/copilot/chat", async (req, res) => {
    const { message, sessionId, conversationId, context } = req.body;

    // Security: Validate surface
    if (context?.surface !== "landing_page") {
      return res.status(403).json({ error: "Unauthorized surface" });
    }

    try {
      // In a real production environment, you would use the Azure AI Foundry REST API:
      // const foundryEndpoint = `https://${process.env.AZURE_AI_FOUNDRY_PROJECT_NAME}.services.ai.azure.com/api/projects/${process.env.AZURE_AI_FOUNDRY_PROJECT_NAME}/agents/${process.env.AZURE_AI_FOUNDRY_AGENT_ID}/chat`;
      
      // For this implementation, we will simulate the Foundry Agent Service response
      // using the Gemini API on the backend to maintain the "Secure Gateway" pattern.
      // This keeps the API keys hidden from the client.

      // Mocking the "Public Advisory" logic
      const reply = await simulateFoundryResponse(message);

      res.json({
        conversationId: conversationId || "foundry-thread-" + Math.random().toString(36).substring(7),
        reply: reply,
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
      res.status(500).json({ error: "Failed to reach Odoo Copilot" });
    }
  });

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

// Simple simulation of the Odoo Copilot advisory brain
async function simulateFoundryResponse(message: string): Promise<string> {
  // In production, this would be a fetch() call to Azure Foundry
  const lowerMsg = message.toLowerCase();
  
  if (lowerMsg.includes("what is odoo")) {
    return "Odoo on Cloud is a modern, modular ERP platform hosted in a secure environment. It allows you to run finance, CRM, inventory, and more without managing your own servers.";
  }
  if (lowerMsg.includes("copilot")) {
    return "Odoo Copilot is our AI-native assistant layer. It helps teams automate repetitive tasks, summarize complex records, and guide users through operational workflows.";
  }
  if (lowerMsg.includes("industries")) {
    return "We specialize in Marketing, Media & Entertainment, Retail, and Financial Services operations.";
  }
  
  return "Odoo Copilot helps teams unify operations and automate execution. For specific implementation details or a deep dive into your industry, I recommend booking a demo with our specialists.";
}

startServer();
