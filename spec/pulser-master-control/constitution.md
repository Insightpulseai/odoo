# Pulser Master Control — Constitution

> **Version**: 1.0.0
> **Status**: Active
> **Last Updated**: 2024-12-20

---

## 1. Purpose

Pulser Master Control is the **unified work orchestration layer** that bridges:
- **SAP enterprise patterns** (SuccessFactors, Concur, Signavio, BTP)
- **Odoo CE/OCA 18** (community-first ERP)
- **GitHub/DevOps tooling** (CI/CD, PR automation)

It treats **ticketing as the execution surface** — every business process (onboarding, offboarding, procurement, expense approval) starts as a work item that fans out into lane-specific subtasks with SLA timers and evidence collection.

---

## 2. Governing Principles

### 2.1 Ticket-First Execution

Every process instance starts as a **work_item** (ticket). Child tasks are generated per lane (HR/IT/Finance/Manager). This provides:
- Single intake point
- Clear audit trail
- SLA enforcement
- Evidence collection

### 2.2 SAP-Parity, CE-Native

We map SAP capabilities to Odoo CE equivalents:

| SAP Capability | Odoo CE Equivalent |
|----------------|-------------------|
| SuccessFactors (HR) | Employees + OCA HR suite |
| Concur (Expense) | Expenses + Tier Validation |
| Ariba/SRM (Procurement) | Purchase + Tier Validation |
| Signavio (BPMN) | Process Runtime (custom) |
| BTP Integration Suite | n8n + webhooks |
| SAC/Datasphere | Superset |

### 2.3 Idempotent & Auditable

All operations must be:
- **Idempotent**: Re-running the same input produces the same output
- **Auditable**: Every state change is logged with actor, timestamp, evidence

### 2.4 Open Source First

- Prefer OCA modules over custom development
- Prefer self-hosted over SaaS where practical
- Maintain CE compatibility (no Enterprise-only dependencies)

---

## 3. Architecture Boundaries

### 3.1 Master Control Core (This System)

- Work item intake (tickets)
- SLA timer management
- Evidence/artifact storage
- Process runtime (BPMN → work items)
- Lane routing (HR/IT/Finance/Dev)

### 3.2 Execution Surfaces (External)

- **Odoo CE**: HR, Finance, Procurement operations
- **GitHub**: PR/CI automation (Pulser Bot)
- **n8n**: Integration workflows
- **Superset**: Analytics/dashboards

### 3.3 Integration Patterns

```
┌─────────────────────────────────────────────────────────────┐
│                    MASTER CONTROL CORE                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │ Work Items  │  │ SLA Timers  │  │  Evidence   │          │
│  └─────────────┘  └─────────────┘  └─────────────┘          │
│         │               │               │                    │
│  ┌─────────────────────────────────────────────────┐        │
│  │              PROCESS RUNTIME                     │        │
│  │         (BPMN → Lanes → Tasks)                  │        │
│  └─────────────────────────────────────────────────┘        │
└─────────────────────────────────────────────────────────────┘
         │                    │                    │
         ▼                    ▼                    ▼
   ┌──────────┐        ┌──────────┐        ┌──────────┐
   │ Odoo CE  │        │  GitHub  │        │   n8n    │
   │   Lane   │        │   Lane   │        │   Lane   │
   └──────────┘        └──────────┘        └──────────┘
```

---

## 4. Governance

### 4.1 Change Control

- All schema changes require migration scripts
- Breaking changes require RFC + approval
- Deprecations have 2-release sunset period

### 4.2 SLA Definitions

| Priority | Response | Resolution | Escalation |
|----------|----------|------------|------------|
| P1 (Critical) | 15 min | 4 hours | Auto at breach |
| P2 (High) | 1 hour | 8 hours | Auto at 75% |
| P3 (Medium) | 4 hours | 24 hours | Manual |
| P4 (Low) | 24 hours | 72 hours | None |

### 4.3 Evidence Requirements

All work items must collect:
- **Creation evidence**: Source, actor, initial payload
- **State change evidence**: Actor, timestamp, reason
- **Resolution evidence**: Outcome, artifacts, approvals

---

## 5. Security & Compliance

### 5.1 Data Classification

- **Public**: Process definitions, SOP templates
- **Internal**: Work item metadata, SLA status
- **Confidential**: Employee data, financial data
- **Restricted**: Credentials, secrets (never in DB)

### 5.2 Access Control

- Lane-based RBAC (HR lane = HR role)
- Tier validation for sensitive operations
- Audit log immutability

### 5.3 Retention

- Work items: 7 years (regulatory)
- Evidence: 7 years (regulatory)
- SLA timers: 1 year (operational)

---

## 6. Non-Goals

This system does NOT:
- Replace Odoo's native workflow engine
- Implement full BPMN 2.0 execution
- Provide end-user ticketing UI (use OCA Helpdesk)
- Store secrets or credentials

---

## 7. Success Metrics

| Metric | Target |
|--------|--------|
| Work item resolution rate | > 95% within SLA |
| Process automation coverage | > 80% of defined lanes |
| Evidence capture rate | 100% for P1/P2 |
| Mean time to onboard (employee) | < 48 hours |
| Mean time to offboard (employee) | < 24 hours |

---

## Appendix A: Capability Registry (SAP → Odoo CE)

See `capability-registry.yaml` for the machine-readable mapping.

## Appendix B: Related Documents

- `prd.md` — Product Requirements
- `plan.md` — Implementation Roadmap
- `tasks.md` — Actionable Work Items
