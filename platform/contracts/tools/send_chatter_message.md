# Tool Spec: send_chatter_message

**Tool ID**: `send_chatter_message`
**Category**: write
**Requires Confirmation**: Yes
**Copilot XML ID**: `tool_send_chatter_message`
**Registry Ref**: `ssot/tools/registry.yaml` (copilot domain)

---

## Description

Post a message in a record's chatter (message log) via `mail.thread`. **Always requires explicit user confirmation** before execution (constitution rule 1). Messages are visible to followers and may trigger email notifications.

---

## Input Schema

```json
{
  "type": "object",
  "properties": {
    "model": {
      "type": "string",
      "description": "Odoo model technical name (must inherit mail.thread)"
    },
    "record_id": {
      "type": "integer",
      "description": "Record ID to post the message on"
    },
    "message": {
      "type": "string",
      "description": "Message content to post in the chatter"
    }
  },
  "required": ["model", "record_id", "message"]
}
```

### Validation Rules

- `model` must inherit `mail.thread`
- `record_id` must reference an existing, accessible record
- `message` must be non-empty, max 10,000 characters
- HTML content is sanitized by Odoo's `mail` module

---

## Preview Output Schema

Before execution, the tool returns a preview:

```json
{
  "preview": {
    "action": "send_chatter_message",
    "model": "sale.order",
    "model_display": "Sales Order",
    "record_id": 42,
    "record_display": "SO001",
    "message": "Shipment delayed by 2 days",
    "followers_count": 3,
    "will_notify": true
  },
  "requires_confirmation": true
}
```

### Preview Rules

- Shows target record display name
- Indicates follower count and whether notifications will fire
- Message content displayed as-is for user review

---

## Approval Requirements

**Mandatory**. Messages are visible to external parties (followers).

Flow:
1. AI returns `tool_calls` with `send_chatter_message` args
2. Controller calls `_dispatch_tool` — returns preview with follower info
3. Frontend shows preview with Confirm / Cancel buttons
4. **User clicks Confirm** → `record.message_post(body=message, message_type='comment')`
5. **User clicks Cancel** → No message posted; audit envelope records `cancelled_by_user`

---

## Response Schema (after confirmation)

```json
{
  "posted": true,
  "message_id": 456,
  "model": "sale.order",
  "record_id": 42,
  "record_display": "SO001"
}
```

---

## Access Control

- User must have read access to the record
- User must have access to `mail.message` create
- If model does not inherit `mail.thread`, returns `VALIDATION_ERROR`
- No `sudo()` escalation permitted

---

## Audit Envelope

```json
{
  "trace_id": "uuid",
  "user_id": 2,
  "timestamp": "2026-03-03T10:00:00Z",
  "tool_name": "send_chatter_message",
  "tool_args": { "model": "sale.order", "record_id": 42, "message": "..." },
  "result_status": "success | cancelled_by_user | access_denied",
  "duration_ms": 85
}
```

---

## Failure Modes

| Error Code | Condition | HTTP Status |
|------------|-----------|-------------|
| `ACCESS_DENIED` | User lacks access to record or mail.message | 403 |
| `RECORD_NOT_FOUND` | Record does not exist | 404 |
| `VALIDATION_ERROR` | Model does not inherit mail.thread | 422 |
| `TOOL_EXECUTION_FAILED` | ORM error during message_post | 500 |

---

## Idempotency

**Not naturally idempotent** — each confirmed call posts a new message. Use `trace_id` to detect duplicate submissions.

---

## Side Effects

- New `mail.message` record created
- Email notifications sent to followers (if configured)
- Activity stream updated for record followers

---

## Evidence Path

`docs/evidence/action_eval/<run_id>/send_chatter_message/`
