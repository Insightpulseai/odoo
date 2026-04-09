# PRD — Unified Finance System

> Product requirements for the coordinated BIR tax compliance,
> month-end close, and finance PPM system.

---

## 1. Problem Statement

TBWA\SMP Finance SSC operates a monthly cycle that spans:

- Philippine BIR tax filing (36 eBIRForms, monthly/quarterly/annual cadences)
- Month-end close (5 phases, 39 tasks, cross-functional handoffs)
- Project portfolio management (Clarity PPM-style planning, OKR tracking, analytic controls)

These are currently implemented as 5 independent Odoo modules with no
unified process model, no shared test coverage, and seed data split across
3 formats. The result is fragmented visibility — no single surface shows
the full finance operations picture.

## 2. End Users

| Role | Code | Responsibilities |
|------|------|------------------|
| Finance Director | CKVC | Approval authority, compliance sign-off, portfolio oversight |
| Senior Finance Manager | RIM | Close orchestration, BIR filing review, PPM planning |
| Finance Supervisor | BOM | Task assignment, deadline tracking, team coordination |
| Accountants (7) | JPAL, LAS, RMQB, JPL, JI, JO, JM | Task execution: journal entries, reconciliation, BIR prep, filing |

## 3. Scope

### 3.1 BIR Tax Compliance

| Outcome | Measure |
|---------|---------|
| All 36 eBIRForms tracked with filing deadlines | 100% form coverage in seed data |
| Monthly filing cycle automated (1601-C, 0619-E, SSS, PhilHealth, Pag-IBIG) | 12 monthly cycles seeded per year |
| Quarterly filings tracked (2550Q, 1601-EQ) | 4 quarterly cycles seeded |
| Annual filings tracked (1604-CF, 2316, Alphalist) | Annual tasks present |
| Deadline alerts sent before due dates | Notifications module active with cron |
| BIR tasks synced to Plane for OKR tracking | Plane sync module operational |

### 3.2 Month-End Close

| Outcome | Measure |
|---------|---------|
| 5-phase close process with 39 tasks | All tasks seeded with phase/milestone assignment |
| Kanban workflow (To Do → In Prep → Review → Approval → Done) | 6 stages defined |
| Team assignments with workload visibility | 9 team members mapped to tasks |
| Milestone tracking per phase | 5 close milestones + 2 output milestones |
| Repeatable monthly cycle | Tasks can be duplicated per period |

### 3.3 Finance PPM / Clarity Parity

| Outcome | Measure |
|---------|---------|
| Project portfolio with analytic controls | `ipai_finance_ppm` extends `project.project` and `account.analytic.account` |
| OKR dashboard | JavaScript dashboard action deployed |
| PPM import wizard for bulk data loading | Wizard functional |
| Clarity-style WBS hierarchy | 5 levels: goal → outcome → objective → workstream → task |
| Budget vs. actual variance analysis | Analytic account extensions with forecast fields |

### 3.4 Gap Evaluation Rule

A capability is classified as **Gap = unresolved** only after a
**cross-repo CE/OCA 18 scan** across:

- project / project-reporting / project-agile
- timesheet
- helpdesk
- knowledge / document approval
- spreadsheet / dashboard
- MIS Builder / financial reporting
- analytic / accounting-adjacent modules
- other adjacent CE/OCA 18 repos materially relevant to PPM

A capability absent from `OCA/project` alone is **not** evidence of a gap.

## Capability Sourcing Doctrine

A capability must be classified in this order:

1. **CE-native** — covered by Odoo 18 CE core
2. **OCA-native (project/timesheet)** — covered by OCA project or timesheet repos
3. **OCA-native (adjacent)** — covered by non-project OCA repos (helpdesk, knowledge, MIS, etc.)
4. **Composite CE+OCA** — composable from multiple modules, no custom model yet
5. **Thin custom delta** — `ipai_*` module required for genuinely unresolved capability
6. **External analytics / planning assist** — Power BI, Databricks, or external tool

A capability may only be labeled "custom delta required" after steps 1–4 fail.

## Capability Coverage Classification

| Classification | Meaning |
|---|---|
| **Covered directly** | CE or OCA module provides the capability as-is |
| **Covered compositionally** | Capability achievable by composing adjacent CE/OCA 18 modules |
| **Unresolved after cross-repo scan** | No proven CE/OCA 18 pattern exists; custom delta or external assist required |

## Revised Sourcing Matrix

| Capability family | Likely source lane | Current status |
|---|---|---|
| Project execution / WBS / milestones | CE Project + OCA/project | Strong |
| Timesheet governance / approvals | OCA/timesheet | Strong |
| Portfolio structure / grouping | OCA/project | Strong / partial by design |
| Issue register | Candidate: OCA/helpdesk linked to project | Likely composable |
| Risk register | Candidate: helpdesk/customized ticketing or governance records | Unresolved, but not yet proven custom-only |
| Governance approvals / decision records | OCA/knowledge document approval + project-linked docs | Likely composable |
| KPI rollups / dashboards | MIS Builder + spreadsheet/dashboard layer | Likely composable |
| Demand / backlog / intake | Candidate: project-agile + helpdesk/form intake + project templates | Partial / unresolved |
| Capacity planning / optimization | No strong proof of mature OCA parity yet | Likely real gap |
| Prioritization / scoring / scenario analysis | No proven CE/OCA 18 pattern yet | Likely real gap |

## 4. Non-Goals

- Rebuilding existing modules from scratch
- Creating a new umbrella module that wraps the five active modules
- Replacing Odoo's native `account` or `project` modules
- Building a custom BIR eFiling integration (electronic submission to BIR systems)
- Implementing payroll computation (owned by `ipai_hr_payroll_ph`)

## 5. Process Model

```
                    Monthly Cycle
                         |
         +---------------+---------------+
         |                               |
    Month-End Close                BIR Tax Filing
    (39 tasks, 5 phases)          (50 tasks, 9 forms)
         |                               |
   Phase I: Pre-Close              Monthly Forms
   Phase II: Transaction Close     (1601-C, 0619-E, SSS,
   Phase III: Reconciliation        PhilHealth, Pag-IBIG)
   Phase IV: Reporting                   |
   Phase V: Post-Close             Quarterly Forms
         |                         (2550Q, 1601-EQ)
         |                               |
         +---------------+---------------+
                         |
                   Finance PPM
              (Portfolio oversight,
               OKR tracking,
               analytic controls)
```

## 6. Reporting and Accountability

- **Kanban board**: Real-time task status per team member
- **Calendar view**: BIR filing deadlines overlaid with close milestones
- **OKR dashboard**: Portfolio-level health metrics
- **Compliance dashboard**: BIR form completion rates, overdue filings
- **Superset views**: 11 SQL views for BI layer (defined in technical guide)

## 7. Seed Data Ownership

| Artifact | Format | Authority | Location |
|----------|--------|-----------|----------|
| Stages, tags, team, projects, milestones, tasks | XML/CSV | **Canonical** | `ipai_finance_close_seed/data/` |
| BIR form schedules | JSON | Derived/reference | `ipai_finance_closing_seed.json` (repo root) |
| Finance expense categories | SQL | Deprecated | `supabase/seeds/002_finance_seed.sql` |

## 8. Success Criteria

1. One spec bundle (`spec/finance-unified/`) governs all finance modules
2. One canonical doc (`docs/modules/FINANCE_UNIFIED_SYSTEM.md`) describes the full system
3. Active vs. deprecated modules are explicitly classified and enforced
4. Seed data has at least one validation test per domain (BIR schedules, close tasks, PPM objects)
5. All active modules target Odoo 18.0 (`ipai_bir_tax_compliance` version aligned to 18.0)
6. No duplicate SSOT surfaces remain unresolved
