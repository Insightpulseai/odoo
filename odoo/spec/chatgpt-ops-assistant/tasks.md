# Tasks — ChatGPT Ops Assistant

> Task breakdown for implementing the ops-assistant MCP server and ChatGPT App.
> Each task maps to a phase in `plan.md`.

## Phase 1: MCP Server Scaffold

- [x] Create `supabase/functions/ops-assistant/index.ts` with Deno SSE handler
- [x] Implement MCP protocol handlers: `initialize`, `tools/list`, `tools/call`
- [x] Add `GET /health` endpoint returning `{ status: "ok", version: "1.0.0" }`
- [x] Implement allowlist loader (parse YAML from bundled config or vault)
- [x] Add tool router with deny-by-default enforcement
- [x] Add audit logger (writes to `ops.run_events`)
- [ ] Create Supabase migration: `ops.run_events` table
- [ ] Create Supabase migration: `ops.idempotency_keys` table
- [ ] Add idempotency key checker middleware
- [ ] Deploy to Supabase Edge Functions (stage environment)
- [ ] Validate: MCP inspector connects, health returns 200, empty tool list

## Phase 2: Odoo Tools

- [ ] Create `lib/odoo-rpc.ts` — XML-RPC client wrapper for Odoo
- [ ] Implement service user auth (`authenticate` → cache uid)
- [ ] Implement `odoo.search_read` tool (domain, fields, model, limit)
- [ ] Implement `odoo.update_partner` tool with field allowlist enforcement
- [ ] Implement `odoo.update_opportunity` tool with field allowlist enforcement
- [ ] Implement `odoo.create_activity` tool with model allowlist enforcement
- [ ] Add blocked-field rejection logic (reject entire request on blocked field)
- [ ] Create Odoo service user `odoo_chatgpt_rpc` with restricted access group
- [ ] Write unit tests for field allowlist enforcement
- [ ] Validate: MCP inspector calls each Odoo tool successfully

## Phase 3: Plane Tools

- [x] Create `lib/plane-api.ts` — Plane REST API client wrapper
- [x] Implement token-bucket rate limiter (60 req/min)
- [x] Implement `plane.list_work_items` tool
- [x] Implement `plane.create_work_item` tool
- [x] Implement `plane.update_work_item` tool
- [x] Implement `plane.create_page` tool
- [x] Implement `plane.add_comment` tool
- [ ] Add request batching for list operations
- [ ] Write unit tests for rate limiter
- [ ] Validate: create work item via MCP, verify in Plane UI

## Phase 4: Slack Tools

- [ ] Create `lib/slack-api.ts` — Slack Web API client wrapper
- [ ] Implement signing secret verification for inbound payloads
- [ ] Implement `slack.post_message` tool with channel allowlist
- [ ] Implement `slack.request_approval` tool with Block Kit interactive message
- [ ] Create approval callback handler endpoint
- [ ] Implement approval state machine (pending → approved | rejected | timeout)
- [ ] Add 60-minute timeout with auto-cancellation
- [ ] Write unit tests for signing verification
- [ ] Validate: post message, then full approval flow end-to-end

## Phase 5: Auth (OAuth 2.1)

- [ ] Implement `/oauth/authorize` endpoint (authorization code + PKCE)
- [ ] Implement `/oauth/token` endpoint (code exchange, PKCE verify)
- [ ] Create Supabase migration: `ops.oauth_sessions` table
- [ ] Implement refresh token rotation
- [ ] Create Apps SDK app manifest (app.json)
- [ ] Register app in OpenAI developer portal
- [ ] Configure OAuth redirect URIs in OpenAI dashboard
- [ ] Validate: ChatGPT connects, authenticates, sees tool list

## Phase 6: Approval Workflow Integration

- [ ] Add pre-execution hook in tool router for `requires_approval` check
- [ ] Build approval request formatter (tool name, record, field changes)
- [ ] Implement blocking wait (SSE keeps connection, polls for approval)
- [ ] Handle approval callback → resume tool execution
- [ ] Handle rejection callback → cancel and notify user
- [ ] Handle timeout → cancel, log, notify user
- [ ] Write integration test: approve flow, reject flow, timeout flow
- [ ] Validate: end-to-end Odoo write with Slack approval in prod config

## Phase 7: Cross-System Linking & Audit

- [ ] Create Supabase migration: `ops.external_identities` table
- [ ] Implement link writer in tool router (post-execution hook)
- [ ] Handle partial links (one system succeeds, other fails)
- [ ] Add Slack notification for partial link failures
- [ ] Create Superset dashboard for `ops.run_events` audit data
- [ ] Add error alerting: Slack notification on tool errors
- [ ] Validate: cross-system operation creates identity link

## Phase 8: Deploy & Register

- [ ] Deploy MCP server to Supabase Edge Function (prod)
- [ ] Configure production secrets in Supabase Vault
- [ ] Register ChatGPT App in OpenAI marketplace (team-scoped)
- [ ] Configure OAuth redirect URIs for prod
- [ ] Set up uptime monitoring on `/health`
- [ ] Create runbook: `docs/runbooks/OPS_ASSISTANT_RUNBOOK.md`
- [ ] Validate: team member uses app in ChatGPT for real operation
- [ ] Document: update `ssot/integrations/_index.yaml` with app entry

## Acceptance Criteria

- [ ] All 3 tool families functional (odoo.*, plane.*, slack.*)
- [ ] Deny-by-default enforced (unknown tools rejected, logged)
- [ ] Field-level access control on Odoo writes
- [ ] Slack approval flow works end-to-end for prod Odoo writes
- [ ] All tool calls audited to `ops.run_events`
- [ ] Idempotency keys prevent duplicate writes
- [ ] Cross-system links written to `ops.external_identities`
- [ ] OAuth 2.1 + PKCE authentication working
- [ ] Rate limiting enforced (60 req/min global, 60 req/min Plane)
- [ ] Health endpoint returns 200 with version
