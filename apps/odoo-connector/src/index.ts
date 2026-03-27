import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { loadPolicy } from "./policy.js";
import { OdooClient } from "./odoo-client.js";
import { registerOdooTools } from "./register-tools.js";
import {
  buildEntraConfig,
  validateToken,
  buildAuthenticatedUser,
  type AuthenticatedUser,
} from "./auth/entra-oauth.js";

type SessionContext = {
  user?: AuthenticatedUser;
  accessToken?: string;
};

function requireEnv(name: string): string {
  const value = process.env[name];
  if (!value) throw new Error(`Missing required environment variable: ${name}`);
  return value;
}

/**
 * Authorize a tool call against the user's Entra-derived scopes.
 *
 * Flow:
 *   1. Extract access token from session context
 *   2. Validate token against Entra (issuer, audience, expiry)
 *   3. Extract odoo.* scopes from token claims
 *   4. Check if required scope is present
 *   5. Return ok or error with OAuth challenge metadata
 */
const entraConfig = buildEntraConfig();

async function authorize(
  ctx: unknown,
  requiredScope: string,
): Promise<
  | { ok: true }
  | { ok: false; error: string; errorDescription: string }
> {
  const session = (ctx ?? {}) as SessionContext;

  // If we already have a validated user in context, check scopes
  if (session.user) {
    if (!session.user.scopes.includes(requiredScope)) {
      return {
        ok: false,
        error: "insufficient_scope",
        errorDescription: `Missing required scope: ${requiredScope}`,
      };
    }
    return { ok: true };
  }

  // Try to validate from access token
  if (session.accessToken) {
    const claims = validateToken(entraConfig, session.accessToken);
    if (!claims) {
      return {
        ok: false,
        error: "invalid_token",
        errorDescription: "Token validation failed. Sign in again.",
      };
    }

    const user = buildAuthenticatedUser(claims);
    // Cache validated user back into session
    (session as any).user = user;

    if (!user.scopes.includes(requiredScope)) {
      return {
        ok: false,
        error: "insufficient_scope",
        errorDescription: `Missing required scope: ${requiredScope}`,
      };
    }

    return { ok: true };
  }

  // No token at all
  return {
    ok: false,
    error: "invalid_token",
    errorDescription: "Sign-in required.",
  };
}

async function main() {
  const policy = loadPolicy();

  const odoo = new OdooClient({
    baseUrl: requireEnv("ODOO_BASE_URL"),
    apiKey: requireEnv("ODOO_API_KEY"),
    database: process.env.ODOO_DATABASE,
    userAgent: "odoo-connector/1.0",
  });

  const server = new McpServer({
    name: "odoo-connector",
    version: "0.1.0",
  });

  registerOdooTools(server, {
    policy,
    odoo,
    authorize,
  });

  const mode = process.env.TRANSPORT ?? "stdio";

  if (mode === "http") {
    const { createHttpServer } = await import("./http-transport.js");
    const port = parseInt(process.env.PORT ?? "3100", 10);
    const basePath = process.env.MCP_BASE_PATH ?? "/odoo-connector/mcp";

    const httpServer = createHttpServer(
      { port, basePath },
      {
        onMcpMessage: async (body) => {
          // Route MCP JSON-RPC messages through the server
          // Full MCP HTTP transport wiring requires SDK streamable-http adapter
          return { jsonrpc: "2.0", result: { ok: true }, id: (body as any)?.id };
        },
        onHealthCheck: async () => {
          return odoo.ping();
        },
        onOAuthCallback: async (code, state) => {
          try {
            const { exchangeCodeForTokens } = await import("./auth/entra-oauth.js");
            const tokens = await exchangeCodeForTokens(entraConfig, code);
            return { ok: true };
          } catch (err) {
            return { ok: false, error: String(err) };
          }
        },
      },
    );

    httpServer.listen(port, () => {
      console.log(`[odoo-connector] HTTP server listening on :${port}`);
      console.log(`[odoo-connector] MCP endpoint: ${basePath}`);
      console.log(`[odoo-connector] Health: ${basePath}/health`);
      console.log(`[odoo-connector] OAuth callback: /odoo-connector/oauth/callback`);
    });
  } else {
    const transport = new StdioServerTransport();
    await server.connect(transport);
  }
}

main().catch((err) => {
  console.error("[odoo-connector] fatal:", err);
  process.exit(1);
});
