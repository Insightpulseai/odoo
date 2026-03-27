import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { loadPolicy } from "./policy.js";
import { OdooClient } from "./odoo-client.js";
import { registerOdooTools } from "./register-tools.js";

type SessionContext = {
  user?: {
    id: string;
    scopes: string[];
  };
};

function requireEnv(name: string): string {
  const value = process.env[name];
  if (!value) throw new Error(`Missing required environment variable: ${name}`);
  return value;
}

async function authorize(
  ctx: unknown,
  requiredScope: string,
): Promise<
  | { ok: true }
  | { ok: false; error: string; errorDescription: string }
> {
  const session = (ctx ?? {}) as SessionContext;

  if (!session.user) {
    return {
      ok: false,
      error: "invalid_token",
      errorDescription: "Sign-in required.",
    };
  }

  if (!session.user.scopes.includes(requiredScope)) {
    return {
      ok: false,
      error: "insufficient_scope",
      errorDescription: `Missing required scope: ${requiredScope}`,
    };
  }

  return { ok: true };
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

  const transport = new StdioServerTransport();
  await server.connect(transport);
}

main().catch((err) => {
  console.error("[odoo-connector] fatal:", err);
  process.exit(1);
});
