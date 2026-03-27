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
    const { startHttpServer } = await import("./http-transport.js");
    const port = parseInt(process.env.PORT ?? "3100", 10);
    const mcpPath = process.env.MCP_PATH ?? "/mcp";

    // Factory creates a fresh server per session (each gets its own tool set)
    const serverFactory = () => {
      const s = new McpServer({ name: "odoo-connector", version: "0.1.0" });
      registerOdooTools(s, { policy, odoo, authorize });
      return s;
    };

    await startHttpServer({ port, mcpPath }, serverFactory);
  } else {
    const transport = new StdioServerTransport();
    await server.connect(transport);
  }
}

main().catch((err) => {
  console.error("[odoo-connector] fatal:", err);
  process.exit(1);
});
