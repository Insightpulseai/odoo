# Action Layer

> Odoo action execution, guardrails, confirmation flow, and audit trail.

## Action Categories

| Category | Examples | Confirmation | Audit |
|----------|----------|-------------|-------|
| **Read** | Fetch invoice, list expenses, show partner | None | Logged |
| **Workflow** | Confirm SO, post invoice, submit expense | Required | Logged |
| **Action** | Create record, update field, send email | Required | Logged |
| **Recommendation** | Suggest reconciliation, flag anomaly | None (informational) | Logged |

Reference: `ssot/odoo/odoo_copilot_finance_tools.yaml`

## Tool Contract

Every copilot tool is a business-safe surface, not a direct database primitive.

```yaml
defaults:
  approval_mode: policy_driven
  audit_required: true
  idempotency_required: true
```

Tool definitions specify:
- **Inputs** with types and required flags
- **Outputs** with entity shape and field list
- **Access** with minimum scope (e.g., `finance.read`, `finance.write`)
- **Side effects** declaration (none, record_mutation, workflow_transition, external_call)

## Guardrails

### ACL Enforcement

The copilot executes all Odoo operations as the authenticated user. It inherits
the user's groups, record rules, and field-level access. The copilot cannot
escalate privileges.

```
User groups -> Odoo ACL check -> Tool execution -> Result
```

If the user lacks permission, the tool returns an access error. The copilot
renders this as a clear denial message, never retries with elevated privileges.

### Confirmation Gate

State-mutating actions require explicit user confirmation before execution:

1. Copilot proposes the action with a preview of what will change
2. User confirms or cancels
3. On confirm, copilot executes and returns the result
4. On cancel, copilot acknowledges and does not execute

Confirmation is enforced client-side in the copilot UI. The backend tool
endpoint also validates that a confirmation token was provided for write
operations.

### Scope Limits

| Limit | Value | Rationale |
|-------|-------|-----------|
| Max records per action | 50 | Prevent bulk mutations via chat |
| Max chained actions per turn | 5 | Prevent runaway multi-step |
| Sensitive fields blocked | `password`, `oauth_*`, `secret_*` | Never writable via copilot |
| Deletion | Disabled | Copilot can archive, never delete |

### Approval-Aware Actions

For actions that require business approval (e.g., expense approval, PO
confirmation above threshold), the copilot:

1. Checks the user's approval authority
2. If authorized, executes with confirmation gate
3. If not authorized, routes to the correct approver via Odoo's approval workflow
4. Never bypasses approval chains

## Audit Trail

Every copilot interaction is logged:

| Field | Source |
|-------|--------|
| `user_id` | Authenticated Odoo user |
| `timestamp` | Server UTC time |
| `action_type` | read / workflow / action / recommendation |
| `tool_name` | Tool key from tool contract |
| `inputs` | Sanitized input parameters (secrets redacted) |
| `outputs` | Result summary (record IDs, status) |
| `confirmation` | Whether user confirmed (for write actions) |
| `duration_ms` | Execution time |
| `error` | Error message if failed |

Audit records are stored in `ipai.copilot.audit.log` (Odoo model) and
optionally forwarded to Azure Monitor for centralized observability.

## Error Handling

| Error Type | Copilot Behavior |
|------------|-----------------|
| ACL denied | "You do not have permission to perform this action." |
| Validation error | Show specific field errors from Odoo |
| Record not found | "The record was not found. Please verify the reference." |
| Timeout | "The operation timed out. Please try again." |
| Unexpected error | "An error occurred. The issue has been logged." (traceback in audit, not shown to user) |

The copilot never fabricates a success message when an action fails.
