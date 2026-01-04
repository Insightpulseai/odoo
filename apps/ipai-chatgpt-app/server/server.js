/**
 * IPAI ChatGPT App - MCP Server
 *
 * Serves:
 * - Resource: ui://ipai/widget.html (text/html+skybridge)
 * - Tool: ipai_ping with _meta.openai/outputTemplate
 *
 * Environment:
 * - PORT: HTTP port (default: 8787)
 * - MCP_PATH: MCP endpoint path (default: /mcp)
 */

import { createServer } from "node:http";
import { readFileSync, existsSync } from "node:fs";
import { resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/streamableHttp.js";

const __dirname = dirname(fileURLToPath(import.meta.url));
const MCP_PATH = process.env.MCP_PATH || "/mcp";
const port = process.env.PORT ? Number(process.env.PORT) : 8787;

// Built widget HTML (single-file, inlined by vite-plugin-singlefile)
const widgetHtmlPath = resolve(__dirname, "../web/dist/index.html");

function getWidgetHtml() {
  if (!existsSync(widgetHtmlPath)) {
    return `<!DOCTYPE html>
<html>
<head><title>IPAI Widget</title></head>
<body>
<div style="padding:20px;font-family:system-ui;color:#888;">
Widget not built. Run: pnpm -C apps/ipai-chatgpt-app/web build
</div>
</body>
</html>`;
  }
  return readFileSync(widgetHtmlPath, "utf8");
}

function reply(structuredContent, message) {
  return {
    content: message ? [{ type: "text", text: message }] : [],
    structuredContent,
  };
}

function createIpaiServer() {
  const server = new McpServer({ name: "ipai-chatgpt-app", version: "0.1.0" });

  // Resource: UI bundle
  server.resource(
    "ipai-widget",
    "ui://ipai/widget.html",
    async () => ({
      contents: [
        {
          uri: "ui://ipai/widget.html",
          mimeType: "text/html+skybridge",
          text: getWidgetHtml(),
        },
      ],
    })
  );

  // Tool: ping (renders widget)
  server.tool(
    "ipai_ping",
    {
      title: "IPAI Ping",
      description: "Health ping. Returns server time and renders IPAI widget UI.",
    },
    async () => {
      return reply(
        { message: "pong", server_time: new Date().toISOString() },
        "pong"
      );
    }
  );

  return server;
}

const mcpServer = createIpaiServer();

const httpServer = createServer(async (req, res) => {
  // Health check
  if (req.method === "GET" && req.url === "/") {
    res.writeHead(200, { "content-type": "application/json" });
    res.end(JSON.stringify({ status: "ok", service: "ipai-chatgpt-app-server" }));
    return;
  }

  // CORS headers
  res.setHeader("access-control-allow-origin", "*");
  res.setHeader("access-control-allow-methods", "GET,POST,OPTIONS");
  res.setHeader("access-control-allow-headers", "content-type, authorization");

  if (req.method === "OPTIONS") {
    res.writeHead(204);
    res.end();
    return;
  }

  if (!req.url?.startsWith(MCP_PATH)) {
    res.writeHead(404, { "content-type": "application/json" });
    res.end(JSON.stringify({ error: "not found" }));
    return;
  }

  try {
    const transport = new StreamableHTTPServerTransport({ path: MCP_PATH });
    await mcpServer.connect(transport);
    await transport.handleRequest(req, res);
  } catch (err) {
    console.error("MCP request error:", err);
    if (!res.headersSent) {
      res.writeHead(500, { "content-type": "application/json" });
      res.end(JSON.stringify({ error: "internal error" }));
    }
  }
});

httpServer.listen(port, () => {
  console.log(`IPAI MCP server listening on http://localhost:${port}${MCP_PATH}`);
  console.log(`Health: http://localhost:${port}/`);
  console.log(`Widget path: ${widgetHtmlPath}`);
});
