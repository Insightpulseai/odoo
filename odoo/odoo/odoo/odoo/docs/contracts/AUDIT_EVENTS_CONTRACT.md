# C-08 — Platform Audit Events Contract

**Status**: Active
**SSOT**: `ops.v_events` view (unified over `integration.event_log` + `ops.run_events`)
**Consumers**: Observability dashboards, compliance audit, correlation tracing
**Validator**: `integration-backbone-gate.yml`

---

## Canonical Audit Surface: `ops.v_events`

Unified read-only VIEW that merges events from all integration domains:

| Column | Type | Description |
|--------|------|-------------|
| `id` | uuid | Event ID |
| `schema_source` | text | `integration` or `ops` |
| `source` | text | Origin system (`odoo`, `slack`, `ci`, `n8n`) |
| `event_type` | text | Qualified event type |
| `entity_type` | text | Aggregate / entity type |
| `entity_ref` | text | Entity identifier |
| `payload` | jsonb | Event payload |
| `correlation_id` | uuid | End-to-end tracing ID |
| `created_at` | timestamptz | Event timestamp |

## Correlation ID Contract

1. Every event emitter MUST include `correlation_id` in its payload
2. Correlation IDs are generated at the origin (Odoo write, CI deploy, Slack action)
3. All downstream handlers propagate the same `correlation_id`
4. The `x-correlation-id` HTTP header is the canonical transport mechanism

## Event Sources

| Source | Schema | Table | Event Examples |
|--------|--------|-------|----------------|
| Odoo | `integration` | `event_log` | `expense.submitted`, `finance_task.created` |
| Slack | `ops` | `run_events` | `slack.approval.approve`, `slack.app_mention` |
| CI/CD | `ops` | `run_events` | `deployment.completed`, `workflow_run` |
| Workers | `ops` | `run_events` | Agent execution events |

## Routing

Events are routed from `integration.outbox` via `ops.integration_routes`:
- Pattern matching: glob-style (`expense.*`, `*.approval_required`)
- Handlers: `slack-notify`, `slack-approval`, `n8n-event-router`
- Resolution: `ops.resolve_routes(event_type)` RPC

## Immutability

- `integration.event_log` is append-only (no UPDATE, no DELETE)
- `ops.run_events` is append-only per run
- `ops.v_events` is a read-only VIEW — no direct writes

## Querying

```sql
-- All events for a correlation chain
SELECT * FROM ops.v_events WHERE correlation_id = '<uuid>' ORDER BY created_at;

-- Recent events by source
SELECT * FROM ops.v_events WHERE source = 'odoo' ORDER BY created_at DESC LIMIT 50;

-- Event type distribution
SELECT event_type, count(*) FROM ops.v_events
WHERE created_at > now() - interval '24 hours'
GROUP BY event_type ORDER BY count DESC;
```
