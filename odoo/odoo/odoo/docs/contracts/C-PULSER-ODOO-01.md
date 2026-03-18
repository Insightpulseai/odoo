# C-PULSER-ODOO-01 — Pulser ↔ Odoo Intent Contract

**Status**: Active
**Parties**: Pulser (Slack/API) → Supabase control plane → Odoo ipai_pulser_connector
**Last updated**: 2026-03-01

---

## Overview

Pulser slash commands and API calls enqueue intent rows in `ops.taskbus_intents`.
The Odoo `ipai_pulser_connector` addon claims `odoo.*` intents via an atomic RPC,
executes them inside Odoo, and writes results back to Supabase.

Data flow:
```
Pulser (Slack/API) → ops.taskbus_intents (Supabase SSOT)
  → Odoo ipai_pulser_connector claims via RPC
  → Odoo executes (read-only MVP)
  → writes result back to ops.taskbus_intents
  → Pulser posts completion to Slack
```

---

## Platform Direction (non-normative)

- **Socket Mode** is the default transport for Pulser's long-lived agent runner.
- Pulser is a **software engineering agent interface** in Slack that enqueues
  intents — it never executes long tasks inline.
- All Slack handlers must ACK within 3 seconds; actual work runs asynchronously.

---

## Intent Schema

### Table: `ops.taskbus_intents`

| Column | Type | Description |
|--------|------|-------------|
| `id` | BIGSERIAL | Internal PK |
| `run_id` | UUID | External-facing unique run identifier |
| `request_id` | TEXT (UNIQUE) | Idempotency key (Slack trigger_id or UUID) |
| `intent_type` | TEXT | e.g. `odoo.healthcheck`, `status`, `deploy` |
| `args` | JSONB | Request arguments (exact shapes below) |
| `requested_by` | TEXT | Slack user id (`U...`) or `manual` |
| `channel_id` | TEXT | Slack channel for reply |
| `response_url` | TEXT | Slack response_url for deferred replies |
| `status` | TEXT | `queued` → `claimed`/`running` → `done`/`failed` |
| `result` | JSONB | Universal envelope (success or error) |
| `error_message` | TEXT | Short error text (max 500 chars) |
| `claimed_by` | TEXT | Instance ID of the claiming worker |
| `claim_token` | UUID | Unique token for this claim |
| `claimed_at` | TIMESTAMPTZ | When the claim was acquired |
| `claim_expires_at` | TIMESTAMPTZ | Lease expiry (120s default) |
| `completed_at` | TIMESTAMPTZ | When execution finished |
| `created_at` | TIMESTAMPTZ | Row creation time |
| `updated_at` | TIMESTAMPTZ | Last modification time |

### Atomic Claim RPC

```sql
ops.claim_taskbus_intent(p_intent_prefix, p_claimed_by, p_lease_seconds)
```

- Uses `FOR UPDATE SKIP LOCKED` to prevent double-claims
- Returns at most 1 row (the claimed intent)
- Sets `status='running'`, `claimed_by`, `claim_token`, `claim_expires_at`
- Expired claims (past `claim_expires_at`) can be re-claimed

---

## Allowed Intent Types (Odoo)

| Intent Type | Access | Description |
|-------------|--------|-------------|
| `odoo.healthcheck` | read-only | Odoo version, db name, uptime, modules count |
| `odoo.modules.status` | read-only | Installed modules + allowlist diff summary |
| `odoo.config.snapshot` | read-only | Safe config fingerprint (no secrets) |

**Rule**: Only `odoo.*` prefixed intents are processed by ipai_pulser_connector.
All others are ignored. Write intents require explicit allowlisting (future).

---

## Request Args Schemas

### odoo.healthcheck

```json
{
  "env": "prod",
  "include": {
    "addons_paths": true,
    "workers": true,
    "modules_count": true,
    "supabase_reachable": true
  },
  "meta": {
    "work_item_ref": "spec:odooops-console",
    "correlation_id": "uuid"
  }
}
```

### odoo.modules.status

```json
{
  "env": "prod",
  "limit": { "installed_sample": 50 },
  "allowlist": { "profile": "oca_allowlist_v1", "include_diff": true },
  "risk": { "include": true },
  "meta": {}
}
```

**Caps**: `installed_sample` max 100, enforced server-side.

### odoo.config.snapshot

```json
{
  "env": "prod",
  "redaction": {
    "mode": "safe",
    "include_keys": ["db_host", "db_port", "db_sslmode", "proxy_mode",
                     "workers", "limit_time_real", "limit_time_cpu",
                     "smtp_host", "smtp_port"]
  },
  "fingerprint": {
    "algorithm": "sha256",
    "include_keys": ["db_host", "db_port", "proxy_mode", "workers",
                     "limit_time_real", "limit_time_cpu", "smtp_host", "smtp_port"]
  }
}
```

**Rules**: Only `safe` redaction mode supported. Keys must be from the safe allowlist.

---

## Response Envelope Contract

### Universal Success Envelope

```json
{
  "ok": true,
  "intent": {
    "intent_id": "bigint",
    "request_id": "string",
    "intent_type": "odoo.healthcheck",
    "args": {},
    "claimed_by": "odoo:<db>:<instance_id>",
    "claim_token": "uuid",
    "claimed_at": "ISO8601",
    "finished_at": "ISO8601",
    "duration_ms": 840
  },
  "trace": {
    "work_item_ref": "spec:odooops-console",
    "run_id": "uuid",
    "correlation_id": "uuid"
  },
  "data": { /* handler-specific payload */ },
  "evidence": {
    "artifacts": [],
    "links": []
  }
}
```

### Universal Failure Envelope

```json
{
  "ok": false,
  "intent": { /* same as success */ },
  "trace": { /* same as success */ },
  "error": {
    "code": "ODOO_EXEC_ERROR",
    "message": "human-readable message",
    "details": {},
    "retryable": false
  },
  "evidence": { "artifacts": [], "links": [] }
}
```

### Error Codes

| Code | Meaning |
|------|---------|
| `ODOO_EXEC_ERROR` | General Odoo execution failure |
| `ARGS_INVALID` | Request args failed validation |
| `ALLOWLIST_PROFILE_UNKNOWN` | Unknown allowlist profile name |
| `REDACTION_MODE_UNSUPPORTED` | Only `safe` mode is supported |

---

## Idempotency Rules

1. `request_id` is UNIQUE — duplicate inserts are no-ops.
2. `claim_token` is required (set by RPC) — only the holder can complete.
3. Expired claims (`claim_expires_at < now()`) can be re-claimed by any worker.
4. Status transitions: `queued → running → done|failed` (never backwards).

---

## Audit Expectations

- Every intent execution writes to `ops.taskbus_intents.result` (always JSON).
- Run events are written to `ops.run_events` for traceability.
- Evidence artifacts reference Storage paths when applicable.
- Payloads are capped at 32KB (Slack-friendly).
- All timestamps are UTC ISO8601.

---

## Auth & Permissions

- Odoo connector authenticates to Supabase using `SUPABASE_SERVICE_ROLE_KEY`.
- Secrets are stored in `ssot/secrets/registry.yaml` (names only, never values).
- The cron job runs as the Odoo admin user.

---

## References

- Migration: `supabase/migrations/20260301000070_ops_taskbus_intents.sql`
- Odoo addon: `addons/ipai/ipai_pulser_connector/`
- Edge Functions: `supabase/functions/pulser-slack-handler/`, `pulser-intent-runner/`
- Spec: `spec/odooops-console/prd.md` (FR17)
- SSOT: `ssot/secrets/registry.yaml`
