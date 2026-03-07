# Plane Seed and Roadmap Model

---

## Workspace

| Field | Value |
|-------|-------|
| **Name** | InsightPulseAI |
| **Slug** | insightpulseai |
| **Purpose** | Single company operating surface for all product, platform, and operations work |

---

## Projects

| Project | Scope | Owner Domain |
|---------|-------|-------------|
| **Platform** | Infrastructure, DevOps, CI/CD, self-hosted services (DO, Docker, n8n, Keycloak) | Engineering |
| **Odoo ERP** | Odoo CE 19, OCA modules, ipai_* custom modules, EE parity work | Engineering / Finance |
| **Supabase Control Plane** | Supabase integrations, Edge Functions, schema management, MCP Jobs | Engineering |
| **Web / Marketing** | Public sites, landing pages, Vercel deployments, content | Marketing / Product |
| **Data / AI** | AI agents, Pulser, MCP servers, Superset BI, ML pipelines | Data / AI |
| **Operations / FinOps** | Finance PPM, BIR compliance, month-end close, cost optimization, HR | Finance / Ops |

---

## Standard Work Item Types

| Type | Purpose | Example |
|------|---------|---------|
| **Initiative** | Strategic objective spanning multiple epics | "Achieve 80% EE parity" |
| **Epic** | Large deliverable broken into features | "Bank reconciliation parity" |
| **Feature** | User-facing capability | "Auto-match bank statement lines" |
| **Task** | Discrete implementation unit | "Add matching algorithm to ipai_bank_reconcile" |
| **Bug** | Defect requiring fix | "SSS computation rounding error" |
| **Risk** | Identified risk requiring mitigation | "PostgreSQL 16 upgrade compatibility" |
| **Decision** | Architectural or process decision to record | "Use Keycloak over Supabase Auth for SSO" |
| **Approval** | Gate requiring sign-off before proceeding | "Month-end close sign-off for January" |

### Work Item States

| State | Meaning |
|-------|---------|
| Backlog | Captured but not prioritized |
| Todo | Prioritized for current or next cycle |
| In Progress | Actively being worked on |
| In Review | Awaiting review or approval |
| Done | Completed and verified |
| Cancelled | No longer relevant |

### Priority Levels

| Priority | Label | SLA Guidance |
|----------|-------|-------------|
| Urgent | P0 | Same-day response |
| High | P1 | Within current cycle |
| Medium | P2 | Next cycle |
| Low | P3 | Backlog |
| None | -- | Unprioritized |

---

## Standard Cycles

### Monthly Planning Cycle

| Field | Value |
|-------|-------|
| **Duration** | 1 calendar month |
| **Start** | 1st of each month |
| **Purpose** | Sprint-level execution, monthly close alignment, delivery tracking |
| **Review** | Last business day of the month |

### Quarterly Roadmap Cycle

| Field | Value |
|-------|-------|
| **Duration** | 3 calendar months (Q1: Jan-Mar, Q2: Apr-Jun, Q3: Jul-Sep, Q4: Oct-Dec) |
| **Start** | 1st of quarter |
| **Purpose** | Strategic planning, initiative progress, OKR alignment |
| **Review** | Last week of the quarter |

---

## Standard Views

| View | Audience | Filter / Layout |
|------|----------|-----------------|
| **Executive Roadmap** | Leadership | Initiatives + Epics, grouped by project, timeline layout |
| **Product Roadmap** | Product team | Features + Epics, grouped by cycle, board layout |
| **Engineering Backlog** | Engineering | Tasks + Bugs, grouped by project, list layout |
| **Delivery Board** | All teams | In Progress + In Review work items, board layout |
| **Risks / Blockers** | Leadership + PM | Risk + Bug types with Urgent/High priority, list layout |
| **PPM Approvals** | Finance / Ops | Approval type work items, grouped by state, list layout |
| **FinOps / Production Readiness** | Ops | Tasks filtered by Operations/FinOps project, board layout |

---

## Pages Seed

Each project starts with these Pages. Content is populated during initial setup.

### Workspace-Level Pages (Wiki)

| Page | Content |
|------|---------|
| **Roadmap Overview** | Current quarter initiatives, key milestones, delivery timeline |
| **PPM Operating Model** | How PPM works in Plane: cycles, approvals, reporting cadence |
| **Delivery Governance** | Definition of done, review process, escalation paths |
| **Integration Map** | Slack channels, GitHub repos, Draw.io diagrams linked to projects |
| **Rollout Checklist** | Production readiness gates from PLANE_COMMERCIAL_TARGET_STATE.md |

### Project-Level Pages (per project)

| Page | Content |
|------|---------|
| **Project Charter** | Scope, goals, team, success criteria |
| **Architecture / Design** | Technical diagrams (Draw.io embedded), ADRs |
| **Production Runbook** | Deploy steps, rollback, monitoring, contacts |
| **Email / Auth Setup Notes** | Per-project auth and notification configuration |
| **Decision Log** | Key decisions with date, context, outcome, owner |

---

## Label Taxonomy

| Label Group | Labels |
|------------|--------|
| **Domain** | platform, odoo, supabase, web, data-ai, ops-finops |
| **Priority Override** | blocker, security, compliance |
| **Type Modifier** | tech-debt, documentation, automation |
| **Integration** | slack, github, drawio, n8n, superset |

---

## Seed Loading Sequence

Execute in this order during initial setup:

```
1. Create workspace: InsightPulseAI
2. Create all 6 projects
3. Configure work item types and states
4. Configure priority levels
5. Create label taxonomy
6. Create monthly + quarterly cycles (current + next)
7. Create standard views in each project
8. Create workspace-level wiki pages
9. Create project-level pages in each project
10. Connect Slack integration
11. Connect Draw.io integration
12. Connect GitHub integration
13. Verify all gates per PLANE_COMMERCIAL_TARGET_STATE.md
```
