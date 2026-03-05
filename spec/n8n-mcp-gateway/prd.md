# n8n MCP Gateway — Product Requirements

> Security hardening and governance implementation for n8n Model Context Protocol gateway.

**Version**: 1.0.0
**Status**: Draft
**Target Date**: 2026-03-12
**Owner**: DevOps / Security

---

## Problem Statement

### Current State (Identified Issues)

1. **Domain Hygiene Violation**
   - **Issue**: MCP connector configuration may reference deprecated `.net` domain
   - **Risk**: DNS ambiguity, potential traffic misdirection
   - **Evidence**: User reported screenshot showing `.net` usage (verification needed)

2. **PUBLIC WRITE + OPEN WORLD Access**
   - **Issue**: `execute_workflow` tool has no access controls
   - **Risk**: Any Claude Code session can execute arbitrary n8n workflows
   - **Impact**: Unauthorized automation execution, potential data manipulation

3. **Missing Allowlisting**
   - **Issue**: No workflow ID allowlist — accepts any workflow ID
   - **Risk**: Execution of unvetted/malicious workflows
   - **Impact**: Supply chain attack vector, unauthorized API calls

4. **No Audit Logging**
   - **Issue**: MCP tool calls not logged to `ops.run_events`
   - **Risk**: No forensic trail for incident investigation
   - **Impact**: Cannot detect or investigate abuse patterns

5. **Visibility Too Permissive**
   - **Issue**: MCP tools may be publicly accessible
   - **Expected**: Private/org-only visibility
   - **Impact**: External actors could discover and enumerate workflows

### Desired State

1. **Domain Compliance**
   - All MCP configurations use canonical `.com` domain
   - CI validates no `.net` references exist
   - DNS SSOT as single source of truth

2. **Privilege Separation**
   - Read-only tools (search, list) remain public (org-only)
   - Execute tools require allowlist + approval workflow
   - Admin tools excluded from MCP surface entirely

3. **Allowlist-Driven Execution**
   - `execute_workflow` only accepts pre-approved workflow IDs
   - Allowlist stored in `ssot/integrations/n8n_mcp_allowlist.yaml`
   - CI validates allowlist schema and workflow existence

4. **Comprehensive Audit Trail**
   - All MCP tool calls logged to Supabase `ops.run_events`
   - 90-day retention (per n8n integration SSOT)
   - User attribution and idempotency key tracking

5. **Private Visibility**
   - MCP gateway requires authentication token
   - No public enumeration of workflows or tools
   - Rate limiting per user/session

---

## Goals and Non-Goals

### Goals

**G1**: Enforce domain hygiene across all n8n MCP configurations
- Verify `~/.claude/mcp-servers.json` uses `.com` domain
- Add CI validation to prevent `.net` regressions
- Update any documentation referencing deprecated domain

**G2**: Implement privilege separation for MCP tools
- Create tool classification (read-only, execute-gated, admin-only)
- Expose only read-only + allowlisted execute tools via MCP
- Document admin operations outside MCP surface

**G3**: Deploy allowlist-based execution policy
- Create `ssot/integrations/n8n_mcp_allowlist.yaml` SSOT
- Implement allowlist validation in MCP gateway middleware
- Add CI check for allowlist schema + workflow ID existence

**G4**: Enable comprehensive audit logging
- All MCP tool calls write to `ops.run_events`
- Include user attribution, workflow ID, execution status
- 90-day retention with idempotency key deduplication

**G5**: Restrict MCP gateway visibility
- Change from public to private/org-only
- Require authentication token (N8N_MCP_TOKEN)
- Implement rate limiting (10 executions/hour per user)

### Non-Goals

**NG1**: Re-architecting n8n workflow engine
- Scope limited to MCP gateway security, not n8n internals
- n8n execution model remains unchanged

**NG2**: Retroactive audit trail for past executions
- Audit logging applies to future MCP calls only
- Historical execution logs remain in n8n database (not migrated)

**NG3**: Real-time threat detection/prevention
- Basic rate limiting implemented, not ML-based anomaly detection
- Advanced threat detection deferred to future iteration

---

## User Stories

### US1: Security Engineer — Audit MCP Tool Usage

**As a** security engineer
**I want** comprehensive audit logs of all MCP tool invocations
**So that** I can investigate incidents and detect abuse patterns

**Acceptance Criteria**:
- Every MCP tool call creates a row in `ops.run_events`
- Logs include: user ID, workflow ID, input data (sanitized), execution status
- Logs queryable via SQL with 90-day retention
- Idempotency key prevents duplicate log entries

**Evidence**: Query `ops.run_events` table shows MCP calls with complete metadata

---

### US2: DevOps Engineer — Control Workflow Execution

**As a** DevOps engineer
**I want** to allowlist workflows before they can be MCP-executed
**So that** only vetted automation can run via Claude Code

**Acceptance Criteria**:
- Allowlist exists at `ssot/integrations/n8n_mcp_allowlist.yaml`
- `execute_workflow` rejects workflow IDs not in allowlist (403 Forbidden)
- CI validates allowlist schema + workflow ID existence
- PR process required for allowlist additions

**Evidence**: Attempt to execute non-allowlisted workflow returns 403 error

---

### US3: Compliance Officer — Enforce Domain Policy

**As a** compliance officer
**I want** all MCP configurations to use the canonical `.com` domain
**So that** infrastructure complies with DNS policy

**Acceptance Criteria**:
- `~/.claude/mcp-servers.json` verified to use `.com` domain
- CI fails if any config references `.net` domain
- Documentation updated to remove `.net` references

**Evidence**: CI validation passes, grep shows no `.net` in MCP configs

---

### US4: AI Agent (Claude Code) — Discover Safe Workflows

**As an** AI agent (Claude Code)
**I want** to search and list available workflows
**So that** I can provide relevant automation suggestions to users

**Acceptance Criteria**:
- `search_workflows` and `list_workflows` tools remain accessible (read-only)
- No authentication required for read-only operations (org-scoped)
- Results include workflow name, description, allowlist status

**Evidence**: Claude Code can query workflows without triggering execution

---

### US5: AI Agent (Claude Code) — Execute Approved Workflows

**As an** AI agent (Claude Code)
**I want** to execute allowlisted workflows when user requests automation
**So that** I can automate tasks without manual intervention

**Acceptance Criteria**:
- `execute_workflow` succeeds for allowlisted workflow IDs
- Execution logged to `ops.run_events` with user attribution
- Non-allowlisted workflows return clear error message
- Execution status returned to Claude Code for user feedback

**Evidence**: Claude Code successfully executes allowlisted workflow, receives execution status

---

## Functional Requirements

### FR1: Domain Validation

**Requirement**: All n8n MCP configurations must use canonical `.com` domain

**Implementation**:
- Update `~/.claude/mcp-servers.json` line 176 if `.net` present
- Add CI workflow: `.github/workflows/n8n-mcp-domain-validation.yml`
- Grep validation: `grep -r "insightpulseai\.net.*mcp" . && exit 1`

**Acceptance Test**:
```bash
# Should fail if .net found
grep -r "insightpulseai\.net" ~/.claude/mcp-servers.json
# Exit code: 1 (not found)

# Should succeed for .com
grep "n8n.insightpulseai.com" ~/.claude/mcp-servers.json
# Exit code: 0 (found)
```

---

### FR2: Allowlist Schema

**Requirement**: Workflow allowlist stored in SSOT file with validated schema

**Schema** (`ssot/integrations/n8n_mcp_allowlist.yaml`):
```yaml
version: "1.0.0"
schema: ssot.n8n_mcp_allowlist.v1
last_updated: "2026-03-05"

allowed_workflows:
  - id: "workflow-uuid-here"
    name: "Human-readable name"
    description: "What this workflow does"
    risk_level: low|medium|high
    approval_required: boolean
    max_execution_time_seconds: integer
    added_by: "GitHub username"
    added_date: "YYYY-MM-DD"

  # Example allowlisted workflow
  - id: "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
    name: "Deploy to Staging"
    description: "Deploys specified git ref to staging environment"
    risk_level: medium
    approval_required: true
    max_execution_time_seconds: 300
    added_by: "jgtolentino"
    added_date: "2026-03-05"
```

**Validation**:
- CI validates YAML syntax
- CI checks workflow IDs exist in n8n (via n8n API)
- CI enforces required fields (id, name, risk_level)

---

### FR3: Execute Workflow Gating

**Requirement**: `execute_workflow` only accepts allowlisted IDs

**Implementation** (n8n webhook validation):
```python
# Pseudo-code for n8n webhook validation
def validate_workflow_execution(workflow_id: str) -> bool:
    allowlist = load_yaml("ssot/integrations/n8n_mcp_allowlist.yaml")
    allowed_ids = [w["id"] for w in allowlist["allowed_workflows"]]

    if workflow_id not in allowed_ids:
        log_audit_event(
            event_type="execute_workflow_rejected",
            reason="workflow_not_allowlisted",
            workflow_id=workflow_id
        )
        return False

    return True
```

**Error Response** (non-allowlisted):
```json
{
  "error": "Workflow execution not allowed",
  "code": "WORKFLOW_NOT_ALLOWLISTED",
  "workflow_id": "<requested-id>",
  "message": "This workflow is not pre-approved for MCP execution. Submit a PR to add it to the allowlist."
}
```

---

### FR4: Audit Logging

**Requirement**: All MCP tool calls logged to `ops.run_events`

**Schema** (`ops.run_events` table):
```sql
CREATE TABLE ops.run_events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  source TEXT NOT NULL,  -- 'n8n-mcp-gateway'
  event_type TEXT NOT NULL,  -- 'execute_workflow', 'search_workflows', etc.
  event_data JSONB NOT NULL,
  user_id TEXT,  -- From MCP session context
  idempotency_key TEXT UNIQUE,
  status TEXT,  -- 'success', 'failed', 'rejected'
  created_at TIMESTAMPTZ DEFAULT now()
);
```

**Audit Event** (example):
```json
{
  "source": "n8n-mcp-gateway",
  "event_type": "execute_workflow",
  "event_data": {
    "workflow_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "workflow_name": "Deploy to Staging",
    "input_data": {"ref": "main", "target": "staging"},
    "execution_id": "exec-12345",
    "execution_status": "running",
    "mcp_session_id": "session-67890"
  },
  "user_id": "claude-code-user",
  "idempotency_key": "n8n:mcp:a1b2c3d4-e5f6-7890-abcd-ef1234567890:exec-12345",
  "status": "success",
  "created_at": "2026-03-05T10:30:00+08:00"
}
```

---

### FR5: Rate Limiting

**Requirement**: Per-user execution quotas enforced

**Limits**:
- Read-only tools: 100 requests/minute
- Execute tools: 10 executions/hour
- Admin tools: Not exposed via MCP

**Implementation**:
- Middleware in n8n webhook (check Supabase `ops.run_events` for recent calls)
- Return 429 Too Many Requests if quota exceeded
- Quota resets every hour (rolling window)

**Rate Limit Response**:
```json
{
  "error": "Rate limit exceeded",
  "code": "RATE_LIMIT_EXCEEDED",
  "limit": "10 executions/hour",
  "retry_after_seconds": 1800,
  "current_usage": {
    "count": 10,
    "window_start": "2026-03-05T10:00:00+08:00",
    "window_end": "2026-03-05T11:00:00+08:00"
  }
}
```

---

## Non-Functional Requirements

### NFR1: Performance

- MCP tool calls respond within 2 seconds (95th percentile)
- Allowlist validation adds <100ms overhead
- Audit logging adds <200ms overhead
- Rate limit check adds <50ms overhead

### NFR2: Reliability

- MCP gateway 99.9% uptime (same as n8n SLA)
- Graceful degradation if Supabase audit logging unavailable (log locally, sync later)
- No workflow execution failures due to allowlist/audit infrastructure issues

### NFR3: Security

- All MCP communications over HTTPS
- MCP token stored in environment variable (not config file)
- No secrets logged in audit events (credentials masked)
- Idempotency prevents replay attacks

### NFR4: Maintainability

- Allowlist managed via Git PR workflow (no manual edits)
- CI validates allowlist changes before merge
- Audit logs queryable via standard SQL (no custom tooling required)
- Clear error messages for debugging (no obscure codes)

---

## Success Metrics

### M1: Domain Compliance

**Target**: 0 `.net` references in MCP configurations
**Measurement**: CI validation passes, manual grep confirms

### M2: Execution Gating

**Target**: 100% of non-allowlisted executions rejected
**Measurement**: Audit logs show 0 successful executions for non-allowlisted IDs

### M3: Audit Coverage

**Target**: 100% of MCP tool calls logged
**Measurement**: Compare n8n execution logs vs `ops.run_events` (should match 1:1)

### M4: Rate Limit Effectiveness

**Target**: 95% of rate limit violations prevented
**Measurement**: 429 responses issued before quota exhaustion

---

## Dependencies

### D1: Supabase `ops.run_events` Table

**Status**: Already exists (per `ssot/integrations/n8n.yaml`)
**Action**: Verify schema supports required columns (user_id, idempotency_key)

### D2: n8n API Access

**Status**: API key exists in Supabase Vault (`n8n_api_key`)
**Action**: Verify API can query workflow IDs for validation

### D3: CI/CD Pipeline

**Status**: GitHub Actions infrastructure exists
**Action**: Create new workflow for allowlist validation

---

## Risks and Mitigations

### R1: Allowlist Maintenance Overhead

**Risk**: PR workflow for allowlist additions slows down automation deployment
**Impact**: Medium — delays in adding new workflows
**Mitigation**: Document fast-track approval process for low-risk workflows
**Probability**: High

### R2: Audit Logging Performance Impact

**Risk**: Supabase writes add latency to MCP tool calls
**Impact**: Low — <200ms overhead acceptable
**Mitigation**: Async audit logging (non-blocking), local queue if Supabase unavailable
**Probability**: Low

### R3: Allowlist Divergence from n8n Reality

**Risk**: Workflow deleted in n8n but remains in allowlist
**Impact**: Low — execution fails gracefully with 404
**Mitigation**: CI periodically validates allowlist against n8n API
**Probability**: Medium

---

## Open Questions

**Q1**: Should read-only tools (search, list) also require authentication?
- **Current stance**: No auth for read-only (org-scoped visibility sufficient)
- **Rationale**: Enables Claude Code context building without friction
- **Review**: Revisit if abuse detected

**Q2**: What approval process for high-risk workflows?
- **Current stance**: PR review + 1 approval minimum
- **Enhancement**: Consider requiring 2+ approvals for `risk_level: high`
- **Decision**: Defer to post-MVP iteration

**Q3**: Should MCP gateway support workflow creation?
- **Current stance**: No — creation is admin operation (use n8n UI)
- **Rationale**: MCP surface should be consumption-focused, not management
- **Review**: Maintain position unless compelling use case emerges

---

## References

- **Constitution**: `spec/n8n-mcp-gateway/constitution.md`
- **n8n Integration SSOT**: `ssot/integrations/n8n.yaml`
- **DNS SSOT**: `infra/dns/subdomain-registry.yaml`
- **Platform SSOT Rules**: `.claude/rules/ssot-platform.md`
- **Supabase Audit Schema**: See `ops.run_events` table schema

---

**This PRD defines WHAT to build. See `plan.md` for HOW to implement.**
