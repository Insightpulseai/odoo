# Tool Spec: search_records

**Tool ID**: `search_records`
**Category**: read
**Requires Confirmation**: No
**Copilot XML ID**: `tool_search_records`
**Registry Ref**: `ssot/tools/registry.yaml` (copilot domain)

---

## Description

Search any Odoo model using natural language. Returns matching records with ID and display name. Read-only — no side effects on Odoo data.

---

## Input Schema

```json
{
  "type": "object",
  "properties": {
    "model": {
      "type": "string",
      "description": "Odoo model technical name (e.g. sale.order, res.partner)"
    },
    "query": {
      "type": "string",
      "description": "Natural language search query"
    },
    "limit": {
      "type": "integer",
      "description": "Maximum number of results to return",
      "default": 5,
      "maximum": 50
    }
  },
  "required": ["model", "query"]
}
```

### Validation Rules

- `model` must be a valid Odoo model accessible via `request.env[model]`
- `query` must be non-empty string, max 500 characters
- `limit` clamped to 1–50

---

## Preview Output Schema

Not applicable — read tools execute immediately without preview.

---

## Approval Requirements

None. Read-only tools do not require user confirmation per constitution rule 1.

---

## Response Schema

```json
{
  "results": [
    { "id": 42, "display_name": "SO001 — Acme Corp" }
  ],
  "model": "sale.order",
  "count": 1,
  "total": 15
}
```

- `count`: number of results returned
- `total`: total matching records (before limit)

---

## Access Control

- Tool executes in `request.env` context (current user's access rights)
- If user lacks read access to `model`, returns `ACCESS_DENIED` error
- No `sudo()` escalation permitted

---

## Audit Envelope

Every invocation emits:

```json
{
  "trace_id": "uuid",
  "user_id": 2,
  "timestamp": "2026-03-03T10:00:00Z",
  "tool_name": "search_records",
  "tool_args": { "model": "sale.order", "query": "Acme", "limit": 5 },
  "result_status": "success",
  "duration_ms": 45
}
```

---

## Failure Modes

| Error Code | Condition | HTTP Status |
|------------|-----------|-------------|
| `ACCESS_DENIED` | User lacks read access to model | 403 |
| `MODEL_NOT_FOUND` | Invalid model name | 400 |
| `MESSAGE_REQUIRED` | Empty query string | 400 |
| `BRIDGE_TIMEOUT` | AI bridge unreachable | 504 |

---

## Idempotency

Read-only. Naturally idempotent — repeated calls with same args return same results (modulo concurrent data changes).

---

## Evidence Path

`docs/evidence/action_eval/<run_id>/search_records/`
