/**
 * HTTP/SSE Transport for the Odoo MCP Connector.
 *
 * Endpoints:
 *   GET  /mcp          — SSE stream (MCP transport)
 *   POST /mcp          — MCP message handler
 *   GET  /mcp/health   — health check (no auth)
 *
 * OAuth endpoints (separate from MCP transport):
 *   GET  /oauth/callback — OAuth redirect URI for Entra code exchange
 *
 * ChatGPT connector config:
 *   MCP Server URL: https://erp.insightpulseai.com/odoo-connector/mcp
 *   Auth: OAuth 2.0 (or none for initial testing)
 */

import http from "node:http";
import { URL } from "node:url";

export interface HttpTransportConfig {
  port: number;
  basePath: string;
}

export function createHttpServer(
  config: HttpTransportConfig,
  handlers: {
    onMcpMessage: (body: unknown) => Promise<unknown>;
    onHealthCheck: () => Promise<{ ok: boolean; version?: string }>;
    onOAuthCallback?: (code: string, state: string) => Promise<{ ok: boolean; error?: string }>;
  },
): http.Server {
  const server = http.createServer(async (req, res) => {
    const url = new URL(req.url ?? "/", `http://${req.headers.host}`);
    const path = url.pathname.replace(/\/$/, "");

    // CORS headers for ChatGPT
    res.setHeader("Access-Control-Allow-Origin", "*");
    res.setHeader("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
    res.setHeader("Access-Control-Allow-Headers", "Content-Type, Authorization");

    if (req.method === "OPTIONS") {
      res.writeHead(204);
      res.end();
      return;
    }

    try {
      // Health check — no auth required
      if (path === `${config.basePath}/health` && req.method === "GET") {
        const health = await handlers.onHealthCheck();
        res.writeHead(200, { "Content-Type": "application/json" });
        res.end(JSON.stringify(health));
        return;
      }

      // MCP message endpoint (POST)
      if (path === config.basePath && req.method === "POST") {
        const body = await readBody(req);
        const parsed = JSON.parse(body);
        const result = await handlers.onMcpMessage(parsed);
        res.writeHead(200, { "Content-Type": "application/json" });
        res.end(JSON.stringify(result));
        return;
      }

      // MCP SSE stream (GET) — for streaming transport
      if (path === config.basePath && req.method === "GET") {
        res.writeHead(200, {
          "Content-Type": "text/event-stream",
          "Cache-Control": "no-cache",
          "Connection": "keep-alive",
        });

        // Send initial connection event
        res.write(`data: ${JSON.stringify({ type: "connection", status: "ok" })}\n\n`);

        // Keep alive
        const keepAlive = setInterval(() => {
          res.write(": keepalive\n\n");
        }, 30000);

        req.on("close", () => {
          clearInterval(keepAlive);
        });

        return;
      }

      // OAuth callback — separate from MCP transport
      if (path === `${config.basePath.replace("/mcp", "")}/oauth/callback` && req.method === "GET") {
        const code = url.searchParams.get("code") ?? "";
        const state = url.searchParams.get("state") ?? "";

        if (!code) {
          res.writeHead(400, { "Content-Type": "application/json" });
          res.end(JSON.stringify({ error: "missing_code" }));
          return;
        }

        if (handlers.onOAuthCallback) {
          const result = await handlers.onOAuthCallback(code, state);
          if (result.ok) {
            res.writeHead(200, { "Content-Type": "text/html" });
            res.end("<html><body><h1>Connected</h1><p>You can close this window.</p></body></html>");
          } else {
            res.writeHead(401, { "Content-Type": "application/json" });
            res.end(JSON.stringify({ error: result.error }));
          }
        } else {
          res.writeHead(501, { "Content-Type": "application/json" });
          res.end(JSON.stringify({ error: "oauth_not_configured" }));
        }

        return;
      }

      // 404
      res.writeHead(404, { "Content-Type": "application/json" });
      res.end(JSON.stringify({ error: "not_found", path }));
    } catch (err) {
      console.error("[http-transport] error:", err);
      res.writeHead(500, { "Content-Type": "application/json" });
      res.end(JSON.stringify({ error: "internal_error" }));
    }
  });

  return server;
}

function readBody(req: http.IncomingMessage): Promise<string> {
  return new Promise((resolve, reject) => {
    const chunks: Buffer[] = [];
    req.on("data", (chunk) => chunks.push(chunk));
    req.on("end", () => resolve(Buffer.concat(chunks).toString("utf8")));
    req.on("error", reject);
  });
}
