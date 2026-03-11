# Tool Spec: navigate_to

**Tool ID**: `navigate_to`
**Category**: navigation
**Requires Confirmation**: No
**Copilot XML ID**: `tool_navigate_to`
**Registry Ref**: `ssot/tools/registry.yaml` (copilot domain)

---

## Description

Open a specific Odoo record in the main view. Returns a client action that the OWL frontend executes to navigate the browser. No data mutation.

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
    "record_id": {
      "type": "integer",
      "description": "Record ID to navigate to"
    }
  },
  "required": ["model", "record_id"]
}
```

### Validation Rules

- `model` must be a valid Odoo model accessible via `request.env[model]`
- `record_id` must be a positive integer
- Record must exist and be readable by current user

---

## Preview Output Schema

Not applicable — navigation tools execute immediately without preview.

---

## Approval Requirements

None. Navigation tools do not mutate data per constitution rule 1.

---

## Response Schema

```json
{
  "action": {
    "type": "ir.actions.act_window",
    "res_model": "sale.order",
    "res_id": 42,
    "views": [[false, "form"]]
  }
}
```

The frontend interprets this as a standard Odoo window action.

---

## Access Control

- Tool executes in `request.env` context (current user's access rights)
- If user lacks read access to model or record, returns `ACCESS_DENIED`
- No `sudo()` escalation permitted

---

## Audit Envelope

Every invocation emits:

```json
{
  "trace_id": "uuid",
  "user_id": 2,
  "timestamp": "2026-03-03T10:00:00Z",
  "tool_name": "navigate_to",
  "tool_args": { "model": "sale.order", "record_id": 42 },
  "result_status": "success",
  "duration_ms": 12
}
```

---

## Failure Modes

| Error Code | Condition | HTTP Status |
|------------|-----------|-------------|
| `ACCESS_DENIED` | User lacks read access to model/record | 403 |
| `MODEL_NOT_FOUND` | Invalid model name | 400 |
| `RECORD_NOT_FOUND` | Record does not exist | 404 |

---

## Idempotency

Navigation is inherently idempotent — repeated calls produce the same client action.

---

## Evidence Path

`docs/evidence/action_eval/<run_id>/navigate_to/`
