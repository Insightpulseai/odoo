# Diva Goals -- Constitution

> Non-negotiable invariants for the Diva Goals product.
> This file is the root governance document. All other spec files inherit from it.

---

## Purpose

**Diva Goals** is the canonical strategy-to-execution control plane for InsightPulse AI.

It is not an OKR tracker. It is not a project management tool. It is not a dashboard.

Diva Goals is the **AI-native orchestration layer** that connects strategic intent (goals, KRs, initiatives) to agentic delivery (specs, work items, agent runs, PRs, pipelines, evals, releases) and runtime evidence (metrics, health, drift). It exists because the agentic DevOps SDLC requires a purpose-built control plane that traditional goal-tracking tools cannot provide.

---

## Core Doctrine (6 Invariants)

These invariants are non-negotiable. Every design decision, feature, and integration must satisfy all six.

### 1. AI-Native by Default

Diva Goals assumes AI agents are first-class participants in the delivery lifecycle. Every entity in the system (goal, KR, initiative, spec, work item, agent run, eval gate, release) must be modelable, queryable, and actionable by both humans and agents. Manual-only workflows are a design defect.

### 2. Agentic SDLC is First-Class

The product models the full agentic software delivery lifecycle:

```
Objective -> KR -> Initiative -> Spec -> Work Item -> Agent Run -> PR -> Pipeline -> Eval Gate -> Release -> Runtime Metric
```

This is not a future aspiration. It is the core graph. Every feature must trace to this chain.

### 3. Evidence Over Self-Report

No status field in Diva Goals may be set by manual assertion alone. Every status transition must be backed by evidence from a source system:

- **Goal progress**: derived from KR completion, not self-reported percentage
- **KR completion**: derived from initiative outcomes and runtime metrics
- **Initiative status**: derived from spec completion, work item closure, pipeline results
- **Work item status**: derived from PR merge, CI/CD pass, eval gate pass
- **Agent run status**: derived from pipeline logs, eval scores, approval records

Self-reported status is permitted only as an **override** with mandatory justification and audit trail.

### 4. Humans Approve, Agents Propose

Agents may propose status changes, create draft reviews, flag drift, and recommend actions. Agents may **never** unilaterally:

- Close a goal or KR
- Mark an initiative as complete
- Override a failing eval gate
- Approve a release
- Modify governance policy

Human approval is the terminal authority for all execution-status transitions above the work-item level.

### 5. Source Systems Remain Authoritative

Diva Goals is an **orchestration and review layer**, not a replacement for authoritative source systems. The source-of-truth boundaries are:

| Domain | Source of Truth | Diva Goals Role |
|--------|----------------|-----------------|
| Goals, Portfolio, OKRs | Azure Boards (Epics, Features) | Read, align, review, flag drift |
| Specs | Spec Kit (`spec/` directory) | Read, trace to goals, validate completeness |
| Code, PRs | GitHub | Read, trace to specs/work items, evidence |
| CI/CD, Pipelines | Azure DevOps Pipelines, GitHub Actions | Read, evidence for delivery status |
| Eval Gates | Eval framework (evals/) | Read, gate release decisions |
| Runtime, Observability | Application Insights, Databricks, Power BI | Read, evidence for KR/metric outcomes |
| Orchestration, Review, Alignment | **Diva Goals** | **Write** -- this is what Diva Goals owns |

Diva Goals never duplicates data that belongs to a source system. It references, indexes, and derives from source systems.

### 6. Goals Must Trace to Execution and Runtime Evidence

Every goal in the system must have a traceable path to execution artifacts and, where applicable, runtime evidence. A goal without downstream traceability is flagged as **orphaned**. A goal with execution artifacts but no runtime evidence is flagged as **unverified**.

The trace chain is:

```
Goal -> KR -> Initiative -> Spec -> Work Items -> Agent Runs/PRs -> Pipelines -> Eval Gates -> Releases -> Runtime Metrics
```

Gaps in this chain are first-class entities in the system (not hidden). They surface as **coverage gaps** in the review engine.

---

## Non-Negotiables

### N1: No Manual-Only Status

Every status field must accept evidence-backed transitions. A status field that can only be set by a human clicking a dropdown is a design defect. Evidence-backed means: the transition is triggered or validated by data from a source system (Azure Boards, GitHub, CI/CD, runtime).

### N2: No Status Without Evidence Lineage

Every status value must be traceable to the evidence that produced it. "Complete" means: here is the PR, here is the pipeline run, here is the eval score, here is the runtime metric. If the evidence chain is broken, the status must be flagged as **unverified**, not silently accepted.

### N3: No Silent Agent Mutation

Agents may propose, draft, and recommend. They may not silently mutate execution status, goal completion, or governance policy. Every agent action must produce an auditable record with: agent identity, action proposed, evidence cited, human approval (if required), timestamp.

### N4: No Duplicated Truth Stores

Diva Goals does not maintain its own copy of work items, PRs, pipeline results, or runtime metrics. It maintains **references** (IDs, URIs, timestamps) and **derived status** (computed from source system data). If a source system is unavailable, Diva Goals reports **stale** status, not cached status presented as current.

---

## Governance

- This constitution is versioned in `spec/diva-goals/constitution.md`.
- Changes to this file require explicit human approval.
- Agents may propose amendments but may not merge them.
- All other Diva Goals spec files (prd.md, plan.md, tasks.md) must satisfy every invariant and non-negotiable in this document.

---

*Product: Diva Goals*
*Version: 1.0*
*Last updated: 2026-03-23*
