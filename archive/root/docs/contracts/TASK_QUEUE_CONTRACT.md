# C-04 — Task Queue Contract

**Status**: Active
**SSOT**: `ops.runs` table (Supabase `ops` schema)
**Consumers**: Slack agent (`@ipai/taskbus`), Edge Function workers, n8n workflows
**Validator**: `integration-backbone-gate.yml`

---

## Schema: `ops.runs`

| Column | Type | Description |
|--------|------|-------------|
| `id` | uuid | Primary key |
| `status` | text | `queued` / `running` / `completed` / `failed` / `cancelled` |
| `actor` | text | Who triggered (e.g., `slack:username`, `ci:deploy-production`) |
| `repo` | text | Repository context |
| `ref` | text | Git ref / branch |
| `pack_id` | text | Job type identifier |
| `input` | jsonb | Run input payload |
| `output` | jsonb | Run output / results |
| `correlation_id` | uuid | End-to-end tracing ID (nullable) |
| `created_at` | timestamptz | Creation time |
| `updated_at` | timestamptz | Last update time |

## Enqueue Protocol

All task enqueue operations MUST go through `@ipai/taskbus.enqueue()` or equivalent RPCs:
- `ops.start_run(p_actor, p_repo, p_ref, p_pack_id, p_input)` → returns `run_id`

## Boundary Rules

1. Slack NEVER writes directly to Odoo or `work.*` tables without an approved run
2. All external events enter via `ops.runs` — never bypass the ledger
3. Idempotency is enforced at the taskbus layer (duplicate keys return existing run)

## Event Lifecycle

```
queued → running → completed
                 → failed
       → cancelled
```

Each transition is logged to `ops.run_events` with level, message, and data.

## Correlation

- `correlation_id` links related events across `integration.outbox`, `integration.event_log`, `ops.runs`, and `ops.run_events`
- Query unified view: `SELECT * FROM ops.v_events WHERE correlation_id = ?`
