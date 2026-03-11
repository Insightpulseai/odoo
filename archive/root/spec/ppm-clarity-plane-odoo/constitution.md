# PPM Clarity Constitution

> Non-negotiable governance rules for the Plane.so + Odoo integration.
> Violation of any principle blocks merge to `main`.

---

## Scope

**PPM Clarity** synchronises planning truth (Plane.so, self-hosted) with
operational truth (Odoo 19 CE) through a deterministic, auditable contract
stored in the Supabase `ops` schema.

---

## Core Principles

### P1: Three-Layer Contract

| Layer | System | Truth Domain |
|-------|--------|-------------|
| Planning | Plane.so (self-hosted) | Templates, states, labels, priorities, cycles |
| Operational | Odoo 19 CE | Tasks, timesheets, costs, assignments, chatter |
| Reconciliation | Supabase `ops` | Bidirectional ID mapping, event ledger, drift detection |

No layer may claim authority over another layer's fields.

### P2: Plane MCP Server First

All programmatic access to Plane MUST use the official MCP server.

**Self-Hosted Configuration** (Stdio transport):
```bash
PLANE_API_KEY=<workspace-api-key>
PLANE_WORKSPACE_SLUG=insightpulseai
PLANE_BASE_URL=https://plane-api.insightpulseai.com
```

**MCP Server** (Claude Code):
```json
{
  "plane": {
    "command": "uvx",
    "args": ["plane-mcp-server"],
    "env": {
      "PLANE_API_KEY": "$PLANE_API_KEY",
      "PLANE_WORKSPACE_SLUG": "$PLANE_WORKSPACE_SLUG",
      "PLANE_BASE_URL": "https://plane-api.insightpulseai.com"
    }
  }
}
```

Direct REST calls are allowed only when MCP tools do not cover the use case.

### P3: Field Ownership (No Ping-Pong)

| Owner | Fields |
|-------|--------|
| **Plane** | title, description, priority, labels, cycle, state |
| **Odoo** | assigned users, timesheets, costs, billable flags, attachments, chatter |

A system may only **write** fields it owns. Cross-ownership writes are
**forbidden** except during nightly reconciliation with explicit conflict
resolution.

### P4: Webhook-Driven Events

Plane webhooks deliver events to n8n via HMAC-SHA256 signed payloads:

- **Endpoint**: `https://n8n.insightpulseai.com/webhook/ppm-clarity/plane`
- **Signature header**: `X-Plane-Signature`
- **Validation**: Reject any payload that fails HMAC verification

### P5: Idempotency Enforcement

Every sync operation MUST include an `idempotency_key` (format:
`{source}:{event_type}:{entity_id}:{timestamp}`). The `ops.work_item_events`
table enforces UNIQUE on this column. Duplicate keys return the cached result
without re-executing.

### P6: Append-Only Event Ledger

`ops.work_item_events` is **append-only**. No UPDATE or DELETE operations are
permitted. Every sync attempt (success or failure) produces exactly one row.

### P7: Hash-Based Change Detection

Each system calculates a deterministic SHA-256 hash of its owned fields only.
Sync occurs only when the hash differs from `last_plane_hash` or
`last_odoo_hash` in `ops.work_item_links`. This prevents no-op updates.

### P8: Conflict Resolution via Field Ownership

During nightly reconciliation, if both hashes have changed since last sync:

1. Apply field ownership rules (Plane wins plan fields, Odoo wins exec fields)
2. Set `sync_state = 'needs_review'` if ownership violation detected
3. Notify via Slack (`#ppm-clarity-conflicts`) with interactive resolution buttons
4. Log a `conflict` event in `ops.work_item_events`

---

## Integration Architecture

### Sync Directions

| Signal | Direction | Trigger |
|--------|-----------|---------|
| Commitment | Plane → Odoo | State changed to `In Progress` or label `commit` added |
| Completion | Odoo → Plane | Stage changed to `Done` in Odoo |
| Blocker | Odoo → Plane | Tag `blocked` added to Odoo task |
| Reconciliation | Bidirectional | Nightly cron (2 AM UTC+08:00) |

### Slack Notifications

PPM Clarity uses the existing Pulser Slack infrastructure pattern:

| Event | Channel | Priority |
|-------|---------|----------|
| Sync success | `#ppm-clarity-logs` | Low |
| Sync failure | `#ppm-clarity-alerts` | Medium |
| Conflict escalation | `#ppm-clarity-conflicts` | High |
| Daily reconciliation | `#ppm-clarity-logs` | Info |

Slack slash commands for manual overrides:
- `/ppm-retry <event-id>` — Retry failed sync
- `/ppm-resolve [plane|odoo] <link-id>` — Resolve conflict
- `/ppm-status` — Show sync health dashboard

---

## Operational Constraints

### Template Enforcement

Plane projects MUST use the PPM Clarity template with these states:
`Backlog → Triage → Planned → In Progress → Review → Done → Cancelled`

### Webhook Security

- HMAC-SHA256 signature validation on all inbound webhooks
- Replay protection via `idempotency_key` uniqueness
- Rate limiting: max 100 events/minute per project

### RLS Policies

All `ops.work_item_*` tables use Row Level Security:
- Only `service_role` can read/write
- No direct user access to SSOT tables
- All access through RPC functions

---

## Emergency Procedures

### Sync Failure (>3 retries)

1. Set `sync_state = 'blocked'` on the affected link
2. Post to `#ppm-clarity-alerts` with error details
3. Log `conflict` event with `success = false`
4. Manual intervention required via `/ppm-resolve`

### Signature Validation Failure

1. Reject the webhook payload (HTTP 401)
2. Log the attempt (source IP, headers, truncated body)
3. Alert `#ppm-clarity-alerts`
4. Do NOT process the event under any circumstances
