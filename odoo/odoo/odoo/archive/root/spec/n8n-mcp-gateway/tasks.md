# n8n MCP Gateway — Task Breakdown

> Actionable implementation tasks generated from `plan.md`.

**Status**: Draft
**Generated**: 2026-03-05
**Total Tasks**: 28
**Estimated Effort**: 16-24 hours

---

## Phase 1: Verification & Baseline (4 hours)

### Task 1.1: Verify MCP Configuration Domain

**Description**: Confirm `~/.claude/mcp-servers.json` uses `.com` domain for n8n
**Acceptance Criteria**:
- Read `~/.claude/mcp-servers.json` line 176 (n8n config)
- Verify URL is `https://n8n.insightpulseai.com/mcp-server/http`
- Document finding in evidence bundle

**Commands**:
```bash
grep "n8n.insightpulseai" ~/.claude/mcp-servers.json
# Expected output should show .com, not .net
```

**Estimated Time**: 0.5 hours

---

### Task 1.2: Test Current MCP Gateway

**Description**: Execute a test workflow via MCP to establish baseline behavior
**Acceptance Criteria**:
- Successfully trigger a workflow via Claude Code MCP interface
- Document execution ID and response
- Capture logs for baseline evidence

**Commands**:
```bash
# Via Claude Code MCP session
# Execute: "Use n8n MCP to run health check workflow"
# Document execution logs
```

**Estimated Time**: 1 hour

---

### Task 1.3: Document Current Tool Surface

**Description**: List all n8n MCP tools currently exposed
**Acceptance Criteria**:
- Query MCP server for available tools
- Create inventory document: `docs/n8n-mcp-tools-inventory.md`
- Classify tools by privilege level (read/execute/admin)

**Deliverable**: `docs/n8n-mcp-tools-inventory.md`

**Estimated Time**: 1 hour

---

### Task 1.4: Create Baseline Evidence Bundle

**Description**: Create timestamped evidence bundle for current state
**Acceptance Criteria**:
- Create directory: `web/docs/evidence/<stamp>/n8n-mcp-baseline/logs/`
- Save current MCP config
- Save tool inventory
- Save test execution logs

**Commands**:
```bash
STAMP=$(TZ='Asia/Manila' date +%Y%m%d-%H%M%z)
mkdir -p "web/docs/evidence/${STAMP}/n8n-mcp-baseline/logs"

# Copy current config
cp ~/.claude/mcp-servers.json "web/docs/evidence/${STAMP}/n8n-mcp-baseline/logs/mcp-servers-current.json"

# Save tool inventory
# (manual step - document tools in inventory file)
```

**Estimated Time**: 1.5 hours

---

## Phase 2: SSOT Allowlist Creation (6 hours)

### Task 2.1: Identify Initial Workflows for Allowlist

**Description**: Select 3-5 low-risk workflows for initial allowlist
**Acceptance Criteria**:
- Query n8n for workflow list
- Select workflows: health-check, git-operations, test-runner (or similar)
- Document workflow IDs, names, descriptions

**Commands**:
```bash
# Query n8n API for workflows
curl -H "X-N8N-API-KEY: ${N8N_API_KEY}" \
  https://n8n.insightpulseai.com/api/v1/workflows | jq
```

**Estimated Time**: 1 hour

---

### Task 2.2: Create Allowlist SSOT File

**Description**: Create `ssot/integrations/n8n_mcp_allowlist.yaml`
**Acceptance Criteria**:
- File created with correct schema (version, allowed_workflows)
- 3-5 workflow entries with all required fields
- YAML syntax valid (yamllint pass)

**File**: `ssot/integrations/n8n_mcp_allowlist.yaml`

**Template**:
```yaml
version: "1.0.0"
schema: ssot.n8n_mcp_allowlist.v1
last_updated: "2026-03-05"

allowed_workflows:
  - id: "<workflow-uuid>"
    name: "Workflow Name"
    description: "What it does"
    risk_level: low
    approval_required: false
    max_execution_time_seconds: 60
    added_by: "jgtolentino"
    added_date: "2026-03-05"
```

**Estimated Time**: 2 hours

---

### Task 2.3: Document Allowlist Format

**Description**: Add allowlist documentation to `ssot/integrations/README.md`
**Acceptance Criteria**:
- Document allowlist schema
- Explain workflow addition process
- Provide examples of low/medium/high risk workflows

**File**: `ssot/integrations/README.md` (update or create)

**Estimated Time**: 1.5 hours

---

### Task 2.4: Validate Allowlist Syntax

**Description**: Test allowlist YAML syntax and schema compliance
**Acceptance Criteria**:
- YAML lint passes (`yamllint n8n_mcp_allowlist.yaml`)
- All required fields present
- risk_level enum values valid (low/medium/high)

**Commands**:
```bash
yamllint ssot/integrations/n8n_mcp_allowlist.yaml
python3 -c "import yaml; yaml.safe_load(open('ssot/integrations/n8n_mcp_allowlist.yaml'))"
```

**Estimated Time**: 0.5 hours

---

### Task 2.5: Test Allowlist Loading

**Description**: Verify allowlist can be read from file system (n8n context)
**Acceptance Criteria**:
- Create test n8n Function node that reads allowlist YAML
- Verify workflow IDs can be extracted
- Document loading pattern for production use

**Estimated Time**: 1 hour

---

## Phase 3: CI Validation Workflow (6 hours)

### Task 3.1: Create CI Workflow File

**Description**: Create `.github/workflows/n8n-mcp-gateway-validation.yml`
**Acceptance Criteria**:
- Workflow triggers on PR + push to main
- Paths filter for allowlist and MCP config changes
- Python 3.12 setup step

**File**: `.github/workflows/n8n-mcp-gateway-validation.yml`

**Estimated Time**: 1 hour

---

### Task 3.2: Implement Allowlist Validation Script

**Description**: Create `scripts/ci/validate_n8n_mcp_allowlist.py`
**Acceptance Criteria**:
- Validates YAML syntax
- Checks required fields (id, name, risk_level, etc.)
- Validates enum values (risk_level: low/medium/high)
- Exit code 0 on success, 1 on failure

**File**: `scripts/ci/validate_n8n_mcp_allowlist.py`

**Estimated Time**: 2 hours

---

### Task 3.3: Implement Domain Hygiene Check

**Description**: Add domain validation step to CI workflow
**Acceptance Criteria**:
- Grep for `insightpulseai.net.*mcp` in MCP configs
- Fail if deprecated `.net` domain found
- Pass if only `.com` domain present

**Workflow Step**:
```yaml
- name: Check Domain Hygiene
  run: |
    if grep -r "insightpulseai\.net.*mcp" ~/.claude/mcp-servers.json 2>/dev/null; then
      echo "❌ ERROR: Deprecated .net domain found"
      exit 1
    fi
    echo "✅ Domain hygiene check passed"
```

**Estimated Time**: 0.5 hours

---

### Task 3.4: Implement Workflow ID Existence Check

**Description**: Create `scripts/ci/check_n8n_workflow_ids.py`
**Acceptance Criteria**:
- Query n8n API for each workflow ID in allowlist
- Fail if any workflow ID not found in n8n
- Report missing workflows clearly

**File**: `scripts/ci/check_n8n_workflow_ids.py`

**API Query**:
```python
import requests
import os

n8n_api_key = os.getenv("N8N_API_KEY")
n8n_base_url = os.getenv("N8N_BASE_URL")

response = requests.get(
    f"{n8n_base_url}/api/v1/workflows/{workflow_id}",
    headers={"X-N8N-API-KEY": n8n_api_key}
)

if response.status_code == 404:
    print(f"❌ Workflow not found: {workflow_id}")
    sys.exit(1)
```

**Estimated Time**: 2 hours

---

### Task 3.5: Test CI Workflow on PR

**Description**: Create test PR to validate CI workflow execution
**Acceptance Criteria**:
- PR with allowlist change triggers workflow
- All validation steps execute
- Workflow passes on valid allowlist
- Workflow fails on invalid allowlist (negative test)

**Estimated Time**: 0.5 hours

---

## Phase 4: Audit Logging Implementation (8 hours)

### Task 4.1: Verify ops.run_events Schema

**Description**: Confirm Supabase table supports required columns
**Acceptance Criteria**:
- Table `ops.run_events` exists
- Columns: source, event_type, event_data (JSONB), user_id, idempotency_key (UNIQUE), status, created_at

**Commands**:
```sql
-- Connect to Supabase PostgreSQL
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_schema = 'ops' AND table_name = 'run_events';
```

**Estimated Time**: 0.5 hours

---

### Task 4.2: Create Audit Logging Helper Function

**Description**: Create n8n sub-workflow for audit logging
**Acceptance Criteria**:
- Sub-workflow accepts: event_type, workflow_id, input_data, user_id
- Writes to `ops.run_events` via Supabase node
- Returns success/failure status

**n8n Workflow Name**: `MCP Gateway - Audit Logger`

**Estimated Time**: 2 hours

---

### Task 4.3: Integrate Audit Logging in MCP Gateway

**Description**: Add audit logging to MCP gateway middleware
**Acceptance Criteria**:
- Every MCP tool call triggers audit log write
- Audit log created BEFORE execution (status: 'running')
- Audit log updated AFTER execution (status: 'success'/'failed')

**Estimated Time**: 2.5 hours

---

### Task 4.4: Test Audit Logging

**Description**: Execute test workflow and verify audit record creation
**Acceptance Criteria**:
- Execute workflow via MCP
- Query `ops.run_events` for record matching execution ID
- Verify all fields populated correctly

**Query**:
```sql
SELECT * FROM ops.run_events
WHERE source = 'n8n-mcp-gateway'
ORDER BY created_at DESC
LIMIT 10;
```

**Estimated Time**: 1 hour

---

### Task 4.5: Test Idempotency

**Description**: Verify duplicate executions don't create duplicate audit logs
**Acceptance Criteria**:
- Execute same workflow with same execution ID twice
- Only 1 audit record created (idempotency_key UNIQUE constraint enforced)
- Second attempt returns existing record or 409 Conflict

**Estimated Time**: 1 hour

---

### Task 4.6: Document Audit Log Schema

**Description**: Add audit logging documentation to `docs/ops/N8N_MCP_GATEWAY.md`
**Acceptance Criteria**:
- Document event_data JSONB structure
- Provide example audit records
- Explain idempotency key format

**Estimated Time**: 1 hour

---

## Phase 5: Rate Limiting (6 hours)

### Task 5.1: Implement Rate Limit Check Function

**Description**: Create n8n Function node to check execution quota
**Acceptance Criteria**:
- Query `ops.run_events` for user's executions in last 1 hour
- Count executions where event_type = 'execute_workflow'
- Return allowed: true/false

**n8n Function Node**: `Check Rate Limit`

**Estimated Time**: 2 hours

---

### Task 5.2: Integrate Rate Limiting in MCP Gateway

**Description**: Add rate limit check before workflow execution
**Acceptance Criteria**:
- Rate limit check executes before audit logging
- If quota exceeded, return 429 Too Many Requests
- If quota OK, proceed with execution

**Estimated Time**: 1.5 hours

---

### Task 5.3: Test Rate Limit Enforcement

**Description**: Execute 11 workflows in 1 hour, verify 11th rejected
**Acceptance Criteria**:
- First 10 executions succeed
- 11th execution returns 429 status code
- Error message includes retry_after_seconds

**Estimated Time**: 1.5 hours

---

### Task 5.4: Document Rate Limit Configuration

**Description**: Add rate limit documentation to `docs/ops/N8N_MCP_GATEWAY.md`
**Acceptance Criteria**:
- Document quota limits (10 executions/hour)
- Explain error responses (429 format)
- Document quota reset behavior

**Estimated Time**: 1 hour

---

## Phase 6: Allowlist Gating (6 hours)

### Task 6.1: Implement Allowlist Validation Function

**Description**: Create n8n Function node to validate workflow ID against allowlist
**Acceptance Criteria**:
- Load allowlist from `ssot/integrations/n8n_mcp_allowlist.yaml`
- Check if workflow_id exists in allowed_workflows
- Return allowed: true/false + workflow metadata

**n8n Function Node**: `Validate Workflow Allowlist`

**Estimated Time**: 2 hours

---

### Task 6.2: Integrate Allowlist Gating in MCP Gateway

**Description**: Add allowlist validation before workflow execution
**Acceptance Criteria**:
- Allowlist check executes after rate limit check
- If not allowlisted, return 403 Forbidden
- If allowlisted, proceed with execution

**Estimated Time**: 1.5 hours

---

### Task 6.3: Test Allowlist Enforcement

**Description**: Execute allowlisted and non-allowlisted workflows
**Acceptance Criteria**:
- Allowlisted workflow executes successfully
- Non-allowlisted workflow returns 403 status code
- Error message includes allowlist submission instructions

**Estimated Time**: 1.5 hours

---

### Task 6.4: Document Allowlist Gating

**Description**: Add allowlist documentation to `docs/ops/N8N_MCP_GATEWAY.md`
**Acceptance Criteria**:
- Document allowlist location and schema
- Explain workflow addition process (PR workflow)
- Document error responses (403 format)

**Estimated Time**: 1 hour

---

## Phase 7: Integration & Evidence (4 hours)

### Task 7.1: End-to-End Integration Test

**Description**: Test complete MCP gateway flow with all features enabled
**Acceptance Criteria**:
- Allowlisted workflow executes successfully
- Audit log created in `ops.run_events`
- Rate limit enforced after 10 executions
- Non-allowlisted workflow rejected with 403

**Estimated Time**: 1.5 hours

---

### Task 7.2: Performance Testing

**Description**: Measure MCP gateway latency with all middleware enabled
**Acceptance Criteria**:
- Execute 100 workflows, measure p95 response time
- Verify <2 second response time (95th percentile)
- Document performance baseline

**Estimated Time**: 1 hour

---

### Task 7.3: Create Final Evidence Bundle

**Description**: Create comprehensive evidence bundle for implementation
**Acceptance Criteria**:
- Directory: `web/docs/evidence/<stamp>/n8n-mcp-hardening/logs/`
- Logs: baseline config, allowlist YAML, audit logs, test results
- Summary: IMPLEMENTATION_SUMMARY.md with STATUS=COMPLETE

**Estimated Time**: 1 hour

---

### Task 7.4: Update Documentation

**Description**: Create comprehensive operations guide
**Acceptance Criteria**:
- Create `docs/ops/N8N_MCP_GATEWAY.md`
- Document all features (allowlist, audit, rate limiting)
- Include troubleshooting guide
- Add runbook for common operations

**Estimated Time**: 0.5 hours

---

## Phase 8: Deployment (Deferred to Implementation)

Tasks 8.1-8.5 deferred until implementation phase begins.

---

## Task Dependencies

```
Phase 1 (Baseline)
  ↓
Phase 2 (Allowlist SSOT)
  ↓
Phase 3 (CI Validation) ← Can run in parallel with Phase 4-6
  ↓
Phase 4 (Audit Logging)
  ↓
Phase 5 (Rate Limiting) ← Depends on Phase 4 (audit table)
  ↓
Phase 6 (Allowlist Gating)
  ↓
Phase 7 (Integration & Evidence)
  ↓
Phase 8 (Deployment)
```

---

## Task Summary by Phase

| Phase | Tasks | Estimated Hours |
|-------|-------|-----------------|
| Phase 1: Baseline | 4 tasks | 4 hours |
| Phase 2: Allowlist | 5 tasks | 6 hours |
| Phase 3: CI Validation | 5 tasks | 6 hours |
| Phase 4: Audit Logging | 6 tasks | 8 hours |
| Phase 5: Rate Limiting | 4 tasks | 6 hours |
| Phase 6: Allowlist Gating | 4 tasks | 6 hours |
| Phase 7: Integration | 4 tasks | 4 hours |
| **Total** | **32 tasks** | **40 hours** |

---

## Next Steps

1. Review task breakdown for completeness
2. Assign priorities (P0, P1, P2)
3. Begin Phase 1 execution (baseline evidence)
4. Create tracking issue: `[Feature] n8n MCP Gateway Security Hardening`

---

**This task breakdown is ready for execution. See `spec/n8n-mcp-gateway/checklist.md` for quality validation checklist (to be created).**
