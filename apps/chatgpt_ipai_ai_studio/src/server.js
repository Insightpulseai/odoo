/**
 * IPAI AI Studio - ChatGPT App MCP Server
 *
 * MCP server that exposes Odoo AI Studio tools to ChatGPT.
 * Connects to Odoo via JSON-RPC for actual execution.
 *
 * Usage:
 *   npm install
 *   ODOO_BASE_URL=https://erp.example.com npm start
 */

import { readFileSync } from "node:fs";
import http from "node:http";
import { fileURLToPath } from "node:url";
import path from "node:path";
import { z } from "zod";

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/streamableHttp.js";

// Configuration from environment
const PORT = parseInt(process.env.PORT || "8787", 10);
const ODOO_BASE_URL = process.env.ODOO_BASE_URL || "https://erp.insightpulseai.net";
const ODOO_DB = process.env.ODOO_DB || "prod";
const ODOO_LOGIN = process.env.ODOO_LOGIN || "";
const ODOO_PASSWORD = process.env.ODOO_PASSWORD || "";
const API_TOKEN = process.env.IPAI_API_TOKEN || "";

// Resolve paths
const __dirname = path.dirname(fileURLToPath(import.meta.url));
const WIDGET_PATH = path.join(__dirname, "..", "public", "widget.html");

// Session cache
let sessionUid = null;
let sessionCookies = "";

/**
 * Call Odoo JSON-RPC endpoint
 */
async function odooJsonRpc(endpoint, params, useCookies = false) {
  const headers = {
    "Content-Type": "application/json",
  };

  if (useCookies && sessionCookies) {
    headers["Cookie"] = sessionCookies;
  }

  if (API_TOKEN && endpoint.includes("/api/public/")) {
    headers["Authorization"] = `Bearer ${API_TOKEN}`;
  }

  const payload = {
    jsonrpc: "2.0",
    method: "call",
    params,
    id: Date.now(),
  };

  const res = await fetch(`${ODOO_BASE_URL}${endpoint}`, {
    method: "POST",
    headers,
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    throw new Error(`Odoo HTTP error: ${res.status} ${res.statusText}`);
  }

  // Capture cookies from login response
  const setCookie = res.headers.get("set-cookie");
  if (setCookie) {
    sessionCookies = setCookie.split(",").map((c) => c.split(";")[0]).join("; ");
  }

  const data = await res.json();

  if (data.error) {
    throw new Error(data.error.data?.message || data.error.message || "Odoo RPC error");
  }

  return data.result;
}

/**
 * Authenticate with Odoo
 */
async function odooLogin() {
  if (sessionUid) {
    return sessionUid;
  }

  if (!ODOO_LOGIN || !ODOO_PASSWORD) {
    throw new Error("Odoo credentials not configured (set ODOO_LOGIN and ODOO_PASSWORD)");
  }

  const result = await odooJsonRpc("/web/session/authenticate", {
    db: ODOO_DB,
    login: ODOO_LOGIN,
    password: ODOO_PASSWORD,
  });

  if (!result?.uid) {
    throw new Error("Odoo authentication failed");
  }

  sessionUid = result.uid;
  console.log(`Authenticated as uid=${sessionUid}`);
  return sessionUid;
}

/**
 * Call Odoo API with session auth
 */
async function callOdooApi(endpoint, params) {
  await odooLogin();
  return odooJsonRpc(endpoint, params, true);
}

// Create MCP server
const server = new McpServer({
  name: "ipai-odoo-ai-studio",
  version: "1.0.0",
});

// Register widget resource
let widgetHtml = "";
try {
  widgetHtml = readFileSync(WIDGET_PATH, "utf8");
} catch (e) {
  console.warn("Widget HTML not found, using placeholder");
  widgetHtml = "<html><body><h1>IPAI AI Studio</h1></body></html>";
}

server.resource(
  "ipai-ai-studio-widget",
  "ui://widget/ipai-ai-studio.html",
  async () => ({
    contents: [
      {
        uri: "ui://widget/ipai-ai-studio.html",
        mimeType: "text/html+skybridge",
        text: widgetHtml,
      },
    ],
  })
);

// Tool: Process NLP Command
server.tool(
  "odoo_ai_studio_process_command",
  {
    command: z.string().min(1).describe("Natural language command to process"),
    context: z.record(z.any()).optional().describe("Optional context (current model, etc.)"),
  },
  async ({ command, context }) => {
    try {
      const result = await callOdooApi("/ipai_studio_ai/api/process_command", {
        command,
        context: context || {},
      });

      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(result, null, 2),
          },
        ],
      };
    } catch (error) {
      return {
        content: [
          {
            type: "text",
            text: JSON.stringify({ error: error.message }),
          },
        ],
        isError: true,
      };
    }
  }
);

// Tool: Analyze Command (dry run)
server.tool(
  "odoo_ai_studio_analyze",
  {
    command: z.string().min(1).describe("Command to analyze without executing"),
  },
  async ({ command }) => {
    try {
      const result = await callOdooApi("/ipai_studio_ai/api/analyze", {
        command,
      });

      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(result, null, 2),
          },
        ],
      };
    } catch (error) {
      return {
        content: [
          {
            type: "text",
            text: JSON.stringify({ error: error.message }),
          },
        ],
        isError: true,
      };
    }
  }
);

// Tool: Create Field
server.tool(
  "odoo_ai_studio_create_field",
  {
    model: z.string().describe("Target model (e.g., 'res.partner')"),
    field_name: z.string().describe("Technical field name (e.g., 'x_phone_2')"),
    field_type: z.string().describe("Field type (char, text, integer, etc.)"),
    label: z.string().describe("Human-readable label"),
    required: z.boolean().optional().describe("Is field required"),
  },
  async ({ model, field_name, field_type, label, required }) => {
    try {
      const result = await callOdooApi("/ipai_studio_ai/api/create_field", {
        model,
        field_name,
        field_type,
        label,
        required: required || false,
      });

      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(result, null, 2),
          },
        ],
      };
    } catch (error) {
      return {
        content: [
          {
            type: "text",
            text: JSON.stringify({ error: error.message }),
          },
        ],
        isError: true,
      };
    }
  }
);

// Tool: Execute Query
server.tool(
  "odoo_ai_studio_query",
  {
    query_type: z.enum(["list", "count"]).describe("Query type"),
    model: z.string().describe("Model to query"),
    domain: z.string().optional().describe("Search domain as JSON string"),
    limit: z.number().optional().describe("Result limit"),
  },
  async ({ query_type, model, domain, limit }) => {
    try {
      const result = await callOdooApi("/ipai_studio_ai/api/query", {
        query_type,
        model,
        domain: domain ? JSON.parse(domain) : [],
        limit: limit || 10,
      });

      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(result, null, 2),
          },
        ],
      };
    } catch (error) {
      return {
        content: [
          {
            type: "text",
            text: JSON.stringify({ error: error.message }),
          },
        ],
        isError: true,
      };
    }
  }
);

// Tool: Get Module Info
server.tool(
  "odoo_module_info",
  {
    module_name: z.string().describe("Technical module name"),
  },
  async ({ module_name }) => {
    try {
      const result = await callOdooApi("/ipai_studio_ai/api/module_info", {
        module_name,
      });

      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(result, null, 2),
          },
        ],
      };
    } catch (error) {
      return {
        content: [
          {
            type: "text",
            text: JSON.stringify({ error: error.message }),
          },
        ],
        isError: true,
      };
    }
  }
);

// HTTP server
const httpServer = http.createServer(async (req, res) => {
  // Health check
  if (req.url === "/health") {
    res.writeHead(200, { "Content-Type": "application/json" });
    res.end(JSON.stringify({ status: "ok", server: "ipai-ai-studio-mcp" }));
    return;
  }

  // Serve widget directly
  if (req.url === "/widget" || req.url === "/widget.html") {
    res.writeHead(200, { "Content-Type": "text/html" });
    res.end(widgetHtml);
    return;
  }

  // MCP endpoint
  if (req.url?.startsWith("/mcp")) {
    try {
      const transport = new StreamableHTTPServerTransport({ req, res });
      await server.connect(transport);
    } catch (error) {
      console.error("MCP error:", error);
      res.writeHead(500);
      res.end(JSON.stringify({ error: error.message }));
    }
    return;
  }

  // 404 for everything else
  res.writeHead(404, { "Content-Type": "application/json" });
  res.end(JSON.stringify({ error: "Not found" }));
});

httpServer.listen(PORT, () => {
  console.log(`
╔════════════════════════════════════════════════════════════╗
║  IPAI AI Studio - ChatGPT App MCP Server                   ║
╠════════════════════════════════════════════════════════════╣
║  Server:   http://localhost:${PORT}                           ║
║  MCP:      http://localhost:${PORT}/mcp                       ║
║  Widget:   http://localhost:${PORT}/widget                    ║
║  Health:   http://localhost:${PORT}/health                    ║
╠════════════════════════════════════════════════════════════╣
║  Odoo:     ${ODOO_BASE_URL.padEnd(43)}║
║  Database: ${ODOO_DB.padEnd(43)}║
╚════════════════════════════════════════════════════════════╝
  `);
});
