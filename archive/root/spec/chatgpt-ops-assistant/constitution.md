# Constitution — ChatGPT Ops Assistant

> Non-negotiable rules for the `ops-assistant` MCP server and ChatGPT App.
> These constraints are enforced at the tool-execution layer, not advisory.

## 1. Deny-by-Default Execution

All tool calls are **denied unless explicitly allowlisted** in
`ssot/integrations/chatgpt_app_tool_allowlist.yaml`.

- Unknown tool names: rejected with error, logged to audit sink.
- Known tools with disallowed fields: rejected, field violation logged.
- No implicit tool discovery from Odoo model introspection at runtime.

## 2. Approval-Gated Odoo Writes

Any tool that **writes to Odoo in production** requires prior Slack approval:

- `slack.request_approval` is called automatically before execution.
- The approval message includes: tool name, target record, field changes, requesting user.
- Timeout: 60 minutes. If not approved, the action is cancelled and logged.
- Stage environment: approval is bypassed (configurable per environment).

## 3. Audit Trail

Every tool invocation — successful, denied, or errored — is written to
`supabase.ops.run_events` with:

- `event_id` (UUID v4)
- `tool_name`
- `input_params` (secrets redacted)
- `output_summary`
- `status` (success | denied | error | approval_pending | approval_timeout)
- `user_id` (OpenAI user identity from OAuth)
- `idempotency_key`
- `timestamp`

Audit records are **append-only**. No deletions.

## 4. No Secrets in Code

- All secrets referenced by name only (vault key or env var name).
- MCP server reads secrets from Supabase Vault or environment variables at runtime.
- No secret values in: source code, YAML configs, MCP tool responses, audit logs.
- Secret names are documented in `ssot/secrets/registry.yaml`.

## 5. Idempotency

Every external write (Odoo, Plane, Slack) must include an **idempotency key**:

- Format: `{tool_name}:{entity_id}:{timestamp_ms}`
- Duplicate keys within a 5-minute window are rejected (HTTP 409).
- Idempotency keys are stored in `ops.idempotency_keys` (Supabase).

## 6. Rate Limiting

- Global: 60 requests/minute per user session.
- Plane API: 60 requests/minute (upstream constraint, enforce client-side).
- Odoo XML-RPC: no upstream limit, but self-imposed 30 writes/minute.
- Slack: standard tier limits apply (chat.postMessage: 1/sec per channel).

## 7. Field-Level Access Control

- Each Odoo write tool declares `allowed_fields` and `blocked_fields`.
- Fields not in `allowed_fields` are silently dropped (not errored).
- Fields in `blocked_fields` cause the entire request to be rejected.
- Financial fields (account_*, bank_*, vat) are always blocked.

## 8. Cross-System Integrity

- When a tool creates a linked entity (e.g., Odoo lead + Plane work item),
  both IDs must be written to `ops.external_identities` atomically.
- If one system write succeeds and the other fails, the successful write
  is logged but the link is marked `status: partial`.
- Partial links trigger a Slack notification for manual resolution.

## 9. No Destructive Operations

The following operations are permanently forbidden:

- `unlink` / `delete` on any Odoo model
- Deleting Plane work items or pages
- Deleting Slack messages
- Dropping or truncating any database table
- Modifying Odoo `ir.config_parameter` values

## 10. Transport Security

- MCP server communicates over HTTPS only (TLS 1.2+).
- SSE transport with proper CORS headers.
- OAuth 2.1 with PKCE for all user authentication.
- No API keys in URL query parameters.
