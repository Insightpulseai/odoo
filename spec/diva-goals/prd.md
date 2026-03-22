# Diva Goals -- Product Requirements Document

> AI-native strategy, capability, and execution control plane.

---

## Product Identity

| Field | Value |
|-------|-------|
| **Product Name** | Diva Goals |
| **Slug** | `diva-goals` |
| **One-liner** | AI-native strategy, capability, and execution control plane |
| **Category** | Strategy-to-execution-to-readiness control plane |
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
8. **Capability gaps** -- both human skills and agent tools/knowledge -- block strategic outcomes. Traditional tools treat L&D as a separate silo and have no concept of agent skill development.
9. **Agent workforce governance** -- autonomy tiers, eval-gated promotion, degradation rules -- has no home in traditional tools.

Diva Goals exists to solve this. It is the **control plane** that sits above Azure Boards, GitHub, CI/CD, eval frameworks, runtime observability, L&D systems, and agent registries to provide a unified strategy-to-execution-to-capability-to-evidence view that is native to the agentic SDLC.

---

## Goals

### G1: Unified Strategy-to-Execution Graph

Provide a single graph that connects strategic objectives to KRs, initiatives, specs, work items, agent runs, PRs, pipelines, eval gates, releases, and runtime metrics. No gaps, no manual stitching.

### G2: Agentic SDLC as Core Model

Model the full agentic delivery lifecycle as a first-class entity chain, not an afterthought bolted onto a human-only workflow.

### G3: Evidence-Backed Status

Eliminate self-reported status. Every status transition must be backed by evidence from a source system, with full lineage.

### G4: AI-Native Review Engine

Provide structured review ceremonies (execution review, portfolio review, capability review, agent readiness review, exception review) that surface evidence, flag drift, detect orphans, and recommend actions -- with agent assistance.

### G5: Human-in-the-Loop Governance

Ensure humans retain approval authority over all material status transitions while agents handle proposal, analysis, and evidence gathering.

### G6: Zero Duplication

Never duplicate data that belongs to a source system. Reference, index, derive -- but never copy-and-own.

### G7: Capability Intelligence

Surface human and agent capability gaps as strategic blockers. Connect learning plans and skill-pack development to operating outcomes. Make readiness visible.

### G8: Agent Development Intelligence

Govern agent lifecycle (registration, evaluation, promotion, degradation) with the same structural rigor as human workforce development.

---

## Users

### Human Users

| User | Description | Primary Jobs |
|------|-------------|-------------|
| **Platform Lead** | Sets strategic objectives, reviews portfolio | Define goals, review execution, approve releases |
| **Engineering Lead** | Owns initiatives and delivery | Track spec completion, review agent output, approve PRs |
| **Finance/Ops Lead** | Owns operational KRs (close cycle, compliance) | Monitor operational metrics, review compliance evidence |
| **Individual Contributor** | Executes work items, reviews agent proposals | Complete tasks, review agent PRs, provide context |
| **Strategic VP HR/People** | Owns organizational capability strategy | Define capability requirements per strategic priority, review readiness |
| **L&D Lead** | Owns learning effectiveness and program design | Design learning paths, measure learning-to-outcome linkage, close capability gaps |
| **OD Lead** | Owns organizational design and role architecture | Define role families, proficiency ladders, org capability maturity |

### Agent Users

| Agent | Description | Primary Jobs |
|-------|-------------|-------------|
| **Maker Agent** | Produces code, specs, configs (Claude Code, Foundry, Copilot) | Execute spec tasks, create PRs, produce artifacts |
| **Judge Agent** | Evaluates output quality (eval framework, benchmark runners) | Score agent output, gate releases, flag regressions |
| **Ops Agent** | Monitors runtime, reports metrics (observability agents) | Report runtime evidence, flag health issues, update KR metrics |
| **Review Synthesis Agent** | Prepares review packs, summarizes evidence | Pre-populate review inputs, flag anomalies, draft summaries |

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

### J6: VP HR/People -- "Show me capability readiness by strategic priority"

> For each strategic objective, I need to see: what human capabilities are required, what is our current proficiency, where are the gaps, and are our learning interventions closing those gaps. Same for agent capabilities: what skills/tools are needed, what is the eval state, where are we under-invested.

### J7: L&D Lead -- "Show me learning effectiveness"

> For each learning intervention, I need to see: which capability gap it targets, which strategic priority it serves, what the completion and assessment data says, and whether the operating outcome improved. Learning without outcome linkage is waste.

### J8: OD Lead -- "Show me organizational capability maturity"

> Across all role families and agent roles, I need a heat map of capability coverage vs. requirement. Where are we strong, where are we fragile, and what is the trajectory.

---

## Product Principles

### P1: Graph, Not List

Goals, KRs, initiatives, specs, work items, agent runs, capabilities, and evidence form a **directed acyclic graph**, not a flat list. The graph is the product.

### P2: Derived Status is Default

Status is computed from source system evidence by default. Manual status is an override, not the norm.

### P3: Evidence is Addressable

Every piece of evidence (a PR, a pipeline run, an eval score, a runtime metric, an assessment result) has a stable URI and can be referenced from any entity in the graph.

### P4: Agents are Participants, Not Tools

Agents appear in the graph as participants with identity, capability declarations, confidence scores, and audit trails. They are not invisible background processes.

### P5: Staleness is Visible

If evidence is older than its freshness policy (e.g., runtime metric older than 24h), the system flags it as stale. Stale evidence degrades derived status to **unverified**.

### P6: Reviews are Structured

Review ceremonies have defined inputs (evidence, drift flags, orphan reports), defined outputs (decisions, action items, approvals), and defined cadence. They are not ad-hoc meetings.

### P7: Layered Authority

The system respects a layered authority model: source systems are authoritative for their domain, Diva Goals is authoritative for orchestration and review, humans are authoritative for approval.

### P8: Capability Is Load-Bearing

Capability requirements on strategic priorities are not decorative metadata. They are constraints that affect readiness status and surface in review ceremonies as blockers when unmet.

---

## Functional Areas

### FA1: Strategy Model

Objectives, Key Results, Initiatives -- imported from Azure Boards, enriched with measurement definitions, initiative-to-spec linkage, portfolio groupings, and capability requirements.

### FA2: Execution Graph

The agentic SDLC chain: Spec -> Work Items -> Agent Runs -> PRs -> Pipelines -> Eval Gates -> Releases. Each entity traced to source systems with derived status.

### FA3: Capability Intelligence

Role families, proficiency ladders, capability gap scoring, strategic-priority-to-capability mapping. For humans: skill taxonomies, assessment evidence, learning-path linkage. For agents: tool catalogs, knowledge-base coverage, eval scores.

### FA4: Agent Development Intelligence

Agent role catalog, skill-pack metadata, eval/readiness tiers, autonomy levels (supervised, semi-autonomous, autonomous), promotion and degradation rules, maker/judge separation enforcement.

### FA5: Human + Agent Operating Model

The unified flow: Goal -> Capability Requirement -> Learning Path (human) or Skill-Pack Plan (agent) -> Work -> Evidence -> Outcome. This is the capability-axis twin of the execution graph.

### FA6: L&D/OD Workflows

Strategic capability planning (what do we need?), learning effectiveness measurement (are interventions working?), capability debt tracking (where are we falling behind?), readiness review preparation.

### FA7: Agent Workforce Governance

Role catalog (what agents exist, what can they do), maker/judge separation (no agent both produces and evaluates its own output), degradation rules (agent downgraded on eval failure), autonomy tier management.

### FA8: Review Engine

Execution review (weekly), portfolio review (monthly), capability/readiness review (quarterly), agent readiness review (quarterly), exception review (on-demand). Each review has defined inputs, outputs, and decision tracking.

### FA9: Evidence Engine

Ingest evidence from all source systems. Compute derived status. Detect staleness, drift, and orphans. Surface coverage gaps.

### FA10: Agent Runtime Model

- **Orchestration**: Microsoft Agent Framework SDK for multi-agent workflow graphs
- **Managed Runtime**: Azure AI Foundry Agent Service for hosted agent execution
- **Knowledge**: Foundry IQ via MCP (`knowledge_base_retrieve`) for domain knowledge access
- **Evaluation**: Foundry evaluators -- `task_completion`, `task_adherence`, `intent_resolution`, `tool_call_accuracy`
- **Observability**: Traceable telemetry in Foundry tracing + Azure Monitor

---

## Success Metrics

### Execution Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Goal-to-execution traceability | 100% of active goals have downstream execution links | Graph coverage query |
| Evidence-backed status | >= 90% of status transitions backed by source system evidence | Audit log analysis |
| Drift detection latency | < 1 hour from source system event to drift flag | Event processing lag |
| Orphan detection coverage | 100% of entities checked weekly | Review engine output |
| Review ceremony completion | 100% of scheduled reviews produce structured output | Review log |
| Agent participation visibility | 100% of agent runs linked to work items and specs | Graph coverage query |
| Stale evidence flagging | 100% of evidence past freshness policy flagged within 1h | Evidence engine metrics |

### Human Capability Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Time-to-readiness | Median time from capability gap identification to certified readiness | Learning record timestamps |
| Capability coverage by priority | >= 80% of strategic priorities have assessed capability coverage | Gap analysis query |
| Learning-to-outcome linkage | >= 70% of learning interventions linked to operating outcomes | Evidence chain query |

### Agent Capability Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Eval pass rate (by agent role) | >= 85% first-attempt pass on target eval suite | Foundry eval pipeline |
| Hallucination rate | < 5% across all agent roles | Foundry groundedness evaluator |
| Skill-pack coverage | >= 90% of agent roles have registered skill packs with eval baselines | Agent registry query |

### Organizational Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Capability gap risk score | Declining trend, quarter-over-quarter | Gap scoring model |
| Readiness by initiative | >= 75% of active initiatives have full capability coverage | Readiness query |
| Agent autonomy distribution | Increasing proportion of agents at semi-autonomous or autonomous tiers | Registry query |

---

## Non-Goals

Diva Goals is explicitly **not**:

- **A replacement for Azure Boards**: Azure Boards remains the source of truth for work items, epics, features, and backlog management. Diva Goals reads from Boards, it does not replace it.
- **A replacement for GitHub**: GitHub remains the source of truth for code, PRs, and repositories. Diva Goals reads PR status and evidence, it does not manage code.
- **A replacement for observability tools**: Application Insights, Databricks, and Power BI remain the source of truth for runtime metrics and health. Diva Goals reads metrics as evidence, it does not collect telemetry.
- **A general-purpose project management tool**: Diva Goals does not manage sprints, kanban boards, or task assignment. It manages the strategy-to-execution-to-evidence graph.
- **A standalone product**: Diva Goals is a control plane that requires Azure Boards, GitHub, CI/CD, and observability as foundational systems. It has no value without them.
- **An LMS (Learning Management System)**: Diva Goals does not host courses, manage enrollment, or deliver content. It reads learning evidence from L&D systems and links it to capability requirements.
- **An HRIS**: Diva Goals does not manage employee records, compensation, or benefits. It reads role and proficiency data as inputs to the capability model.
- **A chatbot directory**: Diva Goals does not provide a catalog for end-user-facing chatbots. It governs agent capability and readiness for the agentic SDLC, not consumer-facing conversational AI.

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

### Phase 6: Capability Model (Weeks 17-20)

- Human capability taxonomy and role families
- Proficiency ladders and gap scoring
- Strategic-priority-to-capability mapping
- Learning-path model and evidence linkage

### Phase 7: Agent Development Governance (Weeks 21-24)

- Agent role catalog and skill-pack metadata
- Eval-based readiness tiers and autonomy management
- Degradation rules and supervision model
- Capability and agent readiness review ceremonies

---

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Source system API rate limits | Medium | High | Batch ingestion, caching, webhook-first where available |
| Evidence freshness lag | Medium | Medium | Event-driven ingestion, explicit staleness flags |
| Agent confidence calibration | High | Medium | Start conservative (low threshold = human review), tune over time |
| Scope creep into project management | High | High | Constitution non-goals, regular scope reviews |
| Adoption resistance (manual status habit) | Medium | Medium | Default to derived status, make override friction visible |
| Capability model over-engineering | Medium | Medium | Start with role families and gap scores; defer proficiency ladders until Phase 6 |
| Agent governance overhead | Medium | Low | Automate eval pipelines; manual review only for autonomy promotions |

---

## Open Questions

1. **Storage**: Should the Diva Goals graph live in Databricks (Delta tables) or a dedicated graph store? Current lean: Databricks for durability and query, with materialized views for the graph.
2. **Real-time vs. batch**: Should evidence ingestion be real-time (webhook/event-driven) or batch (scheduled)? Current lean: event-driven for CI/CD, batch for runtime metrics.
3. **UI surface**: Should the primary UI be Power BI dashboards, a custom web app, or both? Current lean: Power BI for read-only views, custom app for review ceremonies.
4. **Agent task assignment**: Should Diva Goals actively assign tasks to agents, or should agents pull from a queue? Current lean: pull model with priority signals.
5. **Multi-org**: Is Diva Goals single-tenant (InsightPulse AI only) or designed for multi-tenant from the start? Current lean: single-tenant first, multi-tenant later.
6. **Capability taxonomy source**: Should the role-family and proficiency-ladder taxonomy be maintained in Diva Goals YAML or imported from an external HR system? Current lean: YAML-first, import later.
7. **Agent eval frequency**: How often should agents be re-evaluated for autonomy tier maintenance? Current lean: on every production deployment, with quarterly full-suite re-eval.

---

*Product: Diva Goals*
*Version: 2.0*
*Last updated: 2026-03-23*
