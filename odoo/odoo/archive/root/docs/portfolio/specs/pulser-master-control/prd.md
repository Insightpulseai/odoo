# Pulser Master Control — Product Requirements Document

> **Version**: 1.0.0
> **Status**: Draft
> **Last Updated**: 2024-12-20

---

## 1. Executive Summary

Pulser Master Control is a **work orchestration system** that unifies business process execution across Odoo CE, GitHub, and integration platforms. It implements SAP-equivalent capabilities using open-source components.

**Key Value Propositions**:
1. Single intake for all work (HR, IT, Finance, Dev)
2. SLA enforcement with automatic escalation
3. Evidence collection for audit/compliance
4. BPMN-driven process automation
5. GitHub PR automation ("All Green" equivalent)

---

## 2. Problem Statement

### Current State
- Siloed systems for HR (Odoo), Dev (GitHub), Finance (Odoo), IT (various)
- No unified SLA tracking across domains
- Manual handoffs between lanes (HR → IT → Finance)
- Poor audit trail for compliance
- CI failures block merges without remediation path

### Desired State
- Unified work intake across all domains
- Automatic SLA timers with escalation
- Evidence-linked audit trail
- Process-driven task generation
- Self-healing CI with Pulser Bot

---

## 3. User Personas

### 3.1 Process Owner
- Defines BPMN processes
- Sets SLA targets
- Reviews compliance dashboards

### 3.2 Lane Worker (HR/IT/Finance)
- Receives assigned work items
- Completes tasks within SLA
- Attaches evidence/artifacts

### 3.3 Developer
- Receives PR-related work items
- Uses Pulser Bot for CI remediation
- Monitors merge readiness

### 3.4 Manager
- Approves tier-validated requests
- Reviews SLA breach reports
- Escalation recipient

---

## 4. Functional Requirements

### 4.1 Work Item Management

| ID | Requirement | Priority |
|----|-------------|----------|
| WI-001 | Create work items from multiple sources (GitHub, Odoo, manual) | P1 |
| WI-002 | Assign work items to lanes (HR/IT/Finance/Dev) | P1 |
| WI-003 | Track work item status (open/running/blocked/done) | P1 |
| WI-004 | Support parent-child work item relationships | P1 |
| WI-005 | Store arbitrary payload as JSONB | P2 |
| WI-006 | Tag work items for filtering | P3 |

### 4.2 SLA Timer Management

| ID | Requirement | Priority |
|----|-------------|----------|
| SLA-001 | Create SLA timer when work item opens | P1 |
| SLA-002 | Track due_at timestamp per work item | P1 |
| SLA-003 | Mark timer as breached when due_at passes | P1 |
| SLA-004 | Trigger escalation on breach | P2 |
| SLA-005 | Support multiple timers per work item (response/resolution) | P2 |
| SLA-006 | Pause timer for blocked items | P3 |

### 4.3 Evidence Collection

| ID | Requirement | Priority |
|----|-------------|----------|
| EV-001 | Attach evidence to work items | P1 |
| EV-002 | Support multiple evidence types (log/patch/doc/screenshot) | P1 |
| EV-003 | Store evidence as URI or inline body | P1 |
| EV-004 | Immutable evidence (no update/delete) | P2 |
| EV-005 | Evidence versioning | P3 |

### 4.4 Process Runtime

| ID | Requirement | Priority |
|----|-------------|----------|
| PR-001 | Parse BPMN process definitions | P2 |
| PR-002 | Generate work items from process nodes | P2 |
| PR-003 | Route work items to lanes based on swimlane | P2 |
| PR-004 | Handle gateways (exclusive/parallel) | P3 |
| PR-005 | Support subprocess expansion | P3 |

### 4.5 GitHub Integration (Pulser Bot)

| ID | Requirement | Priority |
|----|-------------|----------|
| GH-001 | Receive GitHub webhooks (PR, check, review) | P1 |
| GH-002 | Create work items from failing CI checks | P1 |
| GH-003 | Propose patches via agent (Claude/Codex) | P1 |
| GH-004 | Push patch commits to PR branch | P1 |
| GH-005 | Re-run CI after patch | P1 |
| GH-006 | Comment on PR with status | P2 |
| GH-007 | Auto-merge when all green | P3 |

### 4.6 Odoo Integration

| ID | Requirement | Priority |
|----|-------------|----------|
| OD-001 | Create work items from Odoo events (hire/exit) | P1 |
| OD-002 | Sync work item status to Odoo tasks | P2 |
| OD-003 | Trigger Odoo actions on work item resolution | P2 |
| OD-004 | Map Odoo users to work item assignees | P2 |

---

## 5. Non-Functional Requirements

### 5.1 Performance

| ID | Requirement | Target |
|----|-------------|--------|
| PF-001 | Work item creation latency | < 100ms |
| PF-002 | SLA timer check frequency | Every 60s |
| PF-003 | Webhook processing time | < 5s |
| PF-004 | Concurrent work items | > 10,000 |

### 5.2 Reliability

| ID | Requirement | Target |
|----|-------------|--------|
| RL-001 | System availability | 99.9% |
| RL-002 | Data durability | 99.999% |
| RL-003 | Webhook retry on failure | 3 attempts |

### 5.3 Security

| ID | Requirement | Target |
|----|-------------|--------|
| SC-001 | Webhook signature verification | Required |
| SC-002 | API authentication | JWT/API key |
| SC-003 | Lane-based access control | Enforced |
| SC-004 | Audit log retention | 7 years |

---

## 6. Data Model

### 6.1 Core Entities

```
┌─────────────────┐       ┌─────────────────┐
│   work_items    │──────<│   sla_timers    │
├─────────────────┤       ├─────────────────┤
│ id (PK)         │       │ id (PK)         │
│ source          │       │ work_item_id(FK)│
│ source_ref      │       │ timer_type      │
│ title           │       │ due_at          │
│ status          │       │ breached        │
│ lane            │       │ paused_at       │
│ priority        │       └─────────────────┘
│ parent_id (FK)  │
│ assignee_id     │       ┌─────────────────┐
│ payload (JSONB) │──────<│    evidence     │
│ created_at      │       ├─────────────────┤
│ updated_at      │       │ id (PK)         │
│ resolved_at     │       │ work_item_id(FK)│
└─────────────────┘       │ kind            │
                          │ uri             │
                          │ body            │
                          │ created_at      │
                          └─────────────────┘
```

### 6.2 Enumerations

**Status**: `open`, `running`, `blocked`, `done`, `cancelled`

**Lane**: `HR`, `IT`, `FIN`, `DEV`, `MGR`

**Priority**: `1` (critical), `2` (high), `3` (medium), `4` (low)

**Evidence Kind**: `log`, `patch`, `doc`, `screenshot`, `report`, `approval`

**Timer Type**: `response`, `resolution`, `custom`

---

## 7. Integration Contracts

### 7.1 GitHub Webhook → Work Item

```json
{
  "source": "github_pr",
  "source_ref": "https://github.com/org/repo/pull/123",
  "title": "CI Failed: lint/test-unit",
  "lane": "DEV",
  "priority": 2,
  "payload": {
    "pr_number": 123,
    "failing_checks": ["lint", "test-unit"],
    "head_sha": "abc123",
    "base_branch": "main"
  }
}
```

### 7.2 Odoo Event → Work Item

```json
{
  "source": "odoo_event",
  "source_ref": "hr.employee:42:hire",
  "title": "Onboard: John Doe (Engineering)",
  "lane": "HR",
  "priority": 2,
  "payload": {
    "employee_id": 42,
    "employee_name": "John Doe",
    "department": "Engineering",
    "start_date": "2024-01-15",
    "manager_id": 12
  }
}
```

### 7.3 BPMN Process → Work Items

```json
{
  "process_id": "onboarding_v1",
  "instance_id": "uuid-xxx",
  "work_items": [
    {"lane": "HR", "task": "Create employee record", "order": 1},
    {"lane": "IT", "task": "Provision accounts", "order": 2},
    {"lane": "FIN", "task": "Setup payroll", "order": 3},
    {"lane": "MGR", "task": "Welcome meeting", "order": 4}
  ]
}
```

---

## 8. UI/UX Requirements

### 8.1 Mission Control Dashboard (Next.js)

- Kanban view: Inbox → In Progress → Done
- Filter by lane, priority, SLA status
- Real-time updates via WebSocket
- Evidence attachment modal
- SLA countdown timers

### 8.2 Odoo Integration

- Work items visible in Project tasks
- OCA Helpdesk ticket sync (optional)
- Tier validation for approvals

---

## 9. Acceptance Criteria

### 9.1 MVP Acceptance

- [ ] Work items created from GitHub webhooks
- [ ] SLA timers tracked and breach detected
- [ ] Evidence attached to work items
- [ ] Pulser Bot proposes patches for failing CI
- [ ] Work items visible in dashboard

### 9.2 V1.0 Acceptance

- [ ] BPMN process parsing implemented
- [ ] Lane routing working
- [ ] Odoo event integration live
- [ ] Tier validation integrated
- [ ] SLA escalation automated

---

## 10. Dependencies

| Dependency | Purpose | Status |
|------------|---------|--------|
| Supabase | Database + Auth | Available |
| n8n | Workflow automation | Available |
| OCA Tier Validation | Approvals | To install |
| OCA Helpdesk | Ticket UI | Optional |
| Claude API | Agent patches | Available |

---

## 11. Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| GitHub rate limits | Webhook delays | Implement backoff |
| Agent hallucination | Bad patches | Human review gate |
| SLA timer drift | Missed breaches | Use database time |
| Odoo upgrade breaks API | Integration failure | Version pinning |

---

## Appendix: Related Documents

- `constitution.md` — Governing Principles
- `plan.md` — Implementation Roadmap
- `tasks.md` — Actionable Work Items
