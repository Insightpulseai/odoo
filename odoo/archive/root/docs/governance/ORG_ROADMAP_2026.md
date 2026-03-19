# Insightpulseai Org Roadmap — 2026

## Purpose

This roadmap defines the sequence for evolving the Insightpulseai GitHub organization into a governed enterprise operating surface.

The roadmap uses:
- Figma / FigJam for roadmap design and review
- GitHub Projects for active execution
- repository and release governance as delivery evidence

---

## Q1 2026 — Foundation and classification

### Goal
Create the baseline inventory and governance model.

### Deliverables
- complete org profile metadata
- classify all repositories by type and lifecycle
- create `REPO_INVENTORY.md`
- document archive rationale for all archived repos
- define the 3 standard GitHub Projects
- define shared project field schema
- identify canonical active repository set
- add or update README for active repos lacking purpose clarity

### Success measures
- 100% repo classification complete
- 100% active repos have owner and purpose
- 100% archived repos have archive reason
- Portfolio / Roadmap, Execution Board, and Ops / Release Readiness projects exist

### Risks
- archived repos may still contain canonical logic
- duplicate ownership and overlapping repo purpose may block classification

---

## Q2 2026 — Governance hardening

### Goal
Standardize org governance across all active repos.

### Deliverables
- CODEOWNERS for active repos
- branch protection baseline
- standard release policy
- standard environment policy
- package/artifact policy
- standard labels and issue/PR templates in `.github`
- project templates aligned to initiative/epic/feature/task/bug/risk flows

### Success measures
- 100% active repos have CODEOWNERS
- 100% active repos have branch protection policy
- 100% deployable repos have release/environment policy
- 90% of active work is captured inside standard GitHub Projects

### Risks
- legacy workflows may not align with environment/release policy
- archived repos may still be referenced by active automation

---

## Q3 2026 — Planning and execution consolidation

### Goal
Unify roadmap planning and delivery execution.

### Deliverables
- adopt one Figma/FigJam roadmap template set
- run quarterly planning using Figma roadmap artifacts
- sync approved roadmap items into GitHub Projects
- normalize initiative/epic/feature hierarchy
- create role-based views in GitHub Projects
- make execution board the default cross-repo work surface

### Success measures
- 80% of roadmap items traceable from Figma plan to GitHub Project item
- 80% of execution items linked to repo/PR activity
- one quarterly roadmap review cadence established

### Risks
- stakeholders may continue to keep roadmap items in disconnected docs
- GitHub Projects field design may need iteration before adoption stabilizes

---

## Q4 2026 — Release, package, and artifact maturity

### Goal
Make deployments and releases auditable across the org.

### Deliverables
- formal package strategy for reusable deliverables
- linked artifacts enabled for deployable surfaces where supported
- release audit process documented
- production deployment evidence standardized
- repository-to-environment mapping completed
- release-to-artifact-to-environment linkage documented

### Success measures
- 100% of production deployments traceable to repo + SHA + release + environment + evidence
- no deployable repo without documented release policy
- no production release without evidence trail

### Risks
- some deploy workflows may bypass GitHub-native deployment/artifact patterns
- existing releases may need retrospective audit documentation

---

## Q1 2027 — Optimization and portfolio reporting

### Goal
Operate the org as a measurable enterprise engineering portfolio.

### Deliverables
- dependency map across canonical active repos
- architecture review cadence
- quarterly portfolio scorecard
- delivery metrics dashboard
- archive consolidation complete
- active repo set finalized and enforced

### Success measures
- no orphan active repos
- 95% roadmap traceability
- stable quarterly portfolio review cadence
- active repo set remains within intended canonical boundary

---

## Milestone summary

| Quarter | Milestone | Primary outcome |
|---|---|---|
| Q1 2026 | Foundation | Repo inventory and org taxonomy complete |
| Q2 2026 | Governance | Branch/release/environment policy standardized |
| Q3 2026 | Planning consolidation | Figma roadmap + GitHub execution model operational |
| Q4 2026 | Release maturity | Artifact/release/deployment traceability operational |
| Q1 2027 | Enterprise optimization | Portfolio reporting and steady-state governance |

---

## KPI timeline

### By end of Q1 2026
- repo classification = 100%
- active repos with owner + purpose = 100%

### By end of Q2 2026
- active repos with CODEOWNERS + protection = 100%
- deployable repos with release/environment policy = 100%

### By end of Q3 2026
- roadmap-to-execution traceability = 80%
- active delivery running through standard GitHub Projects = 90%

### By end of Q4 2026
- release/deployment traceability = 100%
- production deployments with evidence trail = 100%

### By end of Q1 2027
- roadmap traceability = 95%
- orphan active repos = 0
- archived repos with rationale = 100%

---

## Consolidation note

This roadmap supersedes the following prior roadmap documents:

| Prior document | Status | Notes |
|---|---|---|
| `agents/PRIORITIZED_ROADMAP.md` | Partially complete | Agent framework phases 0-7; tactical, not org-level |
| `docs/integration/INSIGHTPULSE_ROADMAP.md` | Stale | Finance SSC roadmap (Jan 2026); references deprecated Mattermost |
| `spec/company-roadmap/prd.md` | Active | AI Marketing Canvas; product roadmap, not org governance |
| `infra/superset/PRESET_PARITY_ROADMAP.md` | Active | Superset parity; domain-specific |
| `docs/plane/PLANE_SEED_AND_ROADMAP_MODEL.md` | Active | Plane PM integration model |

Domain-specific roadmaps (finance, agents, superset) remain valid within their scope. This document governs the **organizational operating model** — repo taxonomy, project structure, governance, and release traceability.
