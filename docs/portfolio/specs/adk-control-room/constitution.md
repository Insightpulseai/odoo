# ADK Control Room — Constitution

## Purpose

The Control Room is the canonical orchestration plane that turns docs/specs/config → code → jobs → lineage → audit artifacts across Odoo, Supabase, n8n, and CI/CD.

## Hard Contracts

### 1. Spec-First
- No Control Room feature may be implemented without a spec bundle
- All specs must follow the Spec Kit structure (constitution, prd, plan, tasks)
- Spec changes must go through Continue PR automation

### 2. Agents Are Code
- All agents must be versioned using ADK-TS
- Agents must have TypeScript type definitions
- Agent behavior must be testable (unit + integration)
- No prompt spaghetti — all agent instructions must be declarative

### 3. Tool Boundaries
- Agents may only act through declared tools
- Tool contracts must be TypeScript interfaces
- Tools must validate inputs before execution
- No agent can bypass tool contracts

### 4. Idempotency
- Jobs must be safely re-runnable
- Idempotency keys required for all state mutations
- Duplicate job submissions must be detected and deduplicated
- Retry logic must use exponential backoff

### 5. Lineage Required
- Every job writes lineage metadata
- Upstream/downstream dependencies must be explicit
- Artifacts must be linked to job runs
- Lineage graph must be queryable (Databricks-style)

### 6. Business State Lives in Odoo
- Control Room orchestrates, never owns business truth
- Finance data canonical source: Odoo CE 18
- Approvals must come from Odoo workflows
- Period locks must be respected
- All business mutations must audit to Odoo

## Forbidden

### Prohibited Actions
1. **Direct DB Mutation Outside Migrations**
   - Control Room agents cannot execute raw SQL
   - Schema changes require Supabase migrations
   - Odoo schema changes require module upgrades

2. **Agents Executing Shell/Network Calls Outside Tool Contracts**
   - No `exec()`, `spawn()`, or `system()` calls
   - Network access only through declared HTTP tools
   - File system access only through declared storage tools

3. **Hidden Side Effects**
   - Everything must emit artifacts + logs
   - Silent failures are forbidden
   - All state changes must be observable
   - No undocumented API calls

## Quality Gates

### Pre-Deployment
- ✅ Spec bundle complete
- ✅ Tool contracts defined
- ✅ Agent tests pass
- ✅ Lineage validation complete

### Runtime
- ✅ Idempotency key validation
- ✅ Approval gate check (if required)
- ✅ Period lock check (if finance)
- ✅ Artifact upload confirmation

### Post-Execution
- ✅ Lineage written
- ✅ Logs uploaded
- ✅ Metrics recorded
- ✅ Notifications sent

## Governance

### Change Control
- Spec changes require PR approval
- Agent code changes require unit tests
- Tool contract changes require version bump
- Breaking changes require migration plan

### Security
- No secrets in code or logs
- Secrets must come from Supabase Vault
- API keys rotate every 90 days
- Service accounts have minimum required permissions

### Compliance
- All job runs logged for 7 years (BIR requirement)
- Audit trail immutable
- RBAC enforced (Odoo roles)
- Data retention follows finance policy

## Non-Negotiable Principles

1. **Determinism**: Same inputs → same outputs
2. **Auditability**: Every action traceable
3. **Reversibility**: Rollback capability required
4. **Transparency**: Observable at every layer
5. **Testability**: All components must be testable

## Violation Handling

### Spec Violations
- PR rejected by CI
- Deployment blocked
- Change author notified

### Runtime Violations
- Job marked as failed
- Alert sent to on-call
- Automatic rollback triggered

### Security Violations
- Immediate job termination
- Secrets rotated
- Incident report required
- Audit log frozen

## Version History

- **v1.0.0** (2025-11-24): Initial constitution
  - Core contracts established
  - Tool boundaries defined
  - Governance model set
