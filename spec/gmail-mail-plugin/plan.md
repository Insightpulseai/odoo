# Implementation Plan: Gmail Mail Plugin

## Phase 1 — Bridge Endpoints + Gmail Card Stubs

**Goal**: Working HTTP endpoints on Odoo; placeholder cards in Gmail.

1. Write `ipai_mail_plugin_bridge` Odoo module with session model and controller stubs.
2. Install module on `odoo_dev` and verify endpoints return valid JSON-RPC responses.
3. Create Gmail Apps Script project with `appsscript.json` manifest.
4. Implement `homepage()` returning a static card.
5. Implement `onGmailMessage()` returning a placeholder card.

**Verification**: `curl -X POST https://erp.insightpulseai.com/ipai/mail_plugin/session` returns JSON-RPC envelope.

## Phase 2 — Auth Flow + Contact Lookup

**Goal**: End-to-end authentication and contact display.

1. Implement `auth.ts` — login card, `getOdooSession()`, `fetchBridge()`.
2. Implement `config.ts` with endpoint URLs.
3. Wire `onGmailMessage()` to call `/context` and render partner data.
4. Handle unauthenticated state (show login card).
5. Handle no-match state (show "no contact" card with Create Lead button).

**Verification**: Open an email from a known Odoo contact; sidebar shows name, company, phone.

## Phase 3 — Action Endpoints

**Goal**: Create leads, tickets, and log notes from Gmail.

1. Implement `actions.ts` — `createLead`, `createTicket`, `logToChatter`, `openInOdoo`.
2. Wire action buttons in the context card.
3. Add notification cards for success/failure states.
4. Add server-side logging for all action endpoints.

**Verification**: Click "Create Lead" in Gmail sidebar; verify CRM lead exists in Odoo.

## Phase 4 — Testing + Org Deployment

**Goal**: Production-ready deployment to the Google Workspace org.

1. Test all endpoints against `odoo_dev` with disposable test data.
2. Test add-on in Gmail with multiple user accounts.
3. Test error scenarios: expired token, deleted partner, network failure.
4. Deploy Apps Script project to org (not marketplace).
5. Configure URL whitelist and OAuth consent screen.
6. Document admin setup steps for Workspace admins.

**Verification**: Two org users can independently authenticate and use the add-on.

## Dependencies

| Dependency | Status |
|------------|--------|
| `crm` module installed on ERP | Required |
| `project` module installed on ERP | Required |
| `mail` module installed on ERP | Required (base) |
| Google Workspace admin access | Required for org deployment |
| Azure Front Door passes `/ipai/mail_plugin/*` routes | Required |
