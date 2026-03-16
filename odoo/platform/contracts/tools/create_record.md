# Tool Spec: create_record

**Tool ID**: `create_record`
**Category**: write
**Requires Confirmation**: Yes
**Copilot XML ID**: `tool_create_record`
**Registry Ref**: `ssot/tools/registry.yaml` (copilot domain)

---

## Description

Create a new Odoo record. **Always requires explicit user confirmation** before execution (constitution rule 1). The copilot first shows a preview of what will be created, then blocks until the user clicks Confirm or Cancel.

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
    "values": {
      "type": "object",
      "description": "Field name to value mapping for the new record"
    }
  },
  "required": ["model", "values"]
}
```

### Validation Rules

- `model` must be a valid Odoo model accessible via `request.env[model]`
- `values` must be a non-empty object
- Field names must exist on the model
- Values must be type-compatible with field definitions
- Required fields on the model must be present in `values`

---

## Preview Output Schema

Before execution, the tool returns a preview for user confirmation:

```json
{
  "preview": {
    "action": "create",
    "model": "res.partner",
    "model_display": "Contact",
    "values": {
      "name": "John Doe",
      "email": "john@example.com"
    },
    "warnings": []
  },
  "requires_confirmation": true
}
```

### Preview Rules

- All field values are shown with human-readable labels
- Many2one fields show display_name, not raw ID
- Computed/default fields that will be auto-filled are listed separately
- Warnings include: required fields missing defaults, unusual field values

---

## Approval Requirements

**Mandatory**. Write tools always require user confirmation.

Flow:
1. AI returns `tool_calls` with `create_record` args
2. Controller calls `_dispatch_tool("create_record", args)` — returns preview (read-only)
3. Frontend shows preview with Confirm / Cancel buttons
4. **User clicks Confirm** → Controller calls `_execute_tool_confirmed("create_record", args)`
5. **User clicks Cancel** → No record created; audit envelope records `cancelled_by_user`

---

## Response Schema (after confirmation)

```json
{
  "created": true,
  "record_id": 123,
  "model": "res.partner",
  "display_name": "John Doe"
}
```

---

## Access Control

- Tool executes in `request.env` context (current user's access rights)
- If user lacks create access to model, returns `ACCESS_DENIED` **before** showing preview
- No `sudo()` escalation permitted
- ir.rule record rules are enforced

---

## Audit Envelope

Every invocation emits (including cancelled and failed attempts):

```json
{
  "trace_id": "uuid",
  "user_id": 2,
  "timestamp": "2026-03-03T10:00:00Z",
  "tool_name": "create_record",
  "tool_args": { "model": "res.partner", "values": { "name": "John Doe" } },
  "result_status": "success | cancelled_by_user | access_denied | validation_error",
  "duration_ms": 120
}
```

---

## Failure Modes

| Error Code | Condition | HTTP Status |
|------------|-----------|-------------|
| `ACCESS_DENIED` | User lacks create access to model | 403 |
| `MODEL_NOT_FOUND` | Invalid model name | 400 |
| `VALIDATION_ERROR` | Required fields missing or invalid values | 422 |
| `TOOL_EXECUTION_FAILED` | ORM error during record creation | 500 |

---

## Idempotency

**Not naturally idempotent** — each confirmed call creates a new record. Callers should use the `trace_id` to detect duplicate submissions. The audit envelope records every attempt.

---

## Side Effects

- New record created in target model
- Odoo ORM triggers fire (mail.thread, compute fields, etc.)
- Chatter log entry if model inherits `mail.thread`

---

## Evidence Path

`docs/evidence/action_eval/<run_id>/create_record/`
