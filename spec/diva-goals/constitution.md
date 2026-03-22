# Diva Goals -- Constitution

> Non-negotiable invariants for the Diva Goals product.
> This file is the root governance document. All other spec files inherit from it.

---

## Purpose

**Diva Goals** is the canonical strategy, capability, and execution control plane for InsightPulse AI.

It is not an OKR tracker. It is not a project management tool. It is not a dashboard. It is not an LMS or HRIS.

Diva Goals is the **AI-native orchestration layer** that connects strategic intent (goals, KRs, initiatives) to agentic delivery (specs, work items, agent runs, PRs, pipelines, evals, releases), human and agent capability development (role families, proficiency ladders, skill packs, learning paths), and runtime evidence (metrics, health, drift, readiness). It exists because the agentic DevOps SDLC requires a purpose-built control plane that traditional goal-tracking tools cannot provide, and because capability -- human and agent alike -- is a strategic asset that must be governed alongside execution.

---

## Core Doctrine (10 Invariants)

These invariants are non-negotiable. Every design decision, feature, and integration must satisfy all ten.

### 1. AI-Native by Default

Diva Goals assumes AI agents are first-class participants in the delivery lifecycle. Every entity in the system (goal, KR, initiative, spec, work item, agent run, eval gate, release, capability requirement, learning path, skill pack) must be modelable, queryable, and actionable by both humans and agents. Manual-only workflows are a design defect.

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
- **Capability readiness**: derived from learning evidence, eval scores, and operating outcomes

Self-reported status is permitted only as an **override** with mandatory justification and audit trail.

### 4. Humans Approve, Agents Propose

Agents may propose status changes, create draft reviews, flag drift, and recommend actions. Agents may **never** unilaterally:

- Close a goal or KR
- Mark an initiative as complete
- Override a failing eval gate
- Approve a release
- Modify governance policy
- Upgrade agent autonomy tiers
- Certify human capability readiness

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
| People Capability, L&D | HR/L&D systems, learning records, assessments | Read, evidence for capability readiness |
| Agent Capability | Agent registries, evals, skill packs | Read, evidence for agent readiness |
| Orchestration, Review, Alignment | **Diva Goals** | **Write** -- this is what Diva Goals owns |

Diva Goals never duplicates data that belongs to a source system. It references, indexes, and derives from source systems.

### 6. Goals Must Trace to Execution and Runtime Evidence

Every goal in the system must have a traceable path to execution artifacts and, where applicable, runtime evidence. A goal without downstream traceability is flagged as **orphaned**. A goal with execution artifacts but no runtime evidence is flagged as **unverified**.

The trace chain is:

```
Goal -> KR -> Initiative -> Spec -> Work Items -> Agent Runs/PRs -> Pipelines -> Eval Gates -> Releases -> Runtime Metrics
```

Gaps in this chain are first-class entities in the system (not hidden). They surface as **coverage gaps** in the review engine.

### 7. Humans and Agents Are Both Capability-Bearing Actors

The operating model recognizes two classes of capability-bearing actors: people and agents. Both have roles, skills, proficiency levels, development paths, and readiness states. The capability model must treat them with equal structural rigor, though governance rules differ (agents require eval-based promotion; people require assessment-based certification).

### 8. Capability Is a Strategic Asset, Not a Side Program

Capability gaps -- whether in human skills or agent tools -- are strategic blockers on par with missing infrastructure or budget shortfalls. Every strategic priority may map to required human capabilities and required agent skills. These requirements are not optional metadata; they are load-bearing dependencies in the goal graph.

### 9. Learning Must Be Tied to Operating Outcomes

Learning plans (for people) and skill-pack development (for agents) are not standalone activities. They exist to close capability gaps that block strategic outcomes. A learning intervention without a traced link to an operating outcome is an orphan. A skill pack without a traced link to an agent role requirement is waste.

### 10. Agent Development Must Be Governed Like Workforce Development

Agent capability maturation (new tools, expanded autonomy, new domain knowledge) follows the same governance discipline as human workforce development: define the requirement, assess the current state, plan the development, execute, evaluate, certify. No agent autonomy upgrade without evaluation. No new agent role without a registered skill pack and eval baseline.

---

## Capability Invariants

These extend the core doctrine specifically for the capability axis.

### CI-1: Strategic Priority to Capability Mapping

Every strategic priority (objective, KR, initiative) may declare required human capabilities (role families, proficiency levels) and required agent capabilities (skills, tools, knowledge bases). These declarations are optional per entity but, when present, are load-bearing constraints.

### CI-2: Capability Gaps as Strategic Blockers

When a strategic priority declares a required capability and the current state assessment shows a gap, that gap must surface as a **capability blocker** in the goal graph. Capability blockers appear alongside execution blockers in review ceremonies.

### CI-3: Learning and Skill Plans Linked to Outcomes

Learning plans (human development) and skill-pack plans (agent development) must reference the strategic priority and capability requirement they serve. Plans without outcome linkage are flagged as **unlinked**.

### CI-4: Readiness Requires Evidence

No readiness signal (human certified, agent promoted to higher autonomy) may be asserted without evidence. For humans: assessment scores, project evidence, peer review. For agents: eval scores, test results, supervised-run evidence.

---

## Non-Negotiables

### N1: No Manual-Only Status

Every status field must accept evidence-backed transitions. A status field that can only be set by a human clicking a dropdown is a design defect. Evidence-backed means: the transition is triggered or validated by data from a source system (Azure Boards, GitHub, CI/CD, runtime, L&D system, eval framework).

### N2: No Status Without Evidence Lineage

Every status value must be traceable to the evidence that produced it. "Complete" means: here is the PR, here is the pipeline run, here is the eval score, here is the runtime metric. "Ready" means: here is the assessment, here is the eval pass, here is the supervised-run record. If the evidence chain is broken, the status must be flagged as **unverified**, not silently accepted.

### N3: No Silent Agent Mutation

Agents may propose, draft, and recommend. They may not silently mutate execution status, goal completion, capability readiness, or governance policy. Every agent action must produce an auditable record with: agent identity, action proposed, evidence cited, human approval (if required), timestamp.

### N4: No Duplicated Truth Stores

Diva Goals does not maintain its own copy of work items, PRs, pipeline results, runtime metrics, learning records, or eval scores. It maintains **references** (IDs, URIs, timestamps) and **derived status** (computed from source system data). If a source system is unavailable, Diva Goals reports **stale** status, not cached status presented as current.

### N5: No Readiness Signal Without Evidence

A capability readiness assertion (human or agent) without linked evidence is invalid. The system rejects unlinked readiness claims. Override requires audit-trail justification.

### N6: No Agent Autonomy Upgrade Without Evaluation

An agent's autonomy tier (supervised, semi-autonomous, autonomous) may only increase when the eval framework produces passing scores at the target tier. Manual promotion is blocked by policy gate.

---

## Governance

- This constitution is versioned in `spec/diva-goals/constitution.md`.
- Changes to this file require explicit human approval.
- Agents may propose amendments but may not merge them.
- All other Diva Goals spec files (prd.md, plan.md, tasks.md) must satisfy every invariant and non-negotiable in this document.

---

*Product: Diva Goals*
*Version: 2.0*
*Last updated: 2026-03-23*
