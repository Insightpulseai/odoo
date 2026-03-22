# Diva Goals -- Product Requirements Document

> AI-native goals, execution, and review system for the agentic DevOps SDLC.

---

## Product Identity

| Field | Value |
|-------|-------|
| **Product Name** | Diva Goals |
| **Slug** | `diva-goals` |
| **One-liner** | AI-native goals, execution, and review system for the agentic DevOps SDLC |
| **Category** | Strategy-to-execution control plane |
| **Owner** | InsightPulse AI Platform Team |
| **Constitution** | `spec/diva-goals/constitution.md` |

---

## Problem Statement

Traditional OKR and goal-tracking tools (Lattice, Betterworks, Ally.io, Viva Goals, even Azure Boards alone) were designed for human-only organizations where:

- Humans set goals
- Humans do the work
- Humans report status
- Humans review progress
- Dashboards show what humans typed into fields

This model breaks in an **AI-first, agent-augmented organization** because:

1. **Maker agents** produce code, specs, and artifacts -- but traditional tools cannot model agent participation as a delivery entity.
2. **Judge agents** evaluate quality, run benchmarks, and score outputs -- but traditional tools have no concept of eval gates in the goal chain.
3. **Spec-driven delivery** means work is defined by spec bundles (`constitution.md`, `prd.md`, `plan.md`, `tasks.md`) -- but traditional tools model work as flat task lists.
4. **Eval-gated releases** mean delivery completion depends on automated evaluation passing thresholds -- but traditional tools only model binary done/not-done.
5. **Runtime evidence** (metrics, health checks, observability) should close the loop on whether a goal was actually achieved -- but traditional tools stop at "task marked complete."
6. **Agent runs** are first-class delivery events (a Claude Code session, a Foundry agent invocation, a CI pipeline) -- but traditional tools have no entity for them.
7. **Confidence scoring** for agent outputs requires a different status model than binary pass/fail -- but traditional tools offer only checkbox completion.

Diva Goals exists to solve this. It is the **control plane** that sits above Azure Boards, GitHub, CI/CD, eval frameworks, and runtime observability to provide a unified strategy-to-execution-to-evidence view that is native to the agentic SDLC.

---

## Goals

### G1: Unified Strategy-to-Execution Graph

Provide a single graph that connects strategic objectives to KRs, initiatives, specs, work items, agent runs, PRs, pipelines, eval gates, releases, and runtime metrics. No gaps, no manual stitching.

### G2: Agentic SDLC as Core Model

Model the full agentic delivery lifecycle as a first-class entity chain, not an afterthought bolted onto a human-only workflow.

### G3: Evidence-Backed Status

Eliminate self-reported status. Every status transition must be backed by evidence from a source system, with full lineage.

### G4: AI-Native Review Engine

Provide structured review ceremonies (execution review, portfolio review, exception review) that surface evidence, flag drift, detect orphans, and recommend actions -- with agent assistance.

### G5: Human-in-the-Loop Governance

Ensure humans retain approval authority over all material status transitions while agents handle proposal, analysis, and evidence gathering.

### G6: Zero Duplication

Never duplicate data that belongs to a source system. Reference, index, derive -- but never copy-and-own.

---

## Users

### Human Users

| User | Description | Primary Jobs |
|------|-------------|-------------|
| **Platform Lead** | Sets strategic objectives, reviews portfolio | Define goals, review execution, approve releases |
| **Engineering Lead** | Owns initiatives and delivery | Track spec completion, review agent output, approve PRs |
| **Finance/Ops Lead** | Owns operational KRs (close cycle, compliance) | Monitor operational metrics, review compliance evidence |
| **Individual Contributor** | Executes work items, reviews agent proposals | Complete tasks, review agent PRs, provide context |

### Agent Users

| Agent | Description | Primary Jobs |
|-------|-------------|-------------|
| **Maker Agent** | Produces code, specs, configs (Claude Code, Foundry, Copilot) | Execute spec tasks, create PRs, produce artifacts |
| **Judge Agent** | Evaluates output quality (eval framework, benchmark runners) | Score agent output, gate releases, flag regressions |
| **Ops Agent** | Monitors runtime, reports metrics (observability agents) | Report runtime evidence, flag health issues, update KR metrics |

---

## Jobs to Be Done

### J1: Platform Lead -- "Show me if we're on track"

> I need to see, in one view, whether our strategic objectives are progressing. Not based on what people typed into status fields, but based on actual delivery evidence: specs completed, code merged, pipelines green, evals passing, metrics moving. If something is off track, I need to know why and what the evidence says.

### J2: Engineering Lead -- "Show me the delivery chain"

> For any initiative, I need to trace from the goal down to the spec, the work items, the agent runs, the PRs, the pipeline results, and the eval scores. If an agent produced a PR, I need to see its confidence score, the eval gate result, and whether a human approved it. If a spec is incomplete, I need to see which tasks are blocked and why.

### J3: Finance/Ops Lead -- "Show me compliance evidence"

> For regulatory and operational KRs (BIR filing, month-end close, expense policy), I need evidence that the process ran, the checks passed, and the artifacts exist. Not a checkbox someone clicked -- actual pipeline logs, filing confirmations, reconciliation reports.

### J4: Maker Agent -- "What should I work on next?"

> Given the current goal graph, spec backlog, and priority signals, which spec task should I pick up? What is the context I need? What are the acceptance criteria? When I'm done, where do I submit my output for review?

### J5: Judge Agent -- "What needs evaluation?"

> Which agent outputs are pending evaluation? What are the eval criteria for each? What thresholds must be met for the release gate to pass? If an output fails, what feedback should I provide to the maker agent?

---

## Product Principles

### P1: Graph, Not List

Goals, KRs, initiatives, specs, work items, agent runs, and evidence form a **directed acyclic graph**, not a flat list. The graph is the product.

### P2: Derived Status is Default

Status is computed from source system evidence by default. Manual status is an override, not the norm.

### P3: Evidence is Addressable

Every piece of evidence (a PR, a pipeline run, an eval score, a runtime metric) has a stable URI and can be referenced from any entity in the graph.

### P4: Agents are Participants, Not Tools

Agents appear in the graph as participants with identity, capability declarations, confidence scores, and audit trails. They are not invisible background processes.

### P5: Staleness is Visible

If evidence is older than its freshness policy (e.g., runtime metric older than 24h), the system flags it as stale. Stale evidence degrades derived status to **unverified**.

### P6: Reviews are Structured

Review ceremonies have defined inputs (evidence, drift flags, orphan reports), defined outputs (decisions, action items, approvals), and defined cadence. They are not ad-hoc meetings.

### P7: Layered Authority

The system respects a layered authority model: source systems are authoritative for their domain, Diva Goals is authoritative for orchestration and review, humans are authoritative for approval.

---

## Solution Architecture (5 Layers)

### Layer 1: Strategic Model

The top of the graph. Objectives, Key Results, and Initiatives as defined in Azure Boards (Epics, Features, User Stories) but enriched with:

- KR measurement definitions (metric source, target, threshold)
- Initiative-to-spec linkage
- Portfolio groupings and priority signals

### Layer 2: Execution Graph

The middle of the graph. Maps the agentic SDLC chain:

```
Spec Bundle -> Work Items -> Agent Runs -> PRs -> Pipelines -> Eval Gates -> Releases
```

Each entity is a node with:
- Source system reference (Azure Boards ID, GitHub PR URL, pipeline run ID)
- Status (derived from source system)
- Evidence links (URIs to artifacts, logs, scores)
- Participant links (which agent or human produced/reviewed this)

### Layer 3: Evidence Engine

The connective tissue. Responsible for:

- Ingesting evidence from source systems (Azure Boards API, GitHub API, Azure DevOps API, Application Insights, Databricks)
- Computing derived status from evidence
- Detecting staleness (evidence older than freshness policy)
- Detecting drift (status inconsistent with evidence)
- Detecting orphans (goals without execution, execution without goals)

### Layer 4: Review Engine

The human-facing decision layer. Provides:

- **Execution Review**: Weekly. Surfaces initiative progress, blocked items, agent output pending review, drift flags.
- **Portfolio Review**: Monthly. Surfaces goal/KR progress, coverage gaps, resource allocation, strategic alignment.
- **Exception Review**: On-demand. Triggered by drift detection, eval gate failure, stale evidence, or manual escalation.

Each review produces structured output: decisions made, action items created, approvals granted, exceptions documented.

### Layer 5: Agent Layer

The agent-facing interface. Provides:

- **Task Queue**: Prioritized list of spec tasks available for agent pickup, with context and acceptance criteria.
- **Submission Endpoint**: Where agents submit completed work for review and eval.
- **Confidence Model**: Agents declare confidence in their output; low-confidence items are routed for human review.
- **Audit Trail**: Every agent action is logged with identity, action, evidence, and outcome.

---

## Functional Requirements

### FR1: Agentic SDLC Entity Model

The system must model the complete agentic SDLC chain as first-class entities:

| Entity | Source System | Diva Goals Role |
|--------|--------------|-----------------|
| Objective | Azure Boards (Epic) | Read, align, review |
| Key Result | Azure Boards (Feature) | Read, measure, derive status |
| Initiative | Azure Boards (User Story) | Read, trace to specs |
| Spec Bundle | Spec Kit (`spec/`) | Read, validate completeness |
| Work Item | Azure Boards (Task) | Read, trace to agent runs/PRs |
| Agent Run | CI/CD logs, Foundry logs | Read, evidence for delivery |
| Pull Request | GitHub | Read, evidence for code delivery |
| Pipeline Run | Azure DevOps, GitHub Actions | Read, evidence for build/test |
| Eval Gate | Eval framework | Read, gate release decisions |
| Release | GitHub Release, ACA deployment | Read, evidence for deployment |
| Runtime Metric | App Insights, Databricks, Power BI | Read, evidence for KR outcomes |

### FR2: Agent Participation Model

The system must model agent participation with:

- **Agent Identity**: Name, type (maker/judge/ops), capability declaration
- **Agent Runs**: Timestamped records of agent invocations with input context, output artifacts, confidence score
- **Maker Role**: Agent produces artifacts (code, specs, configs) linked to work items
- **Judge Role**: Agent evaluates artifacts against criteria, produces scores, gates releases
- **Confidence Scoring**: Agents declare confidence (0.0-1.0) in their output; thresholds determine routing (auto-approve, human-review, reject)
- **Approval Workflow**: Human approval required for agent outputs above work-item level

### FR3: Evidence-Backed Status Transitions

Every status transition must:

1. Reference the source system event that triggered it (PR merged, pipeline passed, eval score above threshold)
2. Include a timestamp and evidence URI
3. Be auditable (who/what changed the status, when, based on what evidence)
4. Support override with mandatory justification

### FR4: Drift and Orphan Detection

The system must continuously detect:

- **Drift**: Status inconsistent with evidence (e.g., initiative marked "complete" but linked spec has failing eval gates)
- **Orphans**: Goals without downstream execution, execution without upstream goals
- **Staleness**: Evidence older than its freshness policy

Detections surface as flags in the review engine, not silent background states.

### FR5: Review Engine

The system must provide structured review ceremonies:

- **Execution Review** (weekly): Initiative progress, blocked items, agent output pending review, drift flags, action items from last review
- **Portfolio Review** (monthly): Goal/KR progress, coverage gaps, strategic alignment, resource allocation, exception log
- **Exception Review** (on-demand): Triggered by drift, eval failure, stale evidence, or escalation

Each review produces: decisions, action items, approvals, exceptions -- all persisted and traceable.

### FR6: DevOps Evidence Drill-Through

From any goal or KR, a user must be able to drill through the full evidence chain:

```
Goal -> KR -> Initiative -> Spec -> Work Items -> Agent Runs -> PRs -> Pipelines -> Eval Scores -> Releases -> Runtime Metrics
```

Each level shows: entity identity, source system link, current status, evidence summary, participants.

---

## Non-Goals

Diva Goals is explicitly **not**:

- **A replacement for Azure Boards**: Azure Boards remains the source of truth for work items, epics, features, and backlog management. Diva Goals reads from Boards, it does not replace it.
- **A replacement for GitHub**: GitHub remains the source of truth for code, PRs, and repositories. Diva Goals reads PR status and evidence, it does not manage code.
- **A replacement for observability tools**: Application Insights, Databricks, and Power BI remain the source of truth for runtime metrics and health. Diva Goals reads metrics as evidence, it does not collect telemetry.
- **A general-purpose project management tool**: Diva Goals does not manage sprints, kanban boards, or task assignment. It manages the strategy-to-execution-to-evidence graph.
- **A standalone product**: Diva Goals is a control plane that requires Azure Boards, GitHub, CI/CD, and observability as foundational systems. It has no value without them.

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Goal-to-execution traceability | 100% of active goals have downstream execution links | Graph coverage query |
| Evidence-backed status | >= 90% of status transitions backed by source system evidence | Audit log analysis |
| Drift detection latency | < 1 hour from source system event to drift flag | Event processing lag |
| Orphan detection coverage | 100% of entities checked weekly | Review engine output |
| Review ceremony completion | 100% of scheduled reviews produce structured output | Review log |
| Agent participation visibility | 100% of agent runs linked to work items and specs | Graph coverage query |
| Stale evidence flagging | 100% of evidence past freshness policy flagged within 1h | Evidence engine metrics |

---

## Rollout Phases

### Phase 1: Core Strategy Graph (Weeks 1-3)

- Import objectives and KRs from Azure Boards
- Define KR measurement sources
- Establish initiative-to-spec linkage
- Build basic graph visualization

### Phase 2: SDLC Evidence Chain (Weeks 4-6)

- Ingest work items, PRs, pipeline runs from Azure Boards and GitHub
- Compute derived status from evidence
- Build drill-through from goal to pipeline
- Implement staleness detection

### Phase 3: Agent Participation (Weeks 7-9)

- Model agent identity and capability
- Ingest agent run records from CI/CD and Foundry logs
- Implement confidence scoring and routing
- Build maker/judge participation views
- Implement approval workflow for agent outputs

### Phase 4: Review Engine (Weeks 10-12)

- Build execution review ceremony (weekly)
- Build portfolio review ceremony (monthly)
- Build exception review (on-demand triggers)
- Implement drift and orphan detection
- Generate structured review output

### Phase 5: Governance Automation (Weeks 13-16)

- Policy gates (stale evidence auto-flags, override audit requirements)
- Export/snapshot for compliance
- Agent-assisted review preparation (pre-populate evidence, flag anomalies)
- Integration with Azure DevOps Boards backlog prioritization

---

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Source system API rate limits | Medium | High | Batch ingestion, caching, webhook-first where available |
| Evidence freshness lag | Medium | Medium | Event-driven ingestion, explicit staleness flags |
| Agent confidence calibration | High | Medium | Start conservative (low threshold = human review), tune over time |
| Scope creep into project management | High | High | Constitution non-goals, regular scope reviews |
| Adoption resistance (manual status habit) | Medium | Medium | Default to derived status, make override friction visible |

---

## Open Questions

1. **Storage**: Should the Diva Goals graph live in Databricks (Delta tables) or a dedicated graph store? Current lean: Databricks for durability and query, with materialized views for the graph.
2. **Real-time vs. batch**: Should evidence ingestion be real-time (webhook/event-driven) or batch (scheduled)? Current lean: event-driven for CI/CD, batch for runtime metrics.
3. **UI surface**: Should the primary UI be Power BI dashboards, a custom web app, or both? Current lean: Power BI for read-only views, custom app for review ceremonies.
4. **Agent task assignment**: Should Diva Goals actively assign tasks to agents, or should agents pull from a queue? Current lean: pull model with priority signals.
5. **Multi-org**: Is Diva Goals single-tenant (InsightPulse AI only) or designed for multi-tenant from the start? Current lean: single-tenant first, multi-tenant later.

---

*Product: Diva Goals*
*Version: 1.0*
*Last updated: 2026-03-23*
