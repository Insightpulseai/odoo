/**
 * Streamable HTTP Transport for the Odoo MCP Connector.
 *
 * Uses @modelcontextprotocol/sdk StreamableHTTPServerTransport (v1.27+)
 * which implements the MCP Streamable HTTP protocol that ChatGPT expects.
 *
 * Endpoints:
 *   POST /mcp    — MCP messages (ChatGPT connects here)
 *   GET  /mcp    — SSE stream for server-initiated messages
 *   DELETE /mcp  — Session termination
 *   GET /health  — Health check
 */

import express from "express";
import { randomUUID } from "node:crypto";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/streamableHttp.js";
import { isInitializeRequest } from "@modelcontextprotocol/sdk/types.js";

export interface HttpServerConfig {
  port: number;
  mcpPath: string;
}

export async function startHttpServer(
  config: HttpServerConfig,
  serverFactory: () => McpServer,
) {
  const app = express();
  app.use(express.json());

  // Store transports by session ID
  const transports = new Map<string, StreamableHTTPServerTransport>();

  // Health endpoint
  app.get("/health", (_req, res) => {
    res.json({ ok: true, transport: "streamable-http", timestamp: new Date().toISOString() });
  });

  // MCP Streamable HTTP — POST handles messages
  app.post(config.mcpPath, async (req, res) => {
    const sessionId = req.headers["mcp-session-id"] as string | undefined;
    let transport: StreamableHTTPServerTransport;

    if (sessionId && transports.has(sessionId)) {
      // Existing session
      transport = transports.get(sessionId)!;
    } else if (isInitializeRequest(req.body)) {
      // New session on initialize (with or without session ID header)
      const newId = randomUUID();
      transport = new StreamableHTTPServerTransport({
        sessionIdGenerator: () => newId,
      });

      transports.set(newId, transport);

      const server = serverFactory();
      await server.connect(transport);

      transport.onclose = () => {
        transports.delete(newId);
      };
    } else {
      res.status(400).json({
        jsonrpc: "2.0",
        error: { code: -32000, message: "Bad request: missing mcp-session-id header. Send initialize first." },
        id: (req.body as any)?.id ?? null,
      });
      return;
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
    console.log(`[odoo-connector] Streamable HTTP MCP server on :${config.port}`);
    console.log(`[odoo-connector] MCP endpoint: POST ${config.mcpPath}`);
    console.log(`[odoo-connector] Health: GET /health`);
  });
}
