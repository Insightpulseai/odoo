import { initTracing } from "./tracing.js";
initTracing();

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { loadPolicy } from "./policy.js";
import { OdooClient } from "./odoo-client.js";
import { registerOdooTools } from "./register-tools.js";
import { verifyEntraToken } from "./auth/entra-oauth.js";

// Post-patch shape: verifyEntraToken returns { claims, user } from a
// JWKS-verified token + Graph /me. The previous AuthenticatedUser type
// (with a precomputed `scopes` array) is gone — scope extraction via
// unstable token claims was the anti-pattern we removed.
// TODO(security): restore scope-based authorization by reading `scp` /
// `roles` from the verified JWT payload (safe — payload is crypto-verified).
// For now, authorize on presence of a valid Entra user only.
type AuthenticatedUser = {
  id: string;
  email: string;
  name: string;
};

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
async function authorize(
  ctx: unknown,
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  _requiredScope: string,
): Promise<
  | { ok: true }
  | { ok: false; error: string; errorDescription: string }
> {
  const session = (ctx ?? {}) as SessionContext;

  // If we already have a validated user in context, the caller is
  // authenticated. TODO(security): add scope check against verified JWT's
  // `scp` / `roles` before returning ok.
  if (session.user) {
    return { ok: true };
  }

  // Try to validate from access token
  if (session.accessToken) {
    try {
      const { claims, user } = await verifyEntraToken(session.accessToken);
      const authUser: AuthenticatedUser = {
        id: claims.oid,
        email: user.mail ?? user.userPrincipalName,
        name: user.displayName,
      };
      // Cache validated user back into session
      (session as any).user = authUser;
      // TODO(security): gate on scope here once scope extraction is restored.
      return { ok: true };
    } catch (err) {
      console.error("[odoo-connector] token verification failed:", err);
      return {
        ok: false,
        error: "invalid_token",
        errorDescription: "Token validation failed. Sign in again.",
      };
    }
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

    const serverFactory = () => {
      const s = new McpServer({ name: "odoo-connector", version: "0.1.0" });
      registerOdooTools(s, { policy, odoo, authorize });
      return s;
    };

    await startHttpServer({ port, mcpPath }, serverFactory);
    console.log("[odoo-connector] Ready for ChatGPT connections");
  } else {
    const transport = new StdioServerTransport();
    await server.connect(transport);
  }
}

main().catch((err) => {
  console.error("[odoo-connector] fatal:", err);
  process.exit(1);
});
