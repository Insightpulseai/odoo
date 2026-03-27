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
import { randomUUID } from "node:crypto";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/streamableHttp.js";

export interface HttpServerConfig {
  port: number;
  mcpPath: string;
}

export async function startHttpServer(
  config: HttpServerConfig,
  serverFactory: () => McpServer,
) {
  const app = express();

  // Store transports by session ID
  const transports = new Map<string, StreamableHTTPServerTransport>();

  // Health endpoint
  app.get("/health", (_req, res) => {
    res.json({ ok: true, transport: "streamable-http", timestamp: new Date().toISOString() });
  });

  // MCP Streamable HTTP endpoint
  app.post(config.mcpPath, async (req, res) => {
    const sessionId = req.headers["mcp-session-id"] as string | undefined;
    let transport: StreamableHTTPServerTransport;

    if (sessionId && transports.has(sessionId)) {
      transport = transports.get(sessionId)!;
    } else {
      // New session — create transport and connect server
      const newSessionId = randomUUID();
      transport = new StreamableHTTPServerTransport({
        sessionId: newSessionId,
      });
      transports.set(newSessionId, transport);

      const server = serverFactory();
      await server.connect(transport);

      // Clean up on close
      transport.onclose = () => {
        transports.delete(newSessionId);
      };
    }

    await transport.handleRequest(req, res, req.body);
  });

  // SSE stream for server-initiated messages
  app.get(config.mcpPath, async (req, res) => {
    const sessionId = req.headers["mcp-session-id"] as string | undefined;
    if (!sessionId || !transports.has(sessionId)) {
      res.status(400).json({ error: "Invalid or missing session ID" });
      return;
    }
    const transport = transports.get(sessionId)!;
    await transport.handleRequest(req, res);
  });

  // Session termination
  app.delete(config.mcpPath, async (req, res) => {
    const sessionId = req.headers["mcp-session-id"] as string | undefined;
    if (sessionId && transports.has(sessionId)) {
      const transport = transports.get(sessionId)!;
      await transport.close();
      transports.delete(sessionId);
    }
    res.status(200).json({ ok: true });
  });

  app.listen(config.port, () => {
    console.log(`[odoo-connector] Streamable HTTP server on :${config.port}`);
    console.log(`[odoo-connector] MCP endpoint: ${config.mcpPath}`);
    console.log(`[odoo-connector] Health: /health`);
  });
}
