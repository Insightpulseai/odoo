# PPM Clarity — Task Breakdown

> Actionable tasks derived from the implementation plan.
> Each task has clear inputs, outputs, and completion criteria.

---

## Phase 1: Spec Bundle

### Task 1.1: Create Spec Kit Artifacts
- **Input**: PRD specification, Plane MCP docs, Odoo project model
- **Output**: constitution.md, prd.md, plan.md, tasks.md
- **Done when**: All 4 files pass `scripts/check-spec-kit.sh`

---

## Phase 2: Supabase Schema

### Task 2.1: Create SSOT Migration
- **Input**: Field ownership contract, sync state machine
- **Output**: `supabase/migrations/20260305_create_ppm_clarity_schema.sql`
- **Tables**: `ops.work_item_links`, `ops.work_item_events`
- **Functions**: `upsert_work_item_link`, `append_work_item_event`, `get_sync_conflicts`
- **Done when**: Migration applies without errors, RLS active

### Task 2.2: Validate RLS Policies
- **Input**: Migration file
- **Output**: Verified service_role-only access
- **Done when**: Non-service-role queries return empty results

### Task 2.3: Create RPC Test Harness
- **Input**: RPC function signatures
- **Output**: SQL test script for upsert/append/query operations
- **Done when**: All RPC functions return expected results

---

## Phase 3: Integration Clients

### Task 3.1: Build Odoo XML-RPC Client
- **Input**: Odoo XML-RPC API docs, project.task model
- **Output**: `scripts/ppm/odoo_client.py`
- **Methods**: `create_task`, `update_task`, `get_task_details`, `calculate_hash`
- **Done when**: Unit tests pass with mocked XML-RPC responses

### Task 3.2: Build Plane MCP Client Wrapper
- **Input**: Plane MCP server 55+ tools, self-hosted config
- **Output**: `scripts/ppm/plane_mcp_client.py`
- **Methods**: `get_issue`, `update_issue`, `list_issues`, `calculate_hash`
- **Done when**: Unit tests pass with mocked MCP responses

### Task 3.3: Build Sync Engine
- **Input**: Field ownership rules, hash calculation, idempotency contract
- **Output**: `scripts/ppm/sync_engine.py`
- **Methods**: `plane_to_odoo`, `odoo_to_plane`, `reconcile`
- **Done when**: All sync scenarios pass (create, update, idempotent, conflict)

### Task 3.4: Build Slack Notifier
- **Input**: Pulser Slack patterns (PR #441), notification types
- **Output**: `scripts/ppm/slack_notifier.py`
- **Methods**: `notify_sync_success`, `notify_sync_failure`, `notify_conflict`, `notify_reconciliation_report`
- **Done when**: Unit tests pass with mocked Slack SDK

---

## Phase 4: n8n Workflows

### Task 4.1: Plane → Odoo Workflow
- **Input**: Plane webhook events, sync engine
- **Output**: `automations/n8n/workflows/ppm-clarity-plane-to-odoo.json`
- **Trigger**: Webhook (HMAC-validated)
- **Done when**: Workflow deploys and processes test event

### Task 4.2: Odoo → Plane Workflow
- **Input**: Odoo task completion, sync engine
- **Output**: `automations/n8n/workflows/ppm-clarity-odoo-to-plane.json`
- **Trigger**: Cron (every 10 minutes)
- **Done when**: Workflow deploys and detects completed tasks

### Task 4.3: Reconciliation Workflow
- **Input**: get_sync_conflicts RPC, field ownership rules
- **Output**: `automations/n8n/workflows/ppm-clarity-reconciliation.json`
- **Trigger**: Cron (2 AM UTC+08:00 daily)
- **Done when**: Workflow deploys, detects drift, posts daily report

### Task 4.4: Slack Commands Workflow
- **Input**: Slash command payloads, sync engine
- **Output**: `automations/n8n/workflows/ppm-clarity-slack-commands.json`
- **Commands**: `/ppm-retry`, `/ppm-resolve`, `/ppm-status`
- **Done when**: Commands trigger correct actions and return formatted responses

---

## Phase 5: CI Guardrails

### Task 5.1: Lint Workflow
- **Input**: Spec bundle, migration, Python sources
- **Output**: `.github/workflows/ppm-clarity-lint.yml`
- **Done when**: PR with spec changes triggers validation

### Task 5.2: Integration Test Workflow
- **Input**: Python test suite
- **Output**: `.github/workflows/ppm-clarity-integration-test.yml`
- **Done when**: Tests run on PR and report coverage

### Task 5.3: Write Test Suite
- **Input**: Field ownership contract, sync scenarios
- **Output**: `scripts/ppm/tests/test_*.py` (5 files)
- **Tests**: field_ownership, idempotency, conflicts, integration, slack_notifier
- **Done when**: All tests pass with >95% coverage

---

## Phase 6: Documentation

### Task 6.1: Operational Guide
- **Input**: Architecture, deployment steps, troubleshooting
- **Output**: `docs/ops/PPM_CLARITY_PLANE_ODOO.md`
- **Done when**: Guide covers setup, sync flow, Slack integration, and troubleshooting

### Task 6.2: Update .env.example
- **Input**: All required environment variables
- **Output**: Updated `.env.example` with Plane + Slack vars
- **Done when**: All env vars documented with descriptions

---

## Dependency Matrix

```
Task 1.1 ──────────────────────────────────────── (no deps)
Task 2.1 ← Task 1.1
Task 2.2 ← Task 2.1
Task 2.3 ← Task 2.1
Task 3.1 ← Task 2.1
Task 3.2 ← Task 2.1
Task 3.3 ← Task 3.1 + Task 3.2
Task 3.4 ← (no deps, uses Pulser patterns)
Task 4.1 ← Task 3.3
Task 4.2 ← Task 3.3
Task 4.3 ← Task 3.3 + Task 3.4
Task 4.4 ← Task 3.4
Task 5.1 ← Task 2.1
Task 5.2 ← Task 5.3
Task 5.3 ← Task 3.3 + Task 3.4
Task 6.1 ← All implementation tasks
Task 6.2 ← Task 3.2 + Task 3.4
```

---

## Completion Criteria

All tasks marked complete when:
1. Spec bundle passes `scripts/check-spec-kit.sh`
2. Migration applies cleanly to Supabase
3. All Python tests pass with >95% coverage
4. n8n workflows deploy via `scripts/automations/deploy_n8n_all.py`
5. CI workflows trigger correctly on PR
6. Operational documentation covers all sections
7. No hardcoded secrets in any file
