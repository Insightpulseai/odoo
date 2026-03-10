# PPM Clarity — Product Requirements Document

> Portfolio/Program/Project Management integration between Plane.so (self-hosted)
> and Odoo 19 CE with SSOT governance.

---

## Problem Statement

Planning activities (scope, priorities, sprints) happen in Plane.so while
execution tracking (tasks, timesheets, costs) happens in Odoo. Without a
formal sync contract, teams operate in two disconnected systems, leading to
stale data, duplicated effort, and no unified portfolio view.

---

## User Stories

### US1: Portfolio Manager

> As a portfolio manager, I want Plane projects to automatically create
> corresponding Odoo projects with aligned stages, so I have a single planning
> surface that feeds operational execution.

**Acceptance**: Creating a Plane project from the PPM Clarity template
provisions an Odoo project with matching stage names within 5 minutes.

### US2: Delivery Lead

> As a delivery lead, I want work items committed in Plane (state → In Progress)
> to appear as Odoo tasks, so developers see their assignments in one system.

**Acceptance**: A Plane issue moved to "In Progress" creates an Odoo task with
title, description, and priority within 5 minutes. Re-running the same event
is idempotent.

### US3: Finance Controller

> As a finance controller, I want Odoo task completion (stage → Done) to update
> the Plane issue state, so the planning surface reflects actual delivery status.

**Acceptance**: An Odoo task moved to "Done" updates the corresponding Plane
issue to "Done" within 10 minutes. Timesheets and costs remain in Odoo only.

### US4: Analytics Engineer

> As an analytics engineer, I want an append-only event ledger of all sync
> operations, so I can audit data flow and diagnose failures.

**Acceptance**: Every sync attempt (success or failure) creates a row in
`ops.work_item_events` with event type, source system, payload, and result.

---

## Plane Template Structure

### States (aligned with Odoo stages)

| Plane State | Odoo Stage | Sync Trigger |
|-------------|-----------|--------------|
| Backlog | Backlog | — |
| Triage | Triage | — |
| Planned | Planned | — |
| In Progress | In Progress | Plane → Odoo (commitment) |
| Review | Review | — |
| Done | Done | Odoo → Plane (completion) |
| Cancelled | Cancelled | Bidirectional |

### Labels

| Label | Purpose |
|-------|---------|
| `commit` | Triggers Plane → Odoo sync |
| `blocked` | Triggers Odoo → Plane blocker signal |
| `portfolio` | Portfolio-level work item |
| `program` | Program-level work item |
| `project` | Project-level work item |

### Work Item Types

| Type | Hierarchy |
|------|-----------|
| Epic | Portfolio / Program level |
| Story | Feature / Deliverable |
| Task | Atomic work unit |
| Bug | Defect tracking |

---

## Sync Contract

### Commitment Signal (Plane → Odoo)

**Trigger**: Plane issue state changes to `In Progress` OR label `commit` added.

**Payload** (Plane-owned fields only):
```json
{
  "plane_project_id": "proj-xxx",
  "plane_issue_id": "issue-yyy",
  "title": "Feature X",
  "description": "...",
  "priority": "high",
  "labels": ["commit", "project"],
  "state": "In Progress"
}
```

**Action**: Create or update Odoo `project.task` with mapped fields.

### Completion Signal (Odoo → Plane)

**Trigger**: Odoo task stage changes to `Done`.

**Payload** (execution signals only):
```json
{
  "odoo_task_id": 456,
  "stage": "Done",
  "time_spent_hours": 12.5,
  "completion_date": "2026-03-05"
}
```

**Action**: Update Plane issue state to `Done`. Time/cost data stays in Odoo.

### Nightly Reconciliation

**Schedule**: 2 AM UTC+08:00 daily.

**Process**:
1. Query all `ops.work_item_links` rows
2. Fetch current state from both Plane and Odoo
3. Calculate hashes of owned fields
4. Compare with stored hashes
5. Apply field ownership rules to resolve drift
6. Log reconciliation events
7. Post summary to `#ppm-clarity-logs`

---

## Self-Hosted Deployment

### Plane Self-Hosted

**DNS** (add to `infra/dns/subdomain-registry.yaml`):
```yaml
subdomains:
  - name: plane
    type: A
    target: 178.128.112.214
    purpose: Plane.so frontend (self-hosted)
  - name: plane-api
    type: A
    target: 178.128.112.214
    purpose: Plane.so API (self-hosted)
```

### MCP Server

```bash
# Install
pip install plane-mcp-server
# OR
uvx plane-mcp-server

# Environment
export PLANE_API_KEY=<pat-token>
export PLANE_WORKSPACE_SLUG=insightpulseai
export PLANE_BASE_URL=https://plane-api.insightpulseai.com
```

### Webhooks

Configure in Plane workspace settings:
- **URL**: `https://n8n.insightpulseai.com/webhook/ppm-clarity/plane`
- **Events**: Issue created, Issue updated, Issue deleted
- **Secret**: Store in Supabase Vault as `plane_webhook_secret`

---

## Success Metrics

| Metric | Target |
|--------|--------|
| Sync reliability | >= 99.5% successful syncs |
| Sync latency (commitment) | < 5 minutes |
| Sync latency (completion) | < 10 minutes |
| Conflict rate | < 1% of synced items |
| Event ledger completeness | 100% (every attempt logged) |
| Reconciliation drift | < 0.5% items with hash mismatch |
