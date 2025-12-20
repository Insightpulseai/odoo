# Pulser Master Control — Task Breakdown

> **Version**: 1.0.0
> **Status**: Active
> **Last Updated**: 2024-12-20

---

## Phase 1: Foundation

### 1.1 Database Setup

- [ ] **TASK-001**: Create Supabase migration for `work_items` table
  - Lane: DEV
  - Priority: P1
  - Acceptance: Table exists with all columns, RLS enabled

- [ ] **TASK-002**: Create Supabase migration for `sla_timers` table
  - Lane: DEV
  - Priority: P1
  - Acceptance: FK to work_items, indexes on due_at

- [ ] **TASK-003**: Create Supabase migration for `evidence` table
  - Lane: DEV
  - Priority: P1
  - Acceptance: FK to work_items, kind enum validated

- [ ] **TASK-004**: Create trigger for `updated_at` auto-update
  - Lane: DEV
  - Priority: P2
  - Acceptance: Timestamp updates on any row modification

- [ ] **TASK-005**: Create RLS policies for lane-based access
  - Lane: DEV
  - Priority: P2
  - Acceptance: Users see only their lane's work items

### 1.2 GitHub App Setup

- [ ] **TASK-006**: Register GitHub App in org settings
  - Lane: DEV
  - Priority: P1
  - Acceptance: App ID and private key obtained

- [ ] **TASK-007**: Configure webhook events (PR, check_suite, workflow_run)
  - Lane: DEV
  - Priority: P1
  - Acceptance: Webhooks pointing to runner URL

- [ ] **TASK-008**: Implement webhook signature verification
  - Lane: DEV
  - Priority: P1
  - Acceptance: Invalid signatures rejected

- [ ] **TASK-009**: Implement GitHub API client with app auth
  - Lane: DEV
  - Priority: P1
  - Acceptance: Can read PR, post comments, push commits

### 1.3 Pulser Runner (FastAPI)

- [ ] **TASK-010**: Create FastAPI project skeleton
  - Lane: DEV
  - Priority: P1
  - Acceptance: Health endpoint returns 200

- [ ] **TASK-011**: Implement GitHub webhook endpoint
  - Lane: DEV
  - Priority: P1
  - Acceptance: Webhook received, logged, ACK returned

- [ ] **TASK-012**: Implement work item creation from webhook
  - Lane: DEV
  - Priority: P1
  - Acceptance: Failing check creates work item in DB

- [ ] **TASK-013**: Implement agent core (planner → apply → verify)
  - Lane: DEV
  - Priority: P1
  - Acceptance: Agent proposes patch for lint failure

- [ ] **TASK-014**: Implement patch application (git commit + push)
  - Lane: DEV
  - Priority: P1
  - Acceptance: Patch appears on PR branch

- [ ] **TASK-015**: Implement CI re-run trigger
  - Lane: DEV
  - Priority: P1
  - Acceptance: Check re-runs after patch push

- [ ] **TASK-016**: Implement evidence storage (logs, patches)
  - Lane: DEV
  - Priority: P1
  - Acceptance: Evidence rows created with URI/body

---

## Phase 2: SLA Enforcement

### 2.1 Timer Management

- [ ] **TASK-017**: Create SLA timer on work item creation
  - Lane: DEV
  - Priority: P1
  - Acceptance: Timer created with correct due_at

- [ ] **TASK-018**: Implement SLA policy configuration
  - Lane: DEV
  - Priority: P2
  - Acceptance: Priority → SLA duration mapping works

- [ ] **TASK-019**: Create breach detection cron job
  - Lane: DEV
  - Priority: P1
  - Acceptance: Breached timers marked within 2 minutes

- [ ] **TASK-020**: Implement timer pause/resume for blocked items
  - Lane: DEV
  - Priority: P3
  - Acceptance: Paused timers don't breach

### 2.2 Escalation

- [ ] **TASK-021**: Design escalation workflow in n8n
  - Lane: DEV
  - Priority: P2
  - Acceptance: Workflow triggers on breach webhook

- [ ] **TASK-022**: Implement Slack notification for breach
  - Lane: DEV
  - Priority: P2
  - Acceptance: Slack message sent with work item link

- [ ] **TASK-023**: Implement email escalation fallback
  - Lane: DEV
  - Priority: P3
  - Acceptance: Email sent if Slack fails

---

## Phase 3: Odoo Integration

### 3.1 Odoo Event Emitter Module

- [ ] **TASK-024**: Create `ipai_master_control` module skeleton
  - Lane: DEV
  - Priority: P1
  - Acceptance: Module installs without errors

- [ ] **TASK-025**: Implement HR hire event emitter
  - Lane: DEV
  - Priority: P1
  - Acceptance: Webhook sent on employee create

- [ ] **TASK-026**: Implement HR exit event emitter
  - Lane: DEV
  - Priority: P1
  - Acceptance: Webhook sent on departure_date set

- [ ] **TASK-027**: Implement expense approval event emitter
  - Lane: DEV
  - Priority: P2
  - Acceptance: Webhook sent on expense submit

### 3.2 Work Item Adapter

- [ ] **TASK-028**: Create Odoo webhook endpoint in runner
  - Lane: DEV
  - Priority: P1
  - Acceptance: Endpoint receives Odoo events

- [ ] **TASK-029**: Implement work item creation from Odoo event
  - Lane: DEV
  - Priority: P1
  - Acceptance: HR event creates work item

- [ ] **TASK-030**: Implement user mapping (Odoo → Master Control)
  - Lane: DEV
  - Priority: P2
  - Acceptance: Odoo user ID maps to assignee

- [ ] **TASK-031**: Implement bi-directional status sync
  - Lane: DEV
  - Priority: P2
  - Acceptance: Work item done → Odoo task done

---

## Phase 4: Process Runtime (BPMN)

### 4.1 BPMN Parser

- [ ] **TASK-032**: Implement BPMN XML parser (task elements)
  - Lane: DEV
  - Priority: P2
  - Acceptance: Tasks extracted from BPMN

- [ ] **TASK-033**: Implement lane/swimlane extraction
  - Lane: DEV
  - Priority: P2
  - Acceptance: Tasks mapped to lanes

- [ ] **TASK-034**: Implement sequence flow parsing
  - Lane: DEV
  - Priority: P2
  - Acceptance: Task order determined

- [ ] **TASK-035**: Implement exclusive gateway handling
  - Lane: DEV
  - Priority: P3
  - Acceptance: Conditional branching works

### 4.2 Process Engine

- [ ] **TASK-036**: Create process_instances table
  - Lane: DEV
  - Priority: P2
  - Acceptance: Table tracks running processes

- [ ] **TASK-037**: Implement process instantiation API
  - Lane: DEV
  - Priority: P2
  - Acceptance: POST /process/start creates instance

- [ ] **TASK-038**: Implement work item generation from process
  - Lane: DEV
  - Priority: P2
  - Acceptance: Tasks → work items with parent

- [ ] **TASK-039**: Implement process completion detection
  - Lane: DEV
  - Priority: P2
  - Acceptance: All children done → parent done

### 4.3 Process Templates

- [ ] **TASK-040**: Create onboarding BPMN template
  - Lane: DEV
  - Priority: P2
  - Acceptance: HR → IT → Finance → Manager flow

- [ ] **TASK-041**: Create offboarding BPMN template
  - Lane: DEV
  - Priority: P2
  - Acceptance: Manager → IT → HR → Finance flow

- [ ] **TASK-042**: Create expense approval BPMN template
  - Lane: DEV
  - Priority: P3
  - Acceptance: Submit → Manager → Finance flow

---

## Phase 5: Tier Validation & Approvals

### 5.1 OCA Integration

- [ ] **TASK-043**: Install OCA tier_validation module
  - Lane: DEV
  - Priority: P2
  - Acceptance: Module in addons, installed

- [ ] **TASK-044**: Configure approval tiers for expenses
  - Lane: DEV
  - Priority: P2
  - Acceptance: >$1000 requires manager

- [ ] **TASK-045**: Configure approval tiers for offboarding
  - Lane: DEV
  - Priority: P2
  - Acceptance: HR + IT sign-off required

### 5.2 Approval Evidence

- [ ] **TASK-046**: Capture approval as evidence
  - Lane: DEV
  - Priority: P2
  - Acceptance: Approval event → evidence row

- [ ] **TASK-047**: Block work item until approval
  - Lane: DEV
  - Priority: P2
  - Acceptance: Status = blocked until approved

---

## Phase 6: Dashboard & Reporting

### 6.1 Mission Control UI

- [ ] **TASK-048**: Create Next.js project skeleton
  - Lane: DEV
  - Priority: P2
  - Acceptance: App builds and runs

- [ ] **TASK-049**: Implement Kanban board component
  - Lane: DEV
  - Priority: P2
  - Acceptance: Drag/drop works

- [ ] **TASK-050**: Implement lane filter
  - Lane: DEV
  - Priority: P2
  - Acceptance: Can filter by HR/IT/FIN/DEV

- [ ] **TASK-051**: Implement SLA countdown display
  - Lane: DEV
  - Priority: P2
  - Acceptance: Timer shows remaining time

- [ ] **TASK-052**: Implement real-time updates (WebSocket)
  - Lane: DEV
  - Priority: P3
  - Acceptance: New items appear without refresh

### 6.2 Superset Dashboards

- [ ] **TASK-053**: Create SLA compliance chart
  - Lane: DEV
  - Priority: P2
  - Acceptance: % within SLA visible

- [ ] **TASK-054**: Create work item volume chart
  - Lane: DEV
  - Priority: P2
  - Acceptance: Daily/weekly trends visible

- [ ] **TASK-055**: Create lane workload chart
  - Lane: DEV
  - Priority: P3
  - Acceptance: Work per lane visible

### 6.3 Reporting

- [ ] **TASK-056**: Implement audit trail export API
  - Lane: DEV
  - Priority: P2
  - Acceptance: GET /audit?from=X&to=Y returns CSV

- [ ] **TASK-057**: Implement compliance report generation
  - Lane: DEV
  - Priority: P3
  - Acceptance: PDF report with SLA stats

---

## Summary

| Phase | Tasks | P1 | P2 | P3 |
|-------|-------|----|----|-----|
| 1 Foundation | 16 | 13 | 3 | 0 |
| 2 SLA | 7 | 2 | 3 | 2 |
| 3 Odoo | 8 | 4 | 4 | 0 |
| 4 BPMN | 11 | 0 | 9 | 2 |
| 5 Approvals | 5 | 0 | 5 | 0 |
| 6 Dashboard | 10 | 0 | 7 | 3 |
| **Total** | **57** | **19** | **31** | **7** |

---

## Appendix: Related Documents

- `constitution.md` — Governing Principles
- `prd.md` — Product Requirements
- `plan.md` — Implementation Roadmap
