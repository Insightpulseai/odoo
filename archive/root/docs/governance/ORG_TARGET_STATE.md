# Insightpulseai GitHub Org — Target State

## Purpose

This document defines the desired end state for the Insightpulseai GitHub organization as an enterprise engineering control plane.

The objective is to move from a collection of repositories into a governed portfolio with:

- clear repo taxonomy
- standardized planning and execution surfaces
- auditable releases and deployments
- package/artifact traceability
- a roadmap workflow that separates planning from execution

GitHub Projects provides the execution substrate with project tables, custom fields, filters, saved views, and planning support. Azure Boards is the benchmark reference for backlog, sprint, and portfolio-style work management. Figma/FigJam provides the visual planning layer through official roadmap, strategic planning, and quarterly planning templates.

---

## Current observed baseline

The organization currently shows:

- 22 repositories
- 3 organization-level GitHub Projects
- 1 GitHub Package
- 1 Team
- no populated linked artifacts view in org Packages
- sparse organization profile metadata relative to the desired enterprise posture

This is enough to establish a strong base, but not yet enough to function as a mature enterprise portfolio control plane.

---

## Target operating model

### 1. Organizational layers

The GitHub org should be operated in five layers:

#### A. Control plane
Canonical governance and operational policy:

- `.github`
- `ops-platform`
- `infra`

#### B. Core runtime and product systems
Primary delivery surfaces:

- `odoo`
- `web`
- `lakehouse`

#### C. Shared systems
Reusable internal platform assets:

- `design-system`
- `templates`
- `agents`

#### D. Planning and governance surfaces
Cross-repo coordination and portfolio management:

- GitHub Projects
- release policy
- environment policy
- architecture decision records
- package/artifact policy

#### E. Archived / deprecated estate
Historical repositories retained for audit/reference:

- archived repos remain visible but must be explicitly classified and documented

---

## Canonical repository taxonomy

Every repository must have both a **type** and a **lifecycle state**.

### Repository type
Allowed values:

- `control-plane`
- `runtime`
- `shared-library`
- `template`
- `archive`

### Lifecycle state
Allowed values:

- `active`
- `incubating`
- `maintenance`
- `archived`

### Required metadata for every active repo

Each active repository must have:

- business/technical owner
- one-sentence purpose
- repo type
- lifecycle state
- source-of-truth designation
- linked project(s)
- release/deployability classification
- environment classification if deployable

---

## Canonical active repository set

The desired long-term active set is:

- `.github`
- `odoo`
- `web`
- `infra`
- `ops-platform`
- `lakehouse`
- `design-system`
- `templates`
- `agents`

Any currently archived repository that still contains canonical logic must be migrated into one of the active repos or formally documented before remaining archived.

---

## GitHub Projects operating model

GitHub Projects should become the operational work system. GitHub Projects supports table-based planning, filters, saved views, custom fields, and issue/PR tracking across repositories. Azure Boards remains the benchmark reference for backlog, portfolio, sprint, and board semantics.

### Standard organization projects

The desired steady-state set is exactly three organization-level projects:

1. **InsightPulseAI Portfolio / Roadmap**
2. **Execution Board**
3. **Ops / Release Readiness**

### Project roles

#### 1. InsightPulseAI Portfolio / Roadmap
Purpose:
- initiatives
- quarterly roadmap
- strategic sequencing
- executive portfolio visibility

#### 2. Execution Board
Purpose:
- active implementation
- sprint/cycle work
- bugs/tasks/features
- repo-linked execution

#### 3. Ops / Release Readiness
Purpose:
- release gating
- production readiness
- migration/rollback readiness
- environment checks
- deployment evidence

### Standard project fields

All organization projects should converge on a shared field vocabulary:

- `Domain`
- `Type`
- `Priority`
- `Target Quarter`
- `Sprint/Cycle`
- `Environment`
- `Release`
- `Owner`
- `Status`
- `Blocked`
- `Repo`

---

## Roadmap and planning model

### Planning canvas
Use Figma / FigJam for visual planning and stakeholder alignment. Figma officially provides roadmap-related templates including product development roadmap, strategic planning, quarterly planning, and related planning surfaces.

### Execution system
Use GitHub Projects for operational execution once roadmap items are approved.

### Rule
The planning stack should be:

- **Figma / FigJam** = roadmap design, sequencing, and stakeholder communication
- **GitHub Projects** = approved execution system
- **GitHub repos / PRs / releases** = implementation and delivery evidence

---

## Packages and linked artifacts

GitHub Packages and linked artifacts should be used to provide build-to-deployment traceability.

### Target state
For deployable repos:

- packages are used where reusable artifacts exist
- linked artifacts connect build outputs to deployment environments
- releases can be mapped to artifacts and deployment evidence

### Rule
No production deployment should be considered fully auditable unless it can be traced to:

- repository
- commit SHA
- release tag
- environment
- artifact/deploy evidence

---

## Governance baseline

All active repos should converge on:

- `README`
- `CODEOWNERS`
- branch protection
- issue/PR templates where appropriate
- release policy
- environment policy if deployable
- archive rationale if deprecated later

---

## Desired measurable outcomes

### 30-day outcomes
- 100% of repos classified by type and lifecycle
- 100% of active repos have owner and README
- 100% of archived repos have archive rationale
- organization profile completed
- 3 standard org-level Projects in place

### 60-day outcomes
- 90% of active repos mapped to a GitHub Project
- 100% of deployable repos mapped to environments/releases
- 100% of active repos have CODEOWNERS and branch protection
- 80% of roadmap items traceable from planning to execution

### 90-day outcomes
- 100% of production deployments traceable to release + environment + artifact/evidence
- 0 orphan active repos with no owner or purpose
- 1 standard quarterly roadmap process across the org
- 1 standard release-readiness process across deployable repos

---

## Success metrics

### Repo hygiene
- active repos with owner + README + taxonomy = **100%**

### Project hygiene
- work items with owner + status + quarter = **95%+**

### Roadmap traceability
- roadmap items linked to execution and PRs = **80% in first quarter**, **95% by second quarter**

### Release traceability
- production releases linked to environments and evidence = **100%**

### Archive hygiene
- archived repos with documented rationale = **100%**

---

## Final desired end state

The GitHub organization should function as:

- a portfolio control plane
- an execution system
- a release governance surface
- a traceable deployment/evidence system

not just as a list of repositories.

The end state is:

- 8–10 canonical active repositories
- 3 standard org-level GitHub Projects
- standardized taxonomy and governance
- auditable releases and artifacts
- Figma for roadmap design
- GitHub Projects for delivery execution
