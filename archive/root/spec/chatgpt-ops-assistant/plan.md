# Implementation Plan — ChatGPT Ops Assistant

> Phased plan for building the `ops-assistant` MCP server and registering it
> as a ChatGPT App via the OpenAI Apps SDK.

## Architecture Overview

```
ChatGPT (OpenAI)
    │
    │ SSE (MCP protocol)
    ▼
┌─────────────────────────┐
│  ops-assistant           │
│  (Supabase Edge Function │
│   or DO droplet)         │
│                          │
│  ┌─────────────────────┐ │
│  │ Tool Router          │ │
│  │ (allowlist enforcer) │ │
│  └──────┬──────┬───────┘ │
│         │      │    │     │
│    odoo.*  plane.*  slack.*│
└─────┬──────┬────────┬────┘
      │      │        │
      ▼      ▼        ▼
   Odoo    Plane    Slack
  XML-RPC  REST     Web API
```

## Phase 1: MCP Server Scaffold

**Goal**: Empty MCP server with SSE transport, health check, tool discovery.

**Deliverables**:
- `supabase/functions/ops-assistant/index.ts` (Deno, SSE handler)
- MCP protocol compliance: `initialize`, `tools/list`, `tools/call`
- Health endpoint: `GET /health` returns `{ status: "ok", version: "1.0.0" }`
- Tool discovery: returns empty tool list initially
- Allowlist loader: reads `chatgpt_app_tool_allowlist.yaml` at startup

**Validation**: `curl /health` returns 200. MCP inspector connects via SSE.

## Phase 2: Odoo Tools

**Goal**: `odoo.search_read`, `odoo.update_partner`, `odoo.update_opportunity`, `odoo.create_activity`.

**Deliverables**:
- Odoo XML-RPC client wrapper (`lib/odoo-rpc.ts`)
- Service user authentication (uid cached per session)
- Field-level allowlist enforcement per tool
- `odoo.search_read`: domain filter, fields, limit, offset
- `odoo.update_partner`: validate fields against allowlist, execute `write()`
- `odoo.update_opportunity`: same pattern for crm.lead
- `odoo.create_activity`: validate model against allowed_models

**Validation**: MCP inspector can call each tool. Audit rows appear in `ops.run_events`.

## Phase 3: Plane Tools

**Goal**: `plane.list_work_items`, `plane.create_work_item`, `plane.update_work_item`, `plane.create_page`, `plane.add_comment`.

**Deliverables**:
- Plane REST client wrapper (`lib/plane-api.ts`)
- Bot Token auth (X-API-Key header)
- Rate limiter: token bucket at 60 req/min
- Request batching for list operations
- All five Plane tools registered and functional

**Validation**: Create work item via MCP, verify in Plane UI.

## Phase 4: Slack Tools

**Goal**: `slack.post_message`, `slack.request_approval`.

**Deliverables**:
- Slack Web API client (`lib/slack-api.ts`)
- `slack.post_message`: channel validation against allowed list
- `slack.request_approval`: interactive message with Block Kit buttons
- Approval callback handler (Slack interactivity endpoint)
- Signing secret verification for inbound Slack payloads

**Validation**: Post message appears in Slack. Approval flow completes end-to-end.

## Phase 5: Auth (OAuth 2.1)

**Goal**: OpenAI Apps SDK OAuth 2.1 with PKCE.

**Deliverables**:
- `/oauth/authorize` endpoint (authorization code flow)
- `/oauth/token` endpoint (code exchange + PKCE verification)
- Token storage in Supabase (encrypted, per-user)
- Refresh token rotation
- Apps SDK manifest registration (app.json or equivalent)

**Validation**: ChatGPT can connect to the app, authenticate, and call tools.

## Phase 6: Approval Workflow Integration

**Goal**: Odoo prod writes blocked until Slack approval received.

**Deliverables**:
- Pre-execution hook in tool router: check `requires_approval`
- Approval request builder: formats change details for Slack message
- Blocking wait with 60-minute timeout
- Approval/rejection callback updates `ops.run_events`
- Timeout handling: cancel action, notify user in ChatGPT

**Validation**: Update partner in prod triggers Slack approval. Approve -> write succeeds. Reject -> write cancelled.

## Phase 7: Cross-System Linking & Audit

**Goal**: `ops.external_identities` population, audit dashboard.

**Deliverables**:
- Link writer: after cross-system operations, write to `ops.external_identities`
- Partial link handling: mark `status: partial` on single-system failure
- Superset dashboard for `ops.run_events` (or Supabase Studio view)
- Error alerting: Slack notification on tool errors

**Validation**: Cross-system operation creates identity link. Dashboard shows tool usage.

## Phase 8: Deploy & Register

**Goal**: Live ChatGPT App in OpenAI marketplace (or team-scoped).

**Deliverables**:
- Deploy MCP server to Supabase Edge Function (prod)
- Register app in OpenAI Apps SDK developer portal
- Configure OAuth redirect URIs
- Team-scoped access (not public marketplace initially)
- Monitoring: uptime check on `/health`

**Validation**: Team member opens ChatGPT, adds Ops Assistant app, authenticates, executes a cross-system query.

## Dependencies

| Dependency | Status | Blocker? |
|------------|--------|----------|
| Supabase Edge Functions (Deno) | Available | No |
| Odoo XML-RPC access | Available (prod) | No |
| Plane API key | Available (vault) | No |
| Slack bot token | Available (vault) | No |
| OpenAI Apps SDK access | Requires signup | Yes (Phase 5+) |
| `ops.external_identities` table | Needs creation | No (Phase 7) |
| `ops.run_events` table | Needs creation | No (Phase 2) |
| `ops.idempotency_keys` table | Needs creation | No (Phase 2) |
