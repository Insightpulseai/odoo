# n8n MCP Gateway — Constitution

> Non-negotiable governance principles for the n8n Model Context Protocol (MCP) gateway.
> This document establishes security boundaries, privilege separation, and audit requirements.

**Version**: 1.0.0
**Status**: Draft
**Last Updated**: 2026-03-05

---

## Core Principles

### P1: Defense in Depth

All MCP tools must implement multiple layers of security controls:
- **Network**: Private visibility (org-only), not public exposure
- **Authorization**: Role-based access control (RBAC) for destructive operations
- **Input Validation**: Schema validation + allowlisting
- **Audit**: Comprehensive logging to Supabase `ops.run_events`
- **Rate Limiting**: Per-user execution quotas
- **Idempotency**: Deduplication for state-mutating operations

### P2: Privilege Separation

MCP tools are classified by privilege level:

| Tier | Access Pattern | Tools | Visibility |
|------|----------------|-------|------------|
| **Read-Only** | Public (org members) | `search_workflows`, `get_workflow_details`, `list_executions` | ✅ Claude chat context |
| **Execute-Gated** | Allowlist + approval | `execute_workflow` (allowlisted IDs only) | ❌ Requires explicit enablement |
| **Admin-Only** | Manual approval | `create_workflow`, `update_workflow`, `delete_workflow` | ❌ Not exposed via MCP |

**Rationale**:
- Read-only tools enable discovery and context building without risk.
- Execute-gated tools require pre-approved workflow IDs (prevent arbitrary execution).
- Admin tools are excluded from MCP surface (use n8n UI + approval workflow).

### P3: Audit Trail Completeness

Every MCP tool invocation must generate an audit record in `ops.run_events`:

```sql
INSERT INTO ops.run_events (
  source,
  event_type,
  event_data,
  user_id,
  idempotency_key,
  created_at
) VALUES (
  'n8n-mcp-gateway',
  'execute_workflow',
  jsonb_build_object(
    'workflow_id', $workflow_id,
    'input_data', $input_data,
    'execution_id', $execution_id,
    'status', $status
  ),
  $user_id,
  concat('n8n:mcp:', $workflow_id, ':', $execution_id),
  now()
);
```

**Requirements**:
- All tool calls logged, regardless of success/failure
- Logs persisted for 90 days (per `ssot/integrations/n8n.yaml`)
- Idempotency key format: `n8n:mcp:{workflow_id}:{execution_id}`
- User attribution (from MCP session context)

### P4: Zero Trust Model

No implicit trust relationships:
- **Workflow IDs** must be pre-validated against allowlist (not user-supplied arbitrary IDs)
- **Input schemas** validated before execution (no passthrough)
- **Execution timeout** enforced (max 60 seconds for MCP-triggered runs)
- **Output sanitization** applied (no PII leakage in MCP responses)

### P5: Domain Hygiene

**Canonical domain**: `insightpulseai.com` (NOT `.net`)
**Enforcement**: CI validation in DNS SSOT (`infra/dns/subdomain-registry.yaml`)

**Deprecated patterns** (must never be used):
- ❌ `insightpulseai.net` (legacy domain, deprecated Feb 2026)
- ❌ Hardcoded IP addresses in MCP configurations
- ❌ Localhost/development URLs in production configs

---

## Security Requirements

### SR1: Allowlisting Over Denylisting

**Execution Policy**:
- `execute_workflow` only accepts workflow IDs from **allowlist** (not arbitrary input)
- Allowlist location: `ssot/integrations/n8n_mcp_allowlist.yaml`
- Schema:
  ```yaml
  version: "1.0.0"
  allowed_workflows:
    - id: "workflow_id_here"
      name: "Workflow Name"
      description: "What it does"
      risk_level: low|medium|high
      approval_required: boolean
  ```

### SR2: Rate Limiting

Per-user execution quotas:
- **Read-only tools**: 100 requests/minute
- **Execute tools**: 10 executions/hour
- **Enforcement**: MCP gateway middleware (n8n webhook validation layer)

### SR3: Input Validation

All tool inputs validated against JSON Schema:
- `execute_workflow`: Must include workflow ID (UUID), optional `input_data` (object)
- Schema validation failures return 400 Bad Request (not 500 Internal Server Error)
- No SQL injection vectors (all queries use parameterized statements)

### SR4: Output Sanitization

MCP responses must not leak sensitive information:
- **PII Scrubbing**: Email addresses, phone numbers, tax IDs removed from execution logs
- **Credential Masking**: API keys, tokens shown as `***` (first 4 chars only)
- **Error Messages**: Generic errors for unauthorized requests (no stack traces)

---

## Operational Constraints

### OC1: Manual Approval for Workflow Addition

Adding workflows to the allowlist requires:
1. PR to `ssot/integrations/n8n_mcp_allowlist.yaml`
2. Code review by 1+ approvers
3. CI validation (schema check + workflow ID existence check)
4. Merge to main

**No ad-hoc additions** via MCP or n8n UI.

### OC2: Execution Timeout

All MCP-triggered workflow executions have hard timeout:
- **Default**: 60 seconds
- **Maximum**: 300 seconds (5 minutes, requires explicit justification in allowlist)
- **Enforcement**: n8n webhook timeout + Container Apps Job timeout

### OC3: Rollback Capability

Every allowlist change is version-controlled:
- Git history provides rollback path
- CI validates allowlist syntax before merge
- Invalid workflow IDs fail CI (workflow must exist in n8n)

---

## Integration Boundaries

### IB1: n8n is Execution Fabric, Not SSOT

**Workflow-as-Code Pattern**:
- Source of truth: `automations/n8n/workflows/*.json` (Git)
- Runtime state: n8n database (execution logs, temporary state)
- Durable audit: Supabase `ops.run_events` (permanent record)

**Never**:
- Store business logic exclusively in n8n UI (must export to Git)
- Use n8n DB as SoR for application state
- Bypass ops.run_events audit trail

### IB2: MCP Gateway is API Layer, Not Admin UI

**MCP Surface**:
- Controlled subset of n8n capabilities (read + allowlisted execute)
- Input validation and rate limiting
- Audit logging middleware

**NOT MCP Surface**:
- Workflow creation/modification (use n8n UI + Git export)
- Credential management (use Supabase Vault + n8n credential store)
- Admin operations (use n8n UI with manual approval)

---

## Compliance and Validation

### CV1: CI Enforcement

**Workflow**: `.github/workflows/n8n-mcp-gateway-validation.yml`

**Checks**:
1. Allowlist schema validation (YAML lint + schema check)
2. Workflow ID existence check (n8n API query)
3. Domain hygiene (no `.net` references in MCP configs)
4. Audit logging test (ops.run_events writable)

### CV2: Security Scanning

**Schedule**: Weekly (Sundays at 2 AM UTC)

**Scans**:
- Dependency vulnerabilities (npm audit)
- Secret scanning (no hardcoded tokens)
- Configuration drift (MCP config vs SSOT allowlist)

---

## Emergency Procedures

### EP1: Incident Response

If MCP gateway is compromised or abused:

1. **Immediate**: Disable n8n MCP server in `~/.claude/mcp-servers.json` (set to `"disabled": true`)
2. **Investigation**: Query `ops.run_events` for suspicious activity pattern
3. **Remediation**: Revoke affected API keys, rotate MCP token
4. **Postmortem**: Document in `docs/postmortems/YYYYMMDD-n8n-mcp-incident.md`

### EP2: Rollback Process

If allowlist change causes issues:

```bash
# 1. Identify problematic commit
git log -- ssot/integrations/n8n_mcp_allowlist.yaml

# 2. Revert change
git revert <commit-hash>

# 3. CI validates revert, auto-deploys
git push origin main
```

---

## References

- **SSOT Boundaries**: `docs/architecture/SSOT_BOUNDARIES.md`
- **n8n Integration Contract**: `ssot/integrations/n8n.yaml`
- **Platform SSOT Rules**: `.claude/rules/ssot-platform.md`
- **DNS SSOT**: `infra/dns/subdomain-registry.yaml`

---

**This constitution is immutable for active implementations. Changes require architecture review + approval.**
