# Tasks: Gmail Mail Plugin

## Phase 1 — Bridge Endpoints + Gmail Card Stubs

- [ ] Create `ipai_mail_plugin_bridge` module skeleton (`__manifest__.py`, `__init__.py`)
- [ ] Create `ipai.mail.plugin.session` model with token hash storage
- [ ] Create `ir.model.access.csv` for session model
- [ ] Implement `/ipai/mail_plugin/session` endpoint (auth)
- [ ] Implement `/ipai/mail_plugin/context` endpoint (contact lookup)
- [ ] Implement `/ipai/mail_plugin/actions/create_lead` endpoint
- [ ] Implement `/ipai/mail_plugin/actions/create_ticket` endpoint
- [ ] Implement `/ipai/mail_plugin/actions/log_note` endpoint
- [ ] Install module on `odoo_dev` and verify HTTP responses
- [ ] Create Apps Script project with `appsscript.json`
- [ ] Implement `homepage()` static card
- [ ] Implement `onGmailMessage()` placeholder card

## Phase 2 — Auth Flow + Contact Lookup

- [ ] Implement `config.ts` with ODOO_BASE_URL and API paths
- [ ] Implement `auth.ts` — `getOdooSession()`, `authenticate()`, `fetchBridge()`
- [ ] Implement `loginCard()` with email + API key form
- [ ] Implement `handleLogin()` form submission handler
- [ ] Wire `onGmailMessage()` to call bridge `/context` endpoint
- [ ] Render partner info (name, company, phone) in context card
- [ ] Render related leads in context card
- [ ] Render related tasks/tickets in context card
- [ ] Handle unauthenticated state (redirect to login card)
- [ ] Handle no-match state (show create lead option)

## Phase 3 — Action Endpoints

- [ ] Implement `createLead()` action handler
- [ ] Implement `createTicket()` action handler
- [ ] Implement `logToChatter()` action handler
- [ ] Implement `openInOdoo()` with OpenLink
- [ ] Wire action buttons in context card
- [ ] Add success/failure notification cards
- [ ] Add server-side logging for all bridge actions

## Phase 4 — Testing + Org Deployment

- [ ] Test session endpoint with valid/invalid credentials
- [ ] Test context endpoint with known/unknown email addresses
- [ ] Test create_lead with and without existing partner
- [ ] Test create_ticket with and without existing partner
- [ ] Test log_note with valid/invalid partner_id
- [ ] Test expired token handling
- [ ] Test add-on with multiple Gmail accounts
- [ ] Deploy Apps Script to Google Workspace org
- [ ] Configure Apps Script URL whitelist
- [ ] Verify Azure Front Door routes `/ipai/mail_plugin/*` to Odoo
- [ ] Document admin setup for Workspace deployment
