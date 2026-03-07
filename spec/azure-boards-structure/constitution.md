# Azure Boards Structure — Constitution

> Non-negotiable rules governing Azure Boards usage within InsightPulse AI.
> This document is the governance layer. All configuration must conform to these rules.

---

## 1. Organization

Azure DevOps Organization: **`insightpulseai`**

## 2. Project Boundary

Exactly **3 projects** exist:

| Project | Scope |
|---------|-------|
| `erp-saas` | Odoo ERP SaaS runtime, modules, integrations, release engineering |
| `lakehouse` | Databricks lakehouse, data pipelines, customer 360, marketing intelligence, ML/AI |
| `platform` | Control plane, Azure runtime, boards automation, agents, shared services |

No additional projects may be created without explicit governance approval from the Product Owner and Engineering Manager.

## 3. Boards-Only Rule

Azure DevOps is used for **Boards ONLY**. The following Azure DevOps services are **PROHIBITED**:

- **Repos** — All code lives in GitHub
- **Pipelines** — All CI/CD runs in GitHub Actions
- **Artifacts** — All packages managed via GitHub Packages / npm / PyPI
- **Test Plans** — All test execution managed in GitHub Actions or local tooling
- **Wiki** — All documentation lives in repo `docs/` directories or GitHub wikis

Violation of this rule requires immediate remediation and incident review.

## 4. GitHub as Sole CI/CD and Code Platform

GitHub is the single source of truth for:
- Source code repositories
- Pull requests and code review
- CI/CD pipelines (GitHub Actions)
- Package distribution
- Release management

No code or pipeline configuration may exist in Azure DevOps.

## 5. Work Item Hierarchy

The work item hierarchy is fixed:

```
Epic → Feature → User Story → Task
```

- **No custom work item types** are permitted
- **No additional hierarchy levels** (e.g., Initiative) without governance approval
- All four levels must be used consistently across all three projects

## 6. Area Paths Model Ownership

Area paths represent **team ownership domains**, not environments or deployment targets.

- Area paths are defined per-project (see PRD for specifics)
- Environment information is captured via the `Deployment Surface` custom field
- Never create area paths named after environments (e.g., `dev`, `staging`, `prod`)

## 7. Iteration Paths Use Consistent Cadence

All three projects follow the same sprint cadence:

- **2-week sprints**
- Structure: `2026 → Q1-Q4 → Sprint 01+`
- Sprint start/end dates are synchronized across projects
- Epics scope to quarter/half-year level
- Features scope to 1-3 sprints
- Stories complete within a single sprint
- Tasks complete in 1-3 days

## 8. Board Columns — No Status Explosion

Board columns are kept simple and consistent:

- **Story board**: New, Ready, In Progress, Blocked, In Review, Done
- **Task board**: To Do, Doing, Review, Done

No additional columns may be added without governance approval. Column names must match exactly across all projects.

## 9. Tags for Reporting Only

Tags are used **exclusively for cross-cutting reporting and filtering**. They are not a substitute for area paths or custom fields.

- Maximum **15 tags** across the organization
- Canonical tags: `odoo`, `oca`, `ipai`, `azure`, `databricks`, `supabase`, `agent`, `security`, `finops`, `marketing`, `customer360`, `runtime`, `deploy`, `observability`
- New tags require governance approval
- Tags must not duplicate information already captured by area paths, iteration paths, or custom fields

## 10. Naming Conventions Are Deterministic

| Work Item Type | Format |
|----------------|--------|
| Epic | `[DOMAIN] <Outcome>` |
| Feature | `[DOMAIN] <Capability>` |
| User Story | `As a <role>, I need <capability>, so that <outcome>` |
| Task | `<Verb> <specific deliverable>` |

Domain tags must match the area path hierarchy. These conventions are enforced — non-conforming work items must be corrected during backlog refinement.

## 11. GitHub Linking Required for Code-Triggering Work Items

Every work item that triggers code changes **must** link to a GitHub repository via the `Primary Repo` custom field. Work items without this link cannot move to `In Progress`.

Linked repositories per project:

| Project | Repositories |
|---------|-------------|
| `erp-saas` | `odoo`, `odoo-modules` |
| `lakehouse` | `lakehouse` |
| `platform` | `platform`, `boards-automation`, `agents`, `infra`, `web` |

## 12. PR/Agent Workflow

The canonical workflow for code-triggering work items:

```
Story/Task → Linked repo → Agent picks up → Branch created → PR opened → CI/CD runs → Code review → Merge → Work item auto-updated to Done
```

- Branch naming: `<type>/<work-item-id>-<short-description>`
- PR title must reference the Azure Boards work item ID
- Merging a PR auto-transitions the linked work item to `Done` (via Azure Boards + GitHub integration)
- Agent-assisted PR creation is supported for configured repos

---

## Source-of-Truth Boundaries

| System | Owns | Does NOT Own |
|--------|------|-------------|
| **Azure Boards** | Work items, backlogs, sprints, delivery plans, agent triggers | Code, CI/CD, deployments, artifacts |
| **GitHub** | Repos, PRs, Actions, packages, releases, code review | Planning, roadmap, portfolio management |
| **Odoo** | ERP records, finance, CRM, HR, approvals | Code, planning, infrastructure |
| **Databricks** | Data pipelines, ML, analytics, lakehouse | Code delivery, planning |

No system may encroach on another system's ownership domain. Cross-system references are established via linking (e.g., work item → PR, Odoo record → work item) but never by duplicating data.

---

## Enforcement

- Constitution violations are flagged during sprint retrospectives
- Automated compliance checks run weekly via boards-automation scripts
- Non-conforming work items are quarantined until corrected
- Governance review required for any exception to these rules

---

*Governed by: `ssot/azure/boards-structure.yaml`*
*Last updated: 2026-03-07*
