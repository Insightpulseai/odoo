# Product & Portfolio Management — Skill Reference

> Knowledge base reference for product/portfolio management agent skills.
> These skills govern the lifecycle of feature specifications and goal hierarchies.

---

## Skill Family Split

The product/portfolio skill family is divided into three bounded roles:

| Skill | Authority | Owns |
|-------|-----------|------|
| `product-manager` | Spec Kit authority | Feature specs, PRDs, acceptance criteria, spec bundle completeness |
| `portfolio-manager` | Azure Boards authority | Goals, OKRs, work item hierarchy, capacity allocation, milestone tracking |
| `product-portfolio-judge` | Alignment authority | Cross-validates product specs against portfolio goals, detects drift and orphans |

### product-manager

Owns the specification lifecycle. Every feature must have a complete spec bundle
(`constitution.md`, `prd.md`, `plan.md`, `tasks.md`) with measurable acceptance
criteria before it enters the build pipeline. The product-manager validates
completeness, cross-references architecture docs, and ensures specs stay within
approved OKR scope.

### portfolio-manager

Owns the goal hierarchy and capacity model. OKRs cascade from enterprise to
platform to team level. Every work item in Azure Boards must link to a goal.
The portfolio-manager validates capacity against timelines, detects orphan work
items, and enforces quarterly review cadence.

### product-portfolio-judge

Validates alignment between the two authorities. Runs at pre-release gates and
quarterly reviews. Detects specs without parent goals, goals without implementing
specs, priority conflicts, and timeline infeasibility. Produces an alignment
report but never auto-closes items — flags only.

---

## Cross-References

| Contract | Purpose |
|----------|---------|
| `docs/contracts/boards-to-spec-contract.md` (C-31) | Defines the linkage between Azure Boards work items and spec bundles |
| `docs/contracts/spec-to-pipeline-contract.md` (C-32) | Defines how validated specs gate CI/CD pipeline execution |
| `docs/contracts/eval-gate-contract.md` | Defines evaluation gate criteria for alignment reviews |

---

## Interaction Model

```
Feature Request
      |
      v
product-manager  ──>  Validated Spec Bundle
      |                       |
      v                       v
portfolio-manager ──>  Goal Hierarchy + Capacity Plan
      |                       |
      v                       v
product-portfolio-judge ──>  Alignment Report
      |
      v
Build Pipeline (gated by spec + goal alignment)
```

---

## Spec Bundle Structure

Each feature spec bundle lives in `spec/<feature-name>/` and must contain:

| File | Purpose | Validated by |
|------|---------|-------------|
| `constitution.md` | Non-negotiable constraints | product-manager |
| `prd.md` | Product requirements | product-manager |
| `plan.md` | Implementation plan | product-manager |
| `tasks.md` | Task breakdown | product-manager + portfolio-manager |

---

## OKR Hierarchy

```
Enterprise OKRs (annual)
  └── Platform OKRs (quarterly)
       └── Team OKRs (quarterly)
            └── Work Items (Azure Boards)
                 └── Spec Bundles (spec/)
```

SSOT files:
- `ssot/governance/enterprise_okrs.yaml`
- `ssot/governance/platform-strategy-2026.yaml`

---

*Last updated: 2026-03-17*
