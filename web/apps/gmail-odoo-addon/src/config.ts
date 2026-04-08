/**
 * InsightPulseAI Gmail Add-on — Configuration
 *
 * Tenant config, auth provider registry, and Odoo bridge endpoints.
 * The add-on communicates exclusively through these paths.
 *
 * Auth model:
 *   /web/login           = browser login page (renders OAuth provider buttons natively)
 *   /auth_oauth/signin   = OAuth CALLBACK endpoint (provider redirects back here)
 *   /ipai/mail_plugin/*  = add-on bridge API (session exchange, context, actions)
 *
 * The add-on NEVER opens /auth_oauth/signin directly. That is callback-only.
 */

type OdooAuthProvider = "microsoft_entra_oauth" | "google_oauth" | "local_odoo";

interface TenantConfig {
  tenantId: string;
  displayName: string;
  odooBaseUrl: string;
  authProviders: OdooAuthProvider[];
  defaultAuthProvider: OdooAuthProvider;
}

interface SessionSummary {
  connected: boolean;
  provider: OdooAuthProvider | null;
  userEmail: string | null;
  tenantId: string;
  tenantDisplayName: string;
  expiresAt: string | null;
}

const TENANT_CONFIG: TenantConfig = {
  tenantId: "insightpulseai",
  displayName: "InsightPulseAI ERP",
  odooBaseUrl: "https://erp.insightpulseai.com",
  authProviders: [
    "microsoft_entra_oauth",
    "google_oauth",
    "local_odoo",
  ],
  defaultAuthProvider: "microsoft_entra_oauth",
};

const ODOO_BASE_URL = TENANT_CONFIG.odooBaseUrl;

const API_PATHS = {
  session: "/ipai/mail_plugin/session",
  providerSession: "/ipai/mail_plugin/provider_session",
  context: "/ipai/mail_plugin/context",
  createLead: "/ipai/mail_plugin/actions/create_lead",
  createTicket: "/ipai/mail_plugin/actions/create_ticket",
  logNote: "/ipai/mail_plugin/actions/log_note",
} as const;

const PROVIDER_LABELS: Record<OdooAuthProvider, string> = {
  microsoft_entra_oauth: "Continue with Microsoft",
  google_oauth: "Continue with Google",
  local_odoo: "Use API Key (Advanced)",
};

const PROVIDER_DISPLAY_NAMES: Record<OdooAuthProvider, string> = {
  microsoft_entra_oauth: "Microsoft",
  google_oauth: "Google",
  local_odoo: "API key (advanced)",
};

// Provider start paths — these open the Odoo login page, NOT the OAuth callback.
// /auth_oauth/signin is the CALLBACK endpoint (Google/Entra redirects back here).
// The login page at /web/login renders the OAuth provider buttons natively.
const PROVIDER_AUTH_PATHS: Record<Exclude<OdooAuthProvider, "local_odoo">, string> = {
  microsoft_entra_oauth: "/web/login",
  google_oauth: "/web/login",
};

const AUTH_STATE_TTL_MS = 10 * 60 * 1000; // 10 minutes

/**
 * Build a full URL for an API path.
 */
function apiUrl(path: string): string {
  return `${ODOO_BASE_URL}${path}`;
}
