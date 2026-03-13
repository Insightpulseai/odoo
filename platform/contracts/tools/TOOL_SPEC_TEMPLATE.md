# Tool Specification: <tool_id>

Version: 0.1.0 | Status: Draft | Owner: platform

## Identity

| Field | Value |
|-------|-------|
| **Tool ID** | `<snake_case_identifier>` |
| **Display Name** | `<Human Readable Name>` |
| **Category** | `read` / `write` / `automation` |
| **Requires Confirmation** | `true` / `false` |
| **Registered In** | `ipai.copilot.tool` / `ipai.agent.tool` |

## Purpose

One-paragraph description of what this tool does and when it should be invoked.

## Parameters (JSON Schema)

```json
{
  "type": "object",
  "properties": {
    "param_name": {
      "type": "string",
      "description": "What this parameter controls"
    }
  },
  "required": ["param_name"]
}
```

## Contract

### Preview
What the user sees before confirming execution. Must be deterministic and
human-readable.

### Approval Gate
- **Read tools**: No approval required; results returned immediately.
- **Write tools**: Preview displayed in sidebar; user must click Confirm.
- **Automation tools**: Preview + HMAC-signed webhook; user must click Confirm.

### Idempotency
How duplicate invocations are handled:
- Idempotency key: `<describe key derivation>`
- Window: `<seconds>`
- Behavior on duplicate: `<skip / return cached / error>`

### Audit Envelope
What is logged for every invocation:
- `trace_id`: UUID from bridge response
- `user_id`: Authenticated user
- `tool_name`: This tool's ID
- `args`: Sanitized input parameters (no secrets)
- `result`: Outcome (success/error + summary)
- `timestamp`: ISO 8601

## Permissions

| Gate | Value |
|------|-------|
| **Odoo Access** | `ir.model.access` + `ir.rule` for target model |
| **Group Restriction** | `<xml_id>` or "all authenticated users" |
| **Record Rule** | Standard Odoo record rules apply |

## Eval Coverage

| Eval Harness | Case ID | Description |
|--------------|---------|-------------|
| `eval/action_eval.yaml` | `<case_id>` | Verifies correct execution |
| `eval/action_eval.yaml` | `<case_id>_denied` | Verifies access denial |

## Error Codes

| Code | HTTP | Description | Retryable |
|------|------|-------------|-----------|
| `TOOL_EXECUTION_FAILED` | 500 | Execution error | No |
| `ACCESS_DENIED` | 403 | User lacks permission | No |
| `INVALID_PARAMS` | 400 | Schema validation failed | No |

## Rollback

Describe rollback strategy if the tool's action needs to be undone:
- **Reversible**: Yes/No
- **Mechanism**: `<describe how to undo>`

---

*Template: contracts/tools/TOOL_SPEC_TEMPLATE.md*
*Referenced by: ssot/ai/odoo_ai_mapping.yaml (tool_contract_v1)*
