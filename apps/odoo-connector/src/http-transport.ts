/**
 * Streamable HTTP Transport for the Odoo MCP Connector.
 *
 * Uses @modelcontextprotocol/sdk StreamableHTTPServerTransport
 * which implements the MCP Streamable HTTP protocol that ChatGPT expects.
 *
 * Endpoints:
 *   POST /mcp  — MCP Streamable HTTP (ChatGPT connects here)
 *   GET  /mcp  — SSE stream for server-initiated messages
 *   DELETE /mcp — Session termination
 *
 * ChatGPT connector config:
 *   MCP Server URL: https://<host>/mcp
 *   Auth: No Auth (for testing) or OAuth 2.0 (production)
 */

import express from "express";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { SSEServerTransport } from "@modelcontextprotocol/sdk/server/sse.js";

export interface HttpServerConfig {
  port: number;
  mcpPath: string;
}

export async function startHttpServer(
  config: HttpServerConfig,
  serverFactory: () => McpServer,
) {
  const app = express();

  // Store transports by session
  const transports = new Map<string, SSEServerTransport>();

  // Health endpoint
  app.get("/health", (_req, res) => {
    res.json({ ok: true, transport: "sse", timestamp: new Date().toISOString() });
  });

  // SSE connection endpoint — client connects here for the event stream
  app.get(config.mcpPath, async (req, res) => {
    const transport = new SSEServerTransport(`${config.mcpPath}/message`, res);
    const sessionId = transport.sessionId;
    transports.set(sessionId, transport);

    const server = serverFactory();

    res.on("close", () => {
      transports.delete(sessionId);
    });

    await server.connect(transport);
  });

  // Message endpoint — client sends JSON-RPC messages here
  app.post(`${config.mcpPath}/message`, express.json(), async (req, res) => {
    const sessionId = req.query.sessionId as string;
    const transport = transports.get(sessionId);

    if (!transport) {
      res.status(400).json({ error: "Invalid or missing session. Connect to GET /mcp first." });
      return;
    }

    await transport.handlePostMessage(req, res);
  });

  app.listen(config.port, () => {
    console.log(`[odoo-connector] SSE MCP server on :${config.port}`);
    console.log(`[odoo-connector] SSE endpoint: GET ${config.mcpPath}`);
    console.log(`[odoo-connector] Message endpoint: POST ${config.mcpPath}/message`);
    console.log(`[odoo-connector] Health: GET /health`);
  });
}
