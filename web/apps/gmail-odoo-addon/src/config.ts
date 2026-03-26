/**
 * InsightPulseAI Gmail Add-on — Configuration
 *
 * All Odoo bridge endpoints are defined here.
 * The add-on communicates exclusively through these paths.
 */

const ODOO_BASE_URL = "https://erp.insightpulseai.com";

const API_PATHS = {
  session: "/ipai/mail_plugin/session",
  context: "/ipai/mail_plugin/context",
  createLead: "/ipai/mail_plugin/actions/create_lead",
  createTicket: "/ipai/mail_plugin/actions/create_ticket",
  logNote: "/ipai/mail_plugin/actions/log_note",
} as const;

/**
 * Build a full URL for an API path.
 */
function apiUrl(path: string): string {
  return `${ODOO_BASE_URL}${path}`;
}
