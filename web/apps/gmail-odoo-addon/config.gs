/**
 * InsightPulseAI Gmail Add-on — Configuration
 *
 * Tenant config, auth provider registry, and Odoo bridge endpoints.
 * The add-on communicates exclusively through these paths.
 */

var TENANT_CONFIG = {
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

var ODOO_BASE_URL = TENANT_CONFIG.odooBaseUrl;

var API_PATHS = {
  session: "/ipai/mail_plugin/session",
  providerSession: "/ipai/mail_plugin/provider_session",
  context: "/ipai/mail_plugin/context",
  createLead: "/ipai/mail_plugin/actions/create_lead",
  createTicket: "/ipai/mail_plugin/actions/create_ticket",
  logNote: "/ipai/mail_plugin/actions/log_note",
};

var PROVIDER_LABELS = {
  microsoft_entra_oauth: "Continue with Microsoft",
  google_oauth: "Continue with Google",
  local_odoo: "Use API Key (Advanced)",
};

var PROVIDER_DISPLAY_NAMES = {
  microsoft_entra_oauth: "Microsoft",
  google_oauth: "Google",
  local_odoo: "API key (advanced)",
};

// Provider start paths — these open the Odoo login page, NOT the OAuth callback.
// /auth_oauth/signin is the CALLBACK endpoint (Google/Entra redirects back here).
// The login page at /web/login renders the OAuth provider buttons natively.
var PROVIDER_AUTH_PATHS = {
  microsoft_entra_oauth: "/web/login",
  google_oauth: "/web/login",
};

var AUTH_STATE_TTL_MS = 10 * 60 * 1000; // 10 minutes

/**
 * Build a full URL for an API path.
 */
function apiUrl(path) {
  return ODOO_BASE_URL + path;
}
