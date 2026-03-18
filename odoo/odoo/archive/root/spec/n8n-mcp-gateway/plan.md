# n8n MCP Gateway — Implementation Plan

> Technical implementation strategy for security hardening and governance controls.

**Version**: 1.0.0
**Status**: Draft
**Estimated Effort**: 16-24 hours (2-3 days)
**Dependencies**: Supabase access, n8n API access, GitHub Actions

---

## Architecture Overview

### Current State

```
Claude Code → MCP Client → supergateway
                            ↓
                https://n8n.insightpulseai.com/mcp-server/http
                            ↓
                     n8n MCP Server
                            ↓
                    n8n Workflow Execution
                            ↓
                    (No audit logging)
                    (No allowlist validation)
                    (No rate limiting)
```

### Target State

```
Claude Code → MCP Client → supergateway (updated config)
                            ↓
                https://n8n.insightpulseai.com/mcp-server/http
                            ↓
            [MCP Gateway Middleware] ← Allowlist SSOT
                    ↓                     (n8n_mcp_allowlist.yaml)
                    ├─ Validate workflow ID
                    ├─ Check rate limit
                    ├─ Log to ops.run_events
                    └─ Execute if approved
                            ↓
                    n8n Workflow Execution
                            ↓
                    Return execution status
                            ↓
            [MCP Gateway Middleware]
                    ↓
            Update ops.run_events (completion status)
```

---

## Implementation Phases

### Phase 1: Verification & Baseline

**Goal**: Verify current state and establish evidence baseline

**Tasks**:
1. Verify `~/.claude/mcp-servers.json` n8n config (domain check)
2. Test current MCP gateway functionality (baseline behavior)
3. Document current tool surface (which tools are exposed)
4. Create evidence bundle: `web/docs/evidence/<stamp>/n8n-mcp-baseline/`

**Deliverables**:
- Baseline evidence bundle with current configuration
- Tool inventory (`docs/n8n-mcp-tools-inventory.md`)
- Test execution logs (successful workflow execution proof)

**Duration**: 2-4 hours

---

### Phase 2: SSOT Allowlist Creation

**Goal**: Create and validate workflow allowlist SSOT

**Tasks**:
1. Create `ssot/integrations/n8n_mcp_allowlist.yaml`
2. Identify 3-5 initial workflows for allowlist (low-risk, commonly used)
3. Validate schema with YAML lint
4. Document allowlist format in `ssot/integrations/README.md`

**Deliverables**:
- `ssot/integrations/n8n_mcp_allowlist.yaml` (initial version)
- Schema documentation
- Example workflow entries

**File**: `ssot/integrations/n8n_mcp_allowlist.yaml`
```yaml
version: "1.0.0"
schema: ssot.n8n_mcp_allowlist.v1
last_updated: "2026-03-05"
description: "MCP-executable n8n workflow allowlist with security policies"

allowed_workflows:
  # Health check workflow (safe, read-only)
  - id: "01-health-check-uuid"
    name: "Platform Health Check"
    description: "Queries health endpoints for Odoo, Supabase, n8n"
    risk_level: low
    approval_required: false
    max_execution_time_seconds: 30
    added_by: "jgtolentino"
    added_date: "2026-03-05"

  # Git operations hub (medium risk, write operations)
  - id: "02-git-operations-uuid"
    name: "Git Operations Hub"
    description: "Create branches, PRs, commit evidence bundles"
    risk_level: medium
    approval_required: true
    max_execution_time_seconds: 120
    added_by: "jgtolentino"
    added_date: "2026-03-05"
```

**Duration**: 4-6 hours

---

### Phase 3: CI Validation Workflow

**Goal**: Automated validation of allowlist and domain hygiene

**Tasks**:
1. Create `.github/workflows/n8n-mcp-gateway-validation.yml`
2. Implement allowlist schema validation (YAML lint)
3. Implement domain hygiene check (grep for `.net`)
4. Implement workflow ID existence check (n8n API query)
5. Test workflow on PR

**Deliverables**:
- CI workflow file
- Validation script: `scripts/ci/validate_n8n_mcp_allowlist.py`
- Test PR demonstrating validation

**File**: `.github/workflows/n8n-mcp-gateway-validation.yml`
```yaml
name: n8n MCP Gateway Validation

on:
  pull_request:
    paths:
      - 'ssot/integrations/n8n_mcp_allowlist.yaml'
      - '.claude/mcp-servers.json'
      - '.github/workflows/n8n-mcp-gateway-validation.yml'
  push:
    branches: [main]
    paths:
      - 'ssot/integrations/n8n_mcp_allowlist.yaml'
  workflow_dispatch:

jobs:
  validate:
    name: "🛡️ Validate n8n MCP Gateway Configuration"
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: |
          pip install pyyaml requests

      - name: Validate Allowlist Schema
        run: |
          python scripts/ci/validate_n8n_mcp_allowlist.py

      - name: Check Domain Hygiene
        run: |
          # Fail if deprecated .net domain found in MCP configs
          if grep -r "insightpulseai\.net.*mcp" ~/.claude/mcp-servers.json 2>/dev/null; then
            echo "❌ ERROR: Deprecated .net domain found in MCP config"
            exit 1
          fi
          echo "✅ Domain hygiene check passed"

      - name: Verify Workflow IDs Exist
        env:
          N8N_API_KEY: ${{ secrets.N8N_API_KEY }}
          N8N_BASE_URL: https://n8n.insightpulseai.com
        run: |
          python scripts/ci/check_n8n_workflow_ids.py
```

**File**: `scripts/ci/validate_n8n_mcp_allowlist.py`
```python
#!/usr/bin/env python3
"""Validate n8n MCP allowlist schema and content."""

import yaml
import sys
from pathlib import Path

def validate_allowlist():
    allowlist_path = Path("ssot/integrations/n8n_mcp_allowlist.yaml")

    if not allowlist_path.exists():
        print("❌ Allowlist file not found")
        sys.exit(1)

    with open(allowlist_path) as f:
        data = yaml.safe_load(f)

    # Schema validation
    required_fields = ["version", "schema", "allowed_workflows"]
    for field in required_fields:
        if field not in data:
            print(f"❌ Missing required field: {field}")
            sys.exit(1)

    # Workflow entry validation
    for workflow in data["allowed_workflows"]:
        required_workflow_fields = ["id", "name", "risk_level", "approval_required"]
        for field in required_workflow_fields:
            if field not in workflow:
                print(f"❌ Workflow missing required field '{field}': {workflow.get('name', 'unknown')}")
                sys.exit(1)

        # Validate risk_level enum
        if workflow["risk_level"] not in ["low", "medium", "high"]:
            print(f"❌ Invalid risk_level '{workflow['risk_level']}' in workflow: {workflow['name']}")
            sys.exit(1)

    print(f"✅ Allowlist validation passed ({len(data['allowed_workflows'])} workflows)")

if __name__ == "__main__":
    validate_allowlist()
```

**Duration**: 4-6 hours

---

### Phase 4: Audit Logging Implementation

**Goal**: Log all MCP tool calls to Supabase `ops.run_events`

**Tasks**:
1. Verify `ops.run_events` table schema supports required columns
2. Create audit logging helper function (Python or n8n sub-workflow)
3. Integrate audit logging into MCP gateway middleware
4. Test audit logging with sample workflow execution
5. Verify idempotency key prevents duplicates

**Deliverables**:
- Audit logging integration (n8n webhook or middleware script)
- Test evidence showing audit records in `ops.run_events`
- Idempotency test (duplicate execution prevented)

**Implementation** (n8n webhook with Supabase node):
```javascript
// n8n Function node: Log MCP Tool Call
const supabaseClient = $env.SUPABASE_SERVICE_ROLE_KEY;

const auditEvent = {
  source: 'n8n-mcp-gateway',
  event_type: 'execute_workflow',
  event_data: {
    workflow_id: $input.first().json.workflow_id,
    workflow_name: $workflow.name,
    input_data: $input.first().json.input_data,
    execution_id: $executionId,
    mcp_session_id: $input.first().json.session_id
  },
  user_id: 'claude-code-user',  // TODO: Extract from MCP session context
  idempotency_key: `n8n:mcp:${$input.first().json.workflow_id}:${$executionId}`,
  status: 'running',
  created_at: new Date().toISOString()
};

return [{ json: auditEvent }];
```

**Duration**: 6-8 hours

---

### Phase 5: Rate Limiting

**Goal**: Enforce execution quotas per user/session

**Tasks**:
1. Implement rate limit check (query `ops.run_events` for recent calls)
2. Add rate limit middleware to MCP gateway
3. Test rate limit enforcement (11th execution rejected)
4. Document rate limit configuration

**Deliverables**:
- Rate limiting middleware (n8n sub-workflow or Python script)
- Test evidence showing 429 responses after quota exhaustion
- Configuration documentation

**Implementation** (n8n Function node):
```javascript
// n8n Function node: Check Rate Limit
const userId = $input.first().json.user_id || 'claude-code-user';
const now = new Date();
const oneHourAgo = new Date(now - 3600 * 1000);

// Query ops.run_events for recent executions by this user
const supabaseUrl = $env.SUPABASE_URL;
const supabaseKey = $env.SUPABASE_SERVICE_ROLE_KEY;

const response = await fetch(`${supabaseUrl}/rest/v1/run_events`, {
  method: 'GET',
  headers: {
    'apikey': supabaseKey,
    'Authorization': `Bearer ${supabaseKey}`,
    'Content-Type': 'application/json'
  },
  params: {
    user_id: `eq.${userId}`,
    event_type: 'eq.execute_workflow',
    created_at: `gte.${oneHourAgo.toISOString()}`,
    select: 'count'
  }
});

const data = await response.json();
const executionCount = data[0]?.count || 0;

if (executionCount >= 10) {
  throw new Error('RATE_LIMIT_EXCEEDED: 10 executions/hour limit reached');
}

return [{ json: { allowed: true, current_usage: executionCount } }];
```

**Duration**: 4-6 hours

---

### Phase 6: Allowlist Gating

**Goal**: Reject non-allowlisted workflow executions

**Tasks**:
1. Implement allowlist validation middleware
2. Read allowlist from `ssot/integrations/n8n_mcp_allowlist.yaml`
3. Return 403 Forbidden for non-allowlisted workflow IDs
4. Test with allowlisted and non-allowlisted workflows
5. Document error responses

**Deliverables**:
- Allowlist gating middleware (n8n sub-workflow or Python script)
- Test evidence (allowlisted succeeds, non-allowlisted fails)
- Error response documentation

**Implementation** (n8n Function node):
```javascript
// n8n Function node: Validate Workflow Allowlist
const fs = require('fs');
const yaml = require('js-yaml');

const workflowId = $input.first().json.workflow_id;

// Load allowlist from SSOT
const allowlistPath = '/path/to/repo/ssot/integrations/n8n_mcp_allowlist.yaml';
const allowlistContent = fs.readFileSync(allowlistPath, 'utf8');
const allowlist = yaml.load(allowlistContent);

const allowedIds = allowlist.allowed_workflows.map(w => w.id);

if (!allowedIds.includes(workflowId)) {
  throw new Error(`WORKFLOW_NOT_ALLOWLISTED: ${workflowId} is not pre-approved for MCP execution`);
}

// Return workflow metadata for logging
const workflowMeta = allowlist.allowed_workflows.find(w => w.id === workflowId);
return [{ json: { allowed: true, workflow_meta: workflowMeta } }];
```

**Duration**: 4-6 hours

---

## Technical Decisions

### TD1: MCP Gateway Implementation Approach

**Options**:
1. **n8n Webhook Middleware**: Implement validation/logging as n8n sub-workflows
2. **Standalone Python Service**: Create dedicated MCP gateway service
3. **Nginx Lua Middleware**: Add validation at reverse proxy layer

**Decision**: Option 1 (n8n Webhook Middleware)

**Rationale**:
- Leverages existing n8n infrastructure
- No additional deployment complexity
- Audit logging via Supabase node (built-in)
- Allowlist YAML readable from n8n Function node

**Trade-offs**:
- n8n execution overhead (50-100ms per validation)
- Requires n8n to be available for MCP gateway to function
- Harder to debug than standalone service

---

### TD2: Allowlist Storage Location

**Options**:
1. **Git SSOT**: `ssot/integrations/n8n_mcp_allowlist.yaml`
2. **Supabase Table**: Dynamic allowlist in database
3. **n8n Credentials**: Workflow IDs stored in n8n credential store

**Decision**: Option 1 (Git SSOT)

**Rationale**:
- Version-controlled (audit trail for changes)
- PR workflow enforces review before allowlist additions
- CI validation ensures schema compliance
- Aligns with existing SSOT patterns (DNS, n8n integration)

**Trade-offs**:
- Requires git pull/repo sync to update allowlist
- Cannot add workflows dynamically at runtime
- PR overhead for urgent workflow additions

---

### TD3: Rate Limiting Granularity

**Options**:
1. **Per User**: Track executions by user ID (from MCP session)
2. **Per Session**: Track executions by MCP session ID
3. **Global**: Single quota for all MCP executions

**Decision**: Option 1 (Per User)

**Rationale**:
- Prevents single user from monopolizing execution quota
- Aligns with audit logging (user attribution)
- Fair resource allocation across users

**Trade-offs**:
- Requires user ID extraction from MCP session context
- More complex than global rate limiting
- User ID may not be available in all MCP clients

---

## File Structure

### New Files Created

```
spec/n8n-mcp-gateway/
├── constitution.md                    # ✅ Created
├── prd.md                             # ✅ Created
├── plan.md                            # 🔄 This file
└── tasks.md                           # Next

ssot/integrations/
├── n8n.yaml                           # ✅ Exists
└── n8n_mcp_allowlist.yaml             # 🆕 To create

.github/workflows/
└── n8n-mcp-gateway-validation.yml     # 🆕 To create

scripts/ci/
├── validate_n8n_mcp_allowlist.py      # 🆕 To create
└── check_n8n_workflow_ids.py          # 🆕 To create

web/docs/evidence/<stamp>/
└── n8n-mcp-baseline/                  # 🆕 To create
    ├── IMPLEMENTATION_SUMMARY.md
    └── logs/
        ├── current-config.log
        ├── tool-inventory.log
        └── test-execution.log
```

---

## Testing Strategy

### Unit Tests

**Target**: Individual middleware components

**Tests**:
- Allowlist validation logic (Python unit tests)
- Rate limit calculation (mock `ops.run_events` queries)
- Audit logging format validation

**Tool**: pytest
**Location**: `tests/unit/n8n_mcp_gateway/`

---

### Integration Tests

**Target**: End-to-end MCP tool execution

**Tests**:
1. Execute allowlisted workflow → Success + audit log created
2. Execute non-allowlisted workflow → 403 Forbidden + audit log (rejected)
3. Execute 11th workflow in 1 hour → 429 Rate Limit Exceeded
4. Verify idempotency (duplicate execution ID → no duplicate audit log)

**Tool**: pytest + requests library
**Location**: `tests/integration/n8n_mcp_gateway/`

---

### CI Tests

**Target**: Validation pipeline

**Tests**:
- Allowlist schema validation (CI workflow)
- Domain hygiene check (grep for `.net`)
- Workflow ID existence check (n8n API query)

**Tool**: GitHub Actions
**Location**: `.github/workflows/n8n-mcp-gateway-validation.yml`

---

## Rollout Plan

### Phase A: Development (Week 1)

**Day 1-2**: Baseline + SSOT Allowlist
- Verify current state, create evidence baseline
- Create `n8n_mcp_allowlist.yaml` with 3-5 initial workflows
- Test allowlist loading from n8n Function node

**Day 3-4**: CI Validation
- Implement validation workflow
- Create validation scripts (Python)
- Test CI on PR

**Day 5**: Audit Logging
- Integrate Supabase audit logging
- Test audit log creation
- Verify idempotency

### Phase B: Hardening (Week 2)

**Day 1-2**: Rate Limiting
- Implement rate limit middleware
- Test quota enforcement
- Document rate limit errors

**Day 3**: Allowlist Gating
- Implement allowlist validation
- Test rejection of non-allowlisted workflows
- Document error responses

**Day 4**: Integration Testing
- End-to-end tests for all features
- Performance testing (latency measurement)
- Load testing (concurrent executions)

**Day 5**: Documentation + Evidence
- Create comprehensive evidence bundle
- Update documentation (`docs/ops/N8N_MCP_GATEWAY.md`)
- PR review and approval

### Phase C: Deployment (Week 3)

**Day 1**: Staging Deployment
- Deploy to staging environment
- Test with real Claude Code sessions
- Monitor audit logs for issues

**Day 2-3**: Production Deployment
- Deploy to production (gradual rollout)
- Monitor rate limit hits and allowlist rejections
- Address any issues

**Day 4-5**: Stabilization
- Performance tuning if needed
- Documentation updates based on production behavior
- Postmortem and lessons learned

---

## Success Criteria

### SC1: Domain Hygiene

**Metric**: 0 `.net` references in MCP configs
**Validation**: `grep -r "insightpulseai\.net" ~/.claude/mcp-servers.json`; exit code 1 (not found)

### SC2: Allowlist Enforcement

**Metric**: 100% of non-allowlisted executions rejected
**Validation**: Integration test shows 403 response for non-allowlisted workflow

### SC3: Audit Coverage

**Metric**: 100% of MCP tool calls logged
**Validation**: Query `ops.run_events` for test session → match execution count

### SC4: Rate Limiting

**Metric**: 95% of quota violations prevented
**Validation**: Integration test shows 429 response on 11th execution

### SC5: Performance

**Metric**: <2 second response time (95th percentile)
**Validation**: Performance test with 100 concurrent executions

---

## Risks

### R1: Supabase Audit Logging Latency

**Mitigation**: Async audit logging, local queue if Supabase unavailable
**Contingency**: Degrade gracefully (log warning, allow execution)

### R2: Allowlist Staleness

**Mitigation**: CI validates workflow IDs exist in n8n weekly
**Contingency**: Remove stale entries from allowlist (PR + approval)

### R3: Rate Limit False Positives

**Mitigation**: Clear documentation of quota limits
**Contingency**: Temporary quota increase for power users (via allowlist)

---

## Next Steps

1. Create `tasks.md` — actionable task breakdown for implementation
2. Create baseline evidence bundle (Phase 1)
3. Implement `n8n_mcp_allowlist.yaml` (Phase 2)
4. Begin CI validation workflow (Phase 3)

---

**This plan defines HOW to implement. See `tasks.md` for detailed task breakdown.**
