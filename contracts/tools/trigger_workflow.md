# Tool Spec: trigger_workflow

**Tool ID**: `trigger_workflow`
**Category**: automation
**Requires Confirmation**: Yes
**Copilot XML ID**: `tool_trigger_workflow`
**Registry Ref**: `ssot/tools/registry.yaml` (copilot domain)

---

## Description

Trigger a configured n8n automation workflow via webhook. **Always requires explicit user confirmation** (constitution rule 1). The workflow must be allowlisted in `ssot/bridges/catalog.yaml` and configured via `ir.config_parameter` (constitution rule 10).

---

## Input Schema

```json
{
  "type": "object",
  "properties": {
    "workflow_id": {
      "type": "string",
      "description": "n8n workflow ID from the allowlist (matches ir.config_parameter key suffix)"
    },
    "data": {
      "type": "object",
      "description": "Data payload to pass to the n8n webhook"
    }
  },
  "required": ["workflow_id"]
}
```

### Validation Rules

- `workflow_id` must exist in `ssot/bridges/catalog.yaml` allowlist
- `workflow_id` must have a corresponding `ir.config_parameter` webhook URL
- `data` payload must be JSON-serializable, max 100KB
- No secrets permitted in `data` payload

---

## Preview Output Schema

Before execution, the tool returns a preview:

```json
{
  "preview": {
    "action": "trigger_workflow",
    "workflow_id": "expense_report_sync",
    "workflow_display": "Expense Report Sync",
    "webhook_url_masked": "https://n8n.insightpulseai.com/webhook/****",
    "data_summary": { "keys": ["report_id", "user_id"], "size_bytes": 256 },
    "allowlisted": true
  },
  "requires_confirmation": true
}
```

### Preview Rules

- Webhook URL is masked (last 4 chars of path shown)
- Data payload summarized by keys and size (not full values)
- `allowlisted` field confirms the workflow is in the catalog

---

## Approval Requirements

**Mandatory**. Automation tools trigger external systems.

Flow:
1. AI returns `tool_calls` with `trigger_workflow` args
2. Controller validates `workflow_id` against allowlist
3. If not allowlisted → immediate `ACCESS_DENIED` (no preview)
4. Controller calls `_dispatch_tool` — returns preview
5. Frontend shows preview with Confirm / Cancel
6. **User clicks Confirm** → POST to n8n webhook with HMAC signature
7. **User clicks Cancel** → No webhook called; audit records `cancelled_by_user`

---

## Response Schema (after confirmation)

```json
{
  "triggered": true,
  "workflow_id": "expense_report_sync",
  "webhook_status": 200,
  "webhook_response": { "success": true },
  "duration_ms": 450
}
```

---

## Access Control

- Workflow must be in `ssot/bridges/catalog.yaml` allowlist
- Webhook URL retrieved from `ir.config_parameter` (not user-supplied)
- Request signed with HMAC using `ir.config_parameter` secret
- Non-allowlisted workflows are rejected before preview

---

## Audit Envelope

```json
{
  "trace_id": "uuid",
  "user_id": 2,
  "timestamp": "2026-03-03T10:00:00Z",
  "tool_name": "trigger_workflow",
  "tool_args": { "workflow_id": "expense_report_sync", "data": { "report_id": 7 } },
  "result_status": "success | cancelled_by_user | access_denied | webhook_error",
  "duration_ms": 450
}
```

For rejected (non-allowlisted) workflows:

```json
{
  "trace_id": "uuid",
  "user_id": 2,
  "timestamp": "2026-03-03T10:00:00Z",
  "tool_name": "trigger_workflow",
  "tool_args": { "workflow_id": "unknown_workflow" },
  "result_status": "access_denied",
  "duration_ms": 5
}
```

---

## Failure Modes

| Error Code | Condition | HTTP Status |
|------------|-----------|-------------|
| `ACCESS_DENIED` | Workflow not in allowlist | 403 |
| `BRIDGE_URL_NOT_CONFIGURED` | Webhook URL missing from ir.config_parameter | 503 |
| `BRIDGE_TIMEOUT` | n8n webhook did not respond within 30s | 504 |
| `TOOL_EXECUTION_FAILED` | n8n returned non-2xx status | 502 |

---

## Idempotency

**Depends on the n8n workflow**. The copilot does not guarantee idempotency — it is the workflow's responsibility. The `trace_id` is passed in the webhook payload for deduplication.

---

## Side Effects

- HTTP POST to external n8n webhook
- n8n workflow execution (varies per workflow)
- Potential downstream effects: email, Slack, record updates

---

## Security Notes

- Webhook URLs never exposed to the frontend or AI model
- HMAC signature prevents unauthorized webhook invocation
- Payload size limited to 100KB
- No secrets in `data` payload (enforced at validation)

---

## Evidence Path

`docs/evidence/action_eval/<run_id>/trigger_workflow/`
