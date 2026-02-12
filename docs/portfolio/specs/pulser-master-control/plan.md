# Pulser Master Control — Implementation Plan

> **Version**: 1.0.0
> **Status**: Active
> **Last Updated**: 2024-12-20

---

## 1. Overview

This plan outlines the phased implementation of Pulser Master Control, progressing from core infrastructure through full process automation.

---

## 2. Implementation Phases

### Phase 1: Foundation (Core Tables + GitHub Bot)

**Objective**: Establish database schema and GitHub PR automation.

**Deliverables**:
1. Supabase migrations for core tables
2. GitHub App registration and webhook handling
3. Pulser Bot MVP (CI failure → patch → re-run)
4. Basic evidence collection

**Key Work**:
- Deploy `work_items`, `sla_timers`, `evidence` tables
- Implement GitHub webhook receiver (FastAPI)
- Build agent loop: read failure → propose fix → apply → verify
- Store patches and CI logs as evidence

**Success Criteria**:
- GitHub webhook creates work items
- Pulser Bot successfully patches 1 failing check
- Evidence stored in database

---

### Phase 2: SLA Enforcement

**Objective**: Implement SLA timers with breach detection and escalation.

**Deliverables**:
1. SLA timer creation on work item open
2. Background job for breach checking
3. Escalation triggers (Slack/email)
4. SLA dashboard widgets

**Key Work**:
- Add SLA timer creation trigger
- Implement 60-second cron for breach check
- Build escalation dispatcher (n8n workflow)
- Add SLA status to work item queries

**Success Criteria**:
- SLA timers created automatically
- Breach detected within 2 minutes of due_at
- Escalation notification sent

---

### Phase 3: Odoo Integration

**Objective**: Connect Odoo events to Master Control work items.

**Deliverables**:
1. Odoo webhook module (emit events)
2. Work item adapter (receive events)
3. Bi-directional status sync
4. User mapping (Odoo → Master Control)

**Key Work**:
- Create `ipai_master_control` Odoo module
- Implement event emitters for HR (hire/exit)
- Build adapter to create work items
- Sync resolution status back to Odoo

**Success Criteria**:
- New hire creates onboarding work item
- Exit request creates offboarding work item
- Status sync works both directions

---

### Phase 4: Process Runtime (BPMN)

**Objective**: Parse BPMN and generate lane-specific work items.

**Deliverables**:
1. BPMN parser (subset: tasks, gateways, swimlanes)
2. Process instantiation API
3. Lane routing engine
4. Process template library

**Key Work**:
- Implement BPMN XML parser (tasks, sequence flows, lanes)
- Build process instance tracker
- Create lane router based on swimlane mapping
- Define onboarding/offboarding process templates

**Success Criteria**:
- BPMN file parsed successfully
- Work items generated per lane
- Correct execution order maintained

---

### Phase 5: Tier Validation & Approvals

**Objective**: Integrate OCA tier validation for approval chains.

**Deliverables**:
1. OCA tier_validation module installed
2. Approval rules for key documents
3. Approval status in work items
4. Approval evidence capture

**Key Work**:
- Install and configure OCA tier_validation
- Define approval tiers for HR/Finance requests
- Link approval status to work item gates
- Capture approval as evidence

**Success Criteria**:
- Expense > $1000 requires manager approval
- Offboarding requires HR + IT sign-off
- Approval captured in evidence

---

### Phase 6: Dashboard & Reporting

**Objective**: Build operational dashboards and compliance reports.

**Deliverables**:
1. Mission Control web UI (Next.js)
2. Superset dashboards
3. SLA compliance reports
4. Audit trail exports

**Key Work**:
- Build Kanban UI for work items
- Create Superset charts for SLA metrics
- Implement report generation (PDF/CSV)
- Add audit trail query API

**Success Criteria**:
- Kanban shows all lanes
- SLA compliance visible in Superset
- Audit export works for date range

---

## 3. Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| Database | Supabase (PostgreSQL) | Core storage, RLS, Auth |
| Backend | FastAPI (Python) | Webhook receiver, APIs |
| Agent | Claude API | Patch generation |
| Workflow | n8n | Integration orchestration |
| Frontend | Next.js | Mission Control UI |
| BI | Superset | Dashboards |
| ERP | Odoo CE 18 | Business operations |

---

## 4. Integration Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         GITHUB                                   │
│  PR Events ─────────────────────────────────────┐               │
│  Check Events ──────────────────────────────────┤               │
└─────────────────────────────────────────────────┼───────────────┘
                                                  │
                                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                     PULSER RUNNER (FastAPI)                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ GitHub Hook  │  │  Odoo Hook   │  │  BPMN Engine │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│         │                │                │                      │
│         └────────────────┼────────────────┘                      │
│                          ▼                                       │
│                 ┌──────────────────┐                            │
│                 │   Work Item Svc  │                            │
│                 └──────────────────┘                            │
│                          │                                       │
└──────────────────────────┼───────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                      SUPABASE                                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ work_items   │  │ sla_timers   │  │  evidence    │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
                           │
         ┌─────────────────┼─────────────────┐
         ▼                 ▼                 ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   Odoo CE    │  │     n8n      │  │   Superset   │
│   (Tasks)    │  │ (Workflows)  │  │ (Dashboards) │
└──────────────┘  └──────────────┘  └──────────────┘
```

---

## 5. Milestone Summary

| Phase | Milestone | Key Outcome |
|-------|-----------|-------------|
| 1 | GitHub Bot MVP | PR failures → auto-patch |
| 2 | SLA Live | Breach detection + escalation |
| 3 | Odoo Connected | HR events → work items |
| 4 | BPMN Running | Process → lane tasks |
| 5 | Approvals Live | Tier validation integrated |
| 6 | Dashboard Live | Operational visibility |

---

## 6. Resource Requirements

### Infrastructure
- Supabase project (existing: `spdtwktxdalcfigzeqrz`)
- GitHub App (to register)
- n8n instance (existing)
- Superset instance (existing)

### Development
- Backend: FastAPI + PostgreSQL
- Frontend: Next.js + TailwindCSS
- Odoo: Module development

---

## 7. Risk Register

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| GitHub API changes | Low | High | Pin webhook version |
| Agent generates bad patches | Medium | Medium | Human review gate |
| SLA timer accuracy | Low | High | Use DB timestamp |
| Odoo module conflicts | Medium | Medium | Isolated namespace |

---

## 8. Dependencies Map

```
Phase 1 ──► Phase 2 ──► Phase 6
    │           │
    │           └──► Phase 5
    │
    └──► Phase 3 ──► Phase 4 ──► Phase 5
```

---

## Appendix: Related Documents

- `constitution.md` — Governing Principles
- `prd.md` — Product Requirements
- `tasks.md` — Actionable Work Items
