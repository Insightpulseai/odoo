# Agent Factory / Agent Orchestration Platform - Product Requirements Document

> Spec bundle: `spec/agent-factory/`
> Companion: `spec/agent-factory/constitution.md` (normative doctrine)
> Owner: `@Insightpulseai-net/platform`
> Status: Draft
> Version: 1.0
> Date: 2026-03-19

---

## 1. Product Vision

The Agent Factory is a platform that treats autonomous agents as governed software products, providing a factory assembly line from concept to retirement. Every agent passes through typed stage gates, accumulates machine-verifiable evaluation evidence, and operates under policy constraints enforced by a typed task bus and a maker-judge separation model. The platform is designed for a one-man-team operating model where a single platform operator governs a portfolio of maker and judge agents that execute work, evaluate quality, and self-manage lifecycle progression with human override always available.

---

## 2. Problem Statement

The InsightPulse AI monorepo contains 142 agent capabilities scattered across multiple readiness levels. Six agents are nominally registered in `agents/registry/agents.yaml`, but the current state has critical gaps:

| Gap | Impact |
|-----|--------|
| **No formal lifecycle.** Agents jump from concept to "deployed" with no intermediate validation. | Unreliable agents reach production. No way to assess readiness. |
| **No typed task bus.** Agents call each other directly or through ad-hoc integrations. | Tight coupling. No kill switch. No routing observability. |
| **No stage gates.** Promotion decisions are implicit and undocumented. | No audit trail. No rollback criteria. No evidence of fitness. |
| **No maturity scoring.** All agents are treated as equal regardless of evaluation history. | Over-trust in untested agents. Under-utilization of proven ones. |
| **No promotion records.** There is no append-only log of when and why an agent was promoted or demoted. | Cannot reconstruct lifecycle history. Cannot identify regression causes. |
| **No maker-judge separation.** Agents that produce work are not structurally prevented from evaluating it. | Self-validation bias. Quality is asserted, not proven. |
| **No retirement workflow.** Deprecated agents are silently abandoned, not formally decommissioned. | Orphaned infrastructure. Ambiguous ownership. Routing to dead agents. |
| **No portfolio governance.** The operator has no single view of agent health, maturity distribution, or risk concentration. | Blind spots in the agent portfolio. Reactive instead of proactive management. |

The Agent Factory closes these gaps by imposing structure, automation, and machine-verifiable evidence on the entire agent lifecycle.

---

## 3. Personas

### 3.1 Platform Operator

The solo developer who owns the entire stack. Designs agents, writes policies, reviews promotions, manages infrastructure. Cannot afford manual ceremony for routine operations. Needs CI-enforced gates, CLI-driven workflows, and agent-assisted governance. This person is the final human authority for all policy overrides and destructive decisions.

**Key needs:** Single-pane portfolio view. Automated promotion pipelines. Alert-driven exception handling. Zero-ceremony routine operations.

### 3.2 Maker Agent

An agent that produces work: deploys modules, generates reports, writes code, runs ETL pipelines, reconciles data. Maker agents receive tasks from the task bus, execute them within policy constraints, and emit structured results. They never evaluate their own output.

**Examples:** odoo-sage (ERP operations), devops-prime (CI/CD), data-forge (ETL), ui-craft (frontend).

**Key needs:** Clear task contracts. Declared tool bindings. Bounded execution time. Externalized state.

### 3.3 Judge Agent

An agent that evaluates the quality of work produced by maker agents. Judge agents are structurally independent: they cannot share code, state, or policy bindings with the maker agents they evaluate. Judge agents produce structured evaluation records with pass/fail verdicts and evidence references.

**Examples:** quality-sentinel (code quality), compliance-auditor (policy compliance), perf-guardian (performance), security-prober (vulnerability assessment).

**Key needs:** Read-only access to maker outputs. Structured evaluation schemas. Independence from maker agent lifecycle.

### 3.4 Orchestrator

The top-level routing agent that manages task distribution, conflict resolution, and escalation. The orchestrator reads the agent registry, consults routing rules, and dispatches tasks to qualified agents based on task type, agent maturity, and current load. The orchestrator does not produce domain work -- it manages the flow of work.

**Key needs:** Registry access. Routing rules engine. Escalation paths. Kill switch authority.

---

## 4. Product Goals

| # | Goal | Success Indicator |
|---|------|-------------------|
| G1 | **Every agent is a governed product.** Passport, contract, evaluation history, and promotion record for all agents. | 100% of registered agents have valid passports. Zero agents in production without evaluation evidence. |
| G2 | **All inter-agent communication flows through the typed task bus.** No direct agent-to-agent calls. | Zero direct invocations detected in runtime telemetry. All tasks have typed envelopes. |
| G3 | **Promotion is evidence-based and deterministic.** Stage gates are codified. Evaluation results are machine-verifiable. | Zero promotions without gate passage records. Zero narrative-only evidence accepted. |
| G4 | **Maker-judge separation is structural.** No agent evaluates its own output. Judge agents are independent. | Evaluation routing rules provably exclude producing agents from judge pool. |
| G5 | **One-man-team operable.** Every routine operation is automated or agent-assisted. Human intervention is reserved for policy exceptions. | Routine promotions require zero manual steps. Alert-driven exception handling only. |
| G6 | **Portfolio governance is real-time.** The operator has a single view of agent maturity distribution, health, risk, and lifecycle stage. | Dashboard with live maturity distribution, health signals, and drift alerts. |
| G7 | **Retirement is formal.** Deprecated agents follow a 30-day sunset with successor validation, task draining, and passport archival. | Zero silently abandoned agents. All retirements have records with successor references. |

---

## 5. Major Capabilities

### 5.1 Agent Registry with Passports

Authoritative YAML registry of all agents with passport schema validation. Each agent has: ID, version, domain, maturity level, lifecycle stage, contract reference, skill bindings, tool bindings, policy bindings, promotion history, evaluation history, ownership.

**Artifact:** `agents/registry/agents.yaml` + `agents/passports/<agent-id>.yaml`

### 5.2 Task Bus with Typed Envelopes

Central message broker for all inter-agent work. Every task is a typed envelope with: task ID, type (dot-delimited), priority, payload, source/target agent, correlation ID, timeout, idempotency key. The task bus handles routing, failure, retry, dead-letter, and state transitions.

**Artifact:** `packages/taskbus/`

### 5.3 Factory Assembly Line (16 Stages)

End-to-end pipeline from `S01:intake` to `S16:retired`. Each stage has required artifacts, entry criteria, and exit gates. Stages are traversed forward; backward movement requires a demotion record.

**Artifact:** Stage definitions in constitution (section 4.2). Gate implementations in `agents/foundry/gates/`.

### 5.4 Maturity Model (L0-L5)

Six-level maturity model mapping to lifecycle stages and determining agent permissions: L0 (concept), L1 (prototype), L2 (evaluated), L3 (deployed), L4 (production), L5 (mature). Each level has specific capability requirements, evidence requirements, and blast radius limits.

### 5.5 Stage Gates with Promotion Records

Deterministic, binary gates at each promotion boundary. Gate criteria are codified in YAML. Gate evaluation produces structured pass/fail results. Promotion records are append-only and include evidence references, gate results, and approver identity.

**Artifact:** `agents/foundry/gates/` + `agents/promotions/<agent-id>/`

### 5.6 Evaluation Framework (Deterministic + Judge)

Two-tier evaluation: deterministic evaluations (unit tests, integration tests, schema validation) and judge evaluations (quality assessment by structurally independent judge agents). All evaluations produce machine-verifiable evidence.

**Artifact:** `agents/evals/<agent-id>/`

### 5.7 Orchestration Engine

Top-level routing engine that reads the registry, consults routing rules, and dispatches tasks. Handles: type-based routing, maturity-based priority, load awareness, conflict resolution, escalation to human, and kill switch enforcement.

### 5.8 Runtime Observability

Mandatory telemetry for all agent executions: OTLP traces, structured metrics, JSON logs, health heartbeats. Every span carries agent ID, task ID, task type, correlation ID, and maturity level.

**Destination:** Azure Monitor + Sentry.

### 5.9 Portfolio Governance

Aggregate view of the agent portfolio: maturity distribution, health signals, drift detection, risk concentration, lifecycle velocity. Enables the platform operator to manage agents as a portfolio rather than individually.

### 5.10 Retirement Workflow

Formal decommissioning process: deprecation notice (S14), 30-day sunset period (S15), task draining, successor validation, passport archival, retirement record (S16). Successor agents must be L2+ before predecessor enters sunset.

---

## 6. Functional Requirements

### Registry & Identity

| ID | Title | Description | Priority |
|----|-------|-------------|----------|
| FR-001 | Agent Registration | Register a new agent by creating a passport YAML file conforming to `ipai.passport.v1` schema. Passport must include: agent ID (kebab-case, globally unique), version (semver), domain, purpose, owners, contract reference. Registration triggers CI validation. | P0 |
| FR-002 | Registry Validation | CI pipeline validates all passports on every PR touching `agents/`. Checks: schema conformance, ID uniqueness, required fields present, referenced contracts exist, referenced policies exist. Hard gate -- PR cannot merge if validation fails. | P0 |
| FR-003 | Agent Discovery | Query the registry by domain, maturity level, lifecycle stage, task type capability, or owner. Returns matching agent IDs with current passport summary. Supports both CLI query and programmatic API. | P1 |
| FR-004 | Passport Versioning | Passport changes are tracked via git history. Every passport modification must increment `updated_at`. Contract changes require version bump. | P0 |

### Task Bus

| ID | Title | Description | Priority |
|----|-------|-------------|----------|
| FR-005 | Task Submission | Accept a task envelope conforming to `ipai.task.v1` schema. Validate: required fields present, task type exists in routing table, payload conforms to type-specific schema. Reject malformed tasks with structured error. | P0 |
| FR-006 | Task Routing | Route tasks by `type` field to agents that declare that type in their contract `task_types` field. When multiple agents qualify, select the highest-maturity agent. Ties broken by explicit priority in registry. Reject tasks for retired agents (S15+) with `AGENT_RETIRED` error. | P0 |
| FR-007 | Task State Machine | Track task state transitions: `pending` -> `routed` -> `accepted` -> `executing` -> `completed` / `failed` / `timed_out`. Emit state change events. Persist state to `ops.task_state` (Supabase). | P0 |
| FR-008 | Task Timeout | Enforce hard timeout (default 10 minutes, configurable per task type). On timeout: mark task `timed_out`, emit alert, escalate per policy. | P0 |
| FR-009 | Dead Letter Queue | Tasks that fail routing (no qualified agent, all agents at capacity, task type unknown) are placed in a dead letter queue. Dead letters trigger Slack notification to operator. Dead letter queue is queryable. | P1 |
| FR-010 | Idempotency | Deduplicate tasks by `idempotency_key`. If a task with the same key has completed within the deduplication window (default 24 hours), return the previous result instead of re-executing. | P1 |

### Assembly Line & Stage Gates

| ID | Title | Description | Priority |
|----|-------|-------------|----------|
| FR-011 | Stage Tracking | Track each agent's current lifecycle stage (S01-S16) in its passport. Stage changes produce audit log entries. Forward progression requires gate passage. Backward movement requires demotion record. | P0 |
| FR-012 | Gate Definition | Define stage gates as YAML files in `agents/foundry/gates/`. Each gate specifies: source stage, target stage, required criteria (list of checks), required evidence (list of artifact paths/patterns). Gates are deterministic: pass or fail, no conditional results. | P0 |
| FR-013 | Gate Evaluation | Evaluate a gate by running all specified criteria checks against the agent's current state. Produce a structured result: gate ID, agent ID, timestamp, per-criterion pass/fail with detail, overall verdict. Persist result to `agents/promotions/<agent-id>/`. | P0 |
| FR-014 | Promotion Execution | On gate passage: update agent passport (stage, maturity level, updated_at), write promotion record (append-only), update registry. Promotion records are immutable once written. | P0 |
| FR-015 | Demotion Execution | On demotion: create a demotion record referencing the original promotion. Update passport to lower stage/maturity. Original promotion record remains intact. Demotion triggers alert to operator. | P1 |

### Evaluation

| ID | Title | Description | Priority |
|----|-------|-------------|----------|
| FR-016 | Evaluation Suite Definition | Define evaluation suites as YAML scenario files in `agents/evals/<agent-id>/scenarios/`. Each scenario specifies: input, expected behavior, acceptance criteria, judge assignment (for L2+ evaluations). | P0 |
| FR-017 | Deterministic Evaluation | Execute unit and integration evaluation scenarios. Produce structured results: scenario ID, input hash, output, verdict (pass/fail), duration, error details. No human judgment required. | P0 |
| FR-018 | Judge Evaluation | Route evaluation tasks to qualified judge agents. Judge agents produce structured reviews: scenario ID, maker agent ID, quality score, verdict, evidence references, recommendations. Judge agents must be independent (no shared code/state/policy with maker). | P0 |
| FR-019 | Evaluation Evidence Persistence | Persist all evaluation results to `agents/evals/<agent-id>/results/<run-id>.json`. Evidence must be machine-parseable. Narrative-only evidence is rejected by gate validators. | P0 |

### Orchestration

| ID | Title | Description | Priority |
|----|-------|-------------|----------|
| FR-020 | Orchestrator Routing Engine | Top-level routing that consults registry, routing rules, and agent health to dispatch tasks. Supports: type-based routing, maturity-weighted selection, load-aware distribution, explicit agent targeting (override). | P0 |
| FR-021 | Conflict Resolution | When multiple agents qualify for a task and have equal maturity, resolve by: (1) explicit priority in registry, (2) lowest current task count, (3) most recent successful evaluation. | P1 |
| FR-022 | Escalation | Unroutable tasks (no qualified agent, all agents unhealthy, policy violation) escalate to the platform operator via Slack notification and `ops.unroutable_tasks` log entry. Escalation includes: task details, reason, suggested resolution. | P0 |
| FR-023 | Kill Switch | Immediately stop all task routing to a specific agent. In-flight tasks are allowed to complete (with timeout). Kill switch is available via CLI, API, and Slack command. Kill switch events are logged to `ops.kill_switch_events`. | P0 |

### Observability

| ID | Title | Description | Priority |
|----|-------|-------------|----------|
| FR-024 | Trace Emission | Every agent execution emits OTLP spans with required attributes: `agent.id`, `task.id`, `task.type`, `correlation.id`, `maturity.level`. Spans routed to Azure Monitor. 30-day retention. | P0 |
| FR-025 | Metrics Emission | Every agent emits: `agent.<id>.task.count`, `agent.<id>.task.duration_ms`, `agent.<id>.task.error_rate`. Routed to Azure Monitor. 90-day retention. | P0 |
| FR-026 | Health Heartbeat | Every active agent (S08+) emits a heartbeat every 60 seconds. Missing heartbeat for 5 minutes triggers health alert. Task bus stops routing to unhealthy agents. | P1 |
| FR-027 | Portfolio Dashboard | Aggregate view showing: maturity distribution (histogram of L0-L5), health status per agent, task throughput, error rates, drift alerts, lifecycle velocity (average time per stage). | P1 |

### Retirement

| ID | Title | Description | Priority |
|----|-------|-------------|----------|
| FR-028 | Deprecation Notice | Mark an agent as deprecated (S14). Record: reason, successor agent ID (if any), sunset start date. Successor must be L2+ before predecessor enters S14. | P1 |
| FR-029 | Sunset Enforcement | After 30 days at S14, agent moves to S15 (sunset). Task bus stops routing new tasks. In-flight tasks drain with timeout. | P1 |
| FR-030 | Retirement Completion | After all tasks drain, agent moves to S16 (retired). Passport archived to `agents/passports/retired/`. Retirement record written. Record is permanent and append-only. | P1 |

---

## 7. Non-Functional Requirements

| ID | Title | Description | Priority |
|----|-------|-------------|----------|
| NFR-001 | Task Routing Latency | Task routing decision (submission to agent acceptance) must complete within 500ms at p95 for the current agent portfolio size (< 50 agents). | P0 |
| NFR-002 | Task Bus Reliability | Task bus must achieve 99.9% message delivery. No task silently dropped. Failed deliveries go to dead letter queue. | P0 |
| NFR-003 | Auditability | Every promotion, demotion, retirement, policy override, and kill switch event must have a machine-readable audit record. Records are append-only and queryable by agent ID, timestamp range, and event type. | P0 |
| NFR-004 | Extensibility | New task types, agent domains, evaluation scenarios, and policy types can be added without modifying core platform code. Extension points are schema-driven (YAML/JSON). | P1 |
| NFR-005 | Security | Agents cannot access secrets directly. Tool bindings resolve secrets via Azure Key Vault at runtime. Agent process sees opaque references only. Destructive operations require explicit human approval token. | P0 |
| NFR-006 | One-Man-Team Operability | All routine operations (registration, evaluation, promotion, deployment, monitoring) must be executable by a single operator using CLI tools, CI pipelines, and agent assistance. No process requires synchronous multi-person coordination. | P0 |
| NFR-007 | Idempotency | All agent executions must be idempotent. Re-execution of the same task (same idempotency key) must not produce side effects beyond the first execution. | P0 |
| NFR-008 | Graceful Degradation | Task bus failure must not cascade to agent execution. Agents that cannot reach the task bus must queue tasks locally and retry. Registry unavailability must not prevent in-flight task completion. | P1 |
| NFR-009 | Schema Evolution | Task envelope, passport, and promotion record schemas must support backward-compatible evolution. Old schema versions remain parseable. Schema version is declared in every record. | P1 |
| NFR-010 | Recovery Time | Mean time to recover (MTTR) from a single agent failure must be under 5 minutes with automated detection and kill switch. Portfolio-wide recovery (task bus restart) must complete under 15 minutes. | P1 |
| NFR-011 | Telemetry Completeness | 100% of agent executions at L3+ must emit traces and metrics. Missing telemetry from an L3+ agent triggers a health alert within 5 minutes. | P0 |

---

## 8. Agent Lifecycle

The canonical lifecycle is a 14-phase pipeline. Every agent traverses these phases from intake to retirement. Phases map to lifecycle stages (S01-S16) and maturity levels (L0-L5).

```
                                AGENT LIFECYCLE
  ┌─────────────────────────────────────────────────────────────────────────┐
  │                                                                         │
  │  DEFINE                    BUILD & TEST                                 │
  │  ┌──────────┐  ┌───────────────┐  ┌──────────┐  ┌───────────────────┐  │
  │  │ Intake   │─>│ Qualification │─>│   Spec   │─>│    Contract       │  │
  │  │ (S01)    │  │    (S01)      │  │  (S02)   │  │    (S02)          │  │
  │  │ L0       │  │    L0         │  │  L0      │  │    L0             │  │
  │  └──────────┘  └───────────────┘  └──────────┘  └───────────────────┘  │
  │       │                                              │                  │
  │       v                                              v                  │
  │  ┌──────────┐  ┌───────────────┐  ┌──────────┐  ┌───────────────────┐  │
  │  │ Assembly │─>│  Simulation   │─>│ Testing  │─>│   Evaluation      │  │
  │  │ (S03)    │  │    (S04)      │  │ (S04-05) │  │   (S06-07)        │  │
  │  │ L1       │  │    L1         │  │  L1      │  │    L2             │  │
  │  └──────────┘  └───────────────┘  └──────────┘  └───────────────────┘  │
  │                                                      │                  │
  │  PROMOTE & DEPLOY                                    v                  │
  │  ┌──────────┐  ┌───────────────┐  ┌──────────┐  ┌───────────────────┐  │
  │  │Governance│─>│   Staging     │─>│Production│─>│   Operations      │  │
  │  │ (S07)    │  │    (S08-09)   │  │ (S10)    │  │   (S10-12)        │  │
  │  │ L2       │  │    L3         │  │  L4      │  │    L4             │  │
  │  └──────────┘  └───────────────┘  └──────────┘  └───────────────────┘  │
  │                                                      │                  │
  │  OPTIMIZE & RETIRE                                   v                  │
  │  ┌──────────┐  ┌───────────────┐                                       │
  │  │Optimize  │─>│  Retirement   │                                       │
  │  │ (S13)    │  │  (S14-16)     │                                       │
  │  │ L5       │  │  L5->archive  │                                       │
  │  └──────────┘  └───────────────┘                                       │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘
```

### Phase Details

| Phase | Stage(s) | Maturity | Entry Criteria | Exit Criteria | Artifacts Produced |
|-------|----------|----------|----------------|---------------|--------------------|
| Intake | S01 | L0 | Blueprint submitted | Passport created, owner assigned | `agents/passports/<id>.yaml` |
| Qualification | S01 | L0 | Passport exists | Domain validated, no ID conflict, purpose distinct from existing agents | Qualification record |
| Specification | S02 | L0 | Qualified | Input/output schemas defined, task types declared | Contract draft |
| Contract | S02 | L0 | Schemas defined | Contract validates against `ipai.manifest.v1`, tools and policies declared | `agents/foundry/agents/<id>.manifest.yaml` |
| Assembly | S03 | L1 | Contract valid | Agent implementation exists, skill bindings functional, tool bindings resolve | Agent code + skill bindings |
| Simulation | S04 | L1 | Implementation exists | Sandbox execution completes without crash, basic scenarios pass | Sandbox execution logs |
| Testing | S04-S05 | L1 | Simulation passes | Unit evaluations pass, integration evaluations pass | `agents/evals/<id>/scenarios/`, `agents/evals/<id>/integration/` |
| Evaluation | S06-S07 | L2 | Tests pass | Full eval suite passes in sandbox, judge agent review complete, security review complete | `agents/evals/<id>/results/`, `agents/evals/<id>/judge-reviews/` |
| Governance | S07 | L2 | Evaluation complete | Policy compliance verified, blast radius acceptable, kill switch configured | Policy compliance record |
| Staging | S08-S09 | L3 | Governance passes | Canary deployment healthy, staging metrics within thresholds, 48-hour minimum canary period | Deployment evidence, staging metrics |
| Production | S10 | L4 | Staging passes | Full traffic, observability active, human override verified | `agents/promotions/<id>/<ts>-L4.yaml` |
| Operations | S10-S12 | L4 | Production deployed | Horizontal scaling validated, security hardening complete, edge cases covered | Operational runbooks |
| Optimization | S13 | L5 | 30-day clean production track record | Baseline status achieved, may serve as template for derived agents | Maturity certification |
| Retirement | S14-S16 | L5->archive | Successor at L2+ OR explicit operator decision | Deprecation noticed, tasks drained, passport archived | Retirement record |

---

## 9. Maturity Model

| Level | Name | Definition | Required Capabilities | Required Evidence | Required Controls | Evaluation Expectations | Observability Expectations | Allowed Blast Radius | Promotion Criteria | Rollback Triggers |
|-------|------|------------|----------------------|-------------------|-------------------|------------------------|---------------------------|---------------------|--------------------|-------------------|
| L0 | Concept | Design-only. No executable code. Blueprint and contract drafts. | None (design artifacts only) | Passport exists. Contract schema validates. | None | None | None | None (no execution) | Contract validates against schema. Blueprint reviewed by operator. | N/A (no execution to roll back) |
| L1 | Prototype | Sandbox-executable. No real data, no real tools. | Basic task handling. Skill bindings resolve. Tool bindings resolve in sandbox. | Sandbox execution log. Unit evaluation results (>= 80% pass rate). Integration evaluation results. | Sandbox isolation. No network access to production resources. | Unit + integration evaluations defined and passing. Minimum 10 scenarios. | Execution logs emitted to sandbox telemetry sink. | Sandbox only. Zero production impact. | Unit + integration evals pass. Sandbox execution completes without crash. | Any crash or unhandled exception in sandbox. |
| L2 | Evaluated | Full evaluation suite passes. Judge-reviewed. Security-assessed. | All L1 capabilities + evaluation scenario coverage >= 80% of declared task types. | Full eval suite results. Judge agent review record. Security review checklist complete. | Judge independence verified (no shared code/state/policy). Security review by operator or security-prober agent. | Full eval suite in sandbox with evaluation data. Judge review with structured verdict. >= 90% scenario pass rate. | Structured evaluation results persisted. Judge review records persisted. | Sandbox with evaluation data (may include anonymized production data). | Full eval suite passes. Judge review verdict is "approve". Security review complete with no critical findings. | Judge review verdict is "reject". Critical security finding. |
| L3 | Deployed | Canary/staging deployment with real data. Kill switch mandatory. | All L2 capabilities + real tool bindings resolve. Health heartbeat active. Kill switch functional. | Canary deployment evidence. Staging metrics (latency, error rate, throughput) within thresholds. 48-hour minimum canary period with no critical incidents. | Kill switch mandatory and tested. Human override endpoint active. Policy engine enforcing tool allowlists. Rate limiting active. | Canary period metrics within defined thresholds: error rate < 5%, p95 latency < 2s, zero data corruption incidents. | OTLP traces emitted. Metrics published. Health heartbeat every 60s. Alerts configured for anomalies. | Canary: shadow traffic or <= 10% of real traffic. Staging: full traffic in non-production environment. | 48-hour canary clean. Staging metrics within thresholds. Kill switch tested. No critical incidents. | Error rate > 10%. Latency p95 > 5s. Any data corruption. Kill switch failure. Missing heartbeat > 10 minutes. |
| L4 | Production | Full production deployment. Full traffic. Observability mandatory. | All L3 capabilities + horizontal scaling tested. Runbooks exist. On-call alerting configured. | Production metrics for >= 7 days. Zero critical incidents. Runbook coverage for top 5 failure modes. | All L3 controls + production alerting. Escalation paths defined. Automatic rollback on error rate spike. | Continuous evaluation: weekly automated eval suite re-run. Monthly judge review. Drift detection active. | Full OTLP trace coverage. Dashboard with real-time metrics. Alerting on error rate, latency, throughput anomalies. SLO tracking. | Full production traffic for declared task types. | 7-day production clean. Weekly eval suite passing. Runbooks reviewed. Alerting verified. | Critical incident. Eval suite regression (drop > 10% from baseline). Drift detected without resolution for > 72 hours. |
| L5 | Mature | Proven production. Baseline for domain. Template for derived agents. | All L4 capabilities + 30-day clean production track record. Scenario coverage >= 80%. Served as reference for at least one domain decision. | 30-day production metrics. Zero critical incidents in 30 days. Coverage >= 80% of declared scenarios. Contribution to domain baseline documentation. | All L4 controls + policy tightening based on production learnings. Minimum privilege verified. | Quarterly comprehensive evaluation. Annual judge review. Drift detection with automated remediation. | Full L4 observability + trend analysis. Capacity planning data. Cost attribution. | Full production. May serve as routing fallback for lower-maturity agents in same domain. | 30 days clean production. Zero critical incidents. Coverage >= 80%. Operator certification. | Same as L4. Additionally: any quarter without eval re-run triggers automatic review. |

---

## 10. Task Bus Design

### 10.1 Task Envelope Schema

```typescript
interface TaskEnvelope {
  /** Schema identifier for version compatibility */
  schema: "ipai.task.v1";

  /** Globally unique task identifier (UUIDv7 for time-ordering) */
  task_id: string;

  /** Dot-delimited task type: task.<domain>.<action> */
  type: string;

  /** Execution priority */
  priority: "low" | "normal" | "high" | "critical";

  /** Type-specific payload, validated against per-type schema */
  payload: Record<string, unknown>;

  /** Agent or human that submitted the task */
  source_agent_id: string;

  /** Target agent (optional -- resolved by router if omitted) */
  target_agent_id?: string;

  /** Groups related tasks for correlation */
  correlation_id: string;

  /** ISO8601 creation timestamp */
  created_at: string;

  /** Hard timeout in milliseconds (default: 600000 = 10 min) */
  timeout_ms: number;

  /** Prevents duplicate execution within dedup window */
  idempotency_key: string;

  /** Optional metadata for routing hints, labels, trace context */
  metadata?: {
    /** Trace parent for distributed tracing propagation */
    traceparent?: string;
    /** Arbitrary key-value labels */
    labels?: Record<string, string>;
    /** Retry attempt number (0 = first attempt) */
    retry_attempt?: number;
    /** Maximum retry attempts before dead-letter */
    max_retries?: number;
  };
}
```

```yaml
# YAML equivalent for declarative task definitions
schema: ipai.task.v1
task_id: "01964a2b-7e3c-7f00-8000-000000000001"
type: "task.odoo.deploy-module"
priority: "normal"
payload:
  module_name: "ipai_finance_ppm"
  target_db: "odoo_staging"
  action: "install"
source_agent_id: "devops-prime"
target_agent_id: "odoo-sage"
correlation_id: "01964a2b-7e3c-7f00-8000-000000000000"
created_at: "2026-03-19T10:00:00Z"
timeout_ms: 600000
idempotency_key: "deploy-ipai_finance_ppm-odoo_staging-20260319"
metadata:
  traceparent: "00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01"
  labels:
    environment: "staging"
    triggered_by: "ci-pipeline"
  retry_attempt: 0
  max_retries: 3
```

### 10.2 Task State Model

```
                         TASK STATE TRANSITIONS

    ┌──────────┐     route      ┌──────────┐     accept     ┌──────────┐
    │ PENDING  │───────────────>│ ROUTED   │───────────────>│ ACCEPTED │
    └──────────┘                └──────────┘                └──────────┘
         │                           │                           │
         │ (no agent)                │ (agent rejects)           │ execute
         v                           v                           v
    ┌──────────┐               ┌──────────┐                ┌───────────┐
    │DEAD_LETTER│              │ REJECTED │                │ EXECUTING │
    └──────────┘               └──────────┘                └───────────┘
         │                           │                      /    |    \
         │ retry                     │ retry           ok  /     |     \ timeout
         v                           v                    v      |      v
    ┌──────────┐               ┌──────────┐         ┌─────────┐ │ ┌──────────┐
    │ PENDING  │               │ PENDING  │         │COMPLETED│ │ │TIMED_OUT │
    │ (retry)  │               │ (retry)  │         └─────────┘ │ └──────────┘
    └──────────┘               └──────────┘                     │
                                                                v
                                                           ┌──────────┐
                                                           │  FAILED  │
                                                           └──────────┘
                                                                │
                                                                │ retry
                                                                │ (if attempts < max)
                                                                v
                                                           ┌──────────┐
                                                           │ PENDING  │
                                                           │ (retry)  │
                                                           └──────────┘

  Terminal states: COMPLETED, DEAD_LETTER (after max retries)
  All state transitions emit events to ops.task_state_log
```

**State definitions:**

| State | Description | Transitions To |
|-------|-------------|---------------|
| `PENDING` | Task submitted, awaiting routing. | `ROUTED`, `DEAD_LETTER` |
| `ROUTED` | Router identified target agent. | `ACCEPTED`, `REJECTED` |
| `ACCEPTED` | Target agent acknowledged the task. | `EXECUTING` |
| `EXECUTING` | Agent is actively working on the task. | `COMPLETED`, `FAILED`, `TIMED_OUT` |
| `COMPLETED` | Task finished successfully. Terminal. | (none) |
| `FAILED` | Task execution failed. | `PENDING` (retry), `DEAD_LETTER` (max retries) |
| `TIMED_OUT` | Task exceeded `timeout_ms`. | `PENDING` (retry), `DEAD_LETTER` (max retries) |
| `REJECTED` | Agent rejected the task (policy, capacity). | `PENDING` (re-route), `DEAD_LETTER` |
| `DEAD_LETTER` | Undeliverable after all retries. Terminal. | (none -- requires human intervention) |

### 10.3 Routing Rules

| Rule | Priority | Description |
|------|----------|-------------|
| Explicit target | 1 (highest) | If `target_agent_id` is set and agent is healthy + eligible, route directly. |
| Type match + highest maturity | 2 | Match `type` against agent contract `task_types`. Select highest maturity. |
| Type match + load balance | 3 | Among equal-maturity agents, select lowest current task count. |
| Domain fallback | 4 | If no exact type match, check for domain-level wildcard handlers (e.g., `task.odoo.*`). |
| Escalation | 5 (lowest) | No match found. Place in dead letter queue. Notify operator. |

### 10.4 Failure Handling

| Failure Type | Detection | Response |
|-------------|-----------|----------|
| Agent crash during execution | Health heartbeat stops. Task timeout fires. | Mark task `FAILED`. Retry if attempts < max_retries. Kill switch agent if crash rate > threshold (3 crashes in 10 minutes). |
| Agent rejects task | Agent returns `REJECTED` with reason. | Re-route to next qualified agent. If no alternative, dead-letter. |
| Task timeout | `timeout_ms` exceeded. | Mark `TIMED_OUT`. Retry with exponential backoff if attempts < max_retries. |
| Payload validation failure | Router or agent detects schema violation. | Reject immediately. Do not retry (payload is deterministically invalid). Notify source agent. |
| Task bus unavailable | Agent cannot reach task bus endpoint. | Agent queues task locally (max 100 tasks, 5-minute TTL). Retry connection with exponential backoff. |

### 10.5 Retry / Recovery

| Parameter | Default | Configurable |
|-----------|---------|-------------|
| Max retries | 3 | Per task type |
| Backoff strategy | Exponential (1s, 2s, 4s) | Per task type |
| Deduplication window | 24 hours | Per task type |
| Dead letter retention | 7 days | Global |
| Dead letter alert | Immediate (Slack) | Global |
| Recovery from task bus restart | Replay incomplete tasks from `ops.task_state` | Automatic |

---

## 11. Success Metrics

### Task-Level Metrics

| Metric | Definition | Target | Alert Threshold |
|--------|-----------|--------|-----------------|
| Task Success Rate | `completed / (completed + failed + timed_out)` per task type per 1-hour window | >= 95% | < 90% |
| Task Latency (p50) | Median time from `PENDING` to `COMPLETED` | < 30s for routing tasks, < 5min for execution tasks | > 2x target |
| Task Latency (p95) | 95th percentile time from `PENDING` to `COMPLETED` | < 2min for routing tasks, < 8min for execution tasks | > 2x target |
| Dead Letter Rate | `dead_letter / total_submitted` per 1-hour window | < 1% | > 5% |
| Retry Rate | `retried_tasks / total_submitted` per 1-hour window | < 10% | > 20% |

### Agent-Level Metrics

| Metric | Definition | Target | Alert Threshold |
|--------|-----------|--------|-----------------|
| Agent Availability | `(heartbeat_received / heartbeat_expected)` per agent per 1-hour window | >= 99.5% for L4+ | < 99% |
| Tool Failure Rate | `tool_errors / tool_invocations` per agent per 1-hour window | < 2% | > 5% |
| Eval Score | Latest evaluation suite pass rate per agent | >= 90% for L2+, >= 95% for L4+ | Drop > 10% from previous run |
| Drift Rate | Evaluation score delta between consecutive runs | < 5% degradation | > 10% degradation |
| MTTR | Mean time from failure detection to agent recovery (kill switch + re-route or restart) | < 5 min | > 15 min |

### Stage-Level Metrics

| Metric | Definition | Target | Alert Threshold |
|--------|-----------|--------|-----------------|
| Stage Velocity | Average calendar days an agent spends in each stage | < 7 days for S01-S05, < 14 days for S06-S09 | > 2x target (stalled agent) |
| Gate Pass Rate | `gates_passed / gates_attempted` per stage boundary | >= 80% (first attempt) | < 50% (systemic readiness gap) |
| Promotion Throughput | Agents promoted per month | >= 2 (early phase) | 0 for > 30 days (pipeline stall) |
| Demotion Rate | Demotions per quarter | < 10% of promotions | > 25% (quality gate failure) |

### Portfolio-Level Metrics

| Metric | Definition | Target | Alert Threshold |
|--------|-----------|--------|-----------------|
| Maturity Distribution | Count of agents at each maturity level (L0-L5) | Pyramid shape: more L0-L1 than L4-L5 | Inverted pyramid (too many untested agents in production) |
| Portfolio Health Score | Weighted average of agent availability and eval scores | >= 90% | < 80% |
| Coverage Gap | Task types declared in registry but no agent at L3+ can handle | 0 | > 0 for > 7 days |
| Orphan Agent Count | Agents with no task executions in 30 days (not retired) | 0 | > 0 for > 14 days |
| Mean Agent Age | Average time since agent passport creation for active agents | Informational | N/A |

---

## 12. Risks

| # | Risk | Likelihood | Impact | Mitigation |
|---|------|-----------|--------|------------|
| R1 | **Over-engineering the lifecycle.** 16 stages and 6 maturity levels may be too granular for 6 agents, creating bureaucratic overhead. | Medium | Medium | Allow fast-track promotion paths that skip intermediate stages when evidence covers multiple gates. Review stage count at 20-agent threshold. |
| R2 | **Task bus becomes a bottleneck.** Single message broker handling all inter-agent communication is a single point of failure. | Medium | High | Implement local task queuing in agents (FR-010 failure handling). Task bus persistence in Supabase `ops.task_state` enables recovery from bus restart. Consider partitioned routing by domain at scale. |
| R3 | **Judge agent quality.** Judge agents are only as reliable as their evaluation criteria. Poor judges produce false confidence. | Medium | High | Bootstrap with deterministic evaluations first (schema validation, test suites). Introduce judge agents incrementally. Platform operator reviews judge verdicts quarterly. |
| R4 | **One-man-team fatigue.** Even with automation, the platform operator is the bottleneck for policy exceptions, security reviews, and architecture decisions. | High | High | Maximize automation for routine operations. Reserve human judgment for L3+ promotions and policy overrides only. Design for async review (CI-driven, not synchronous). |
| R5 | **Schema evolution breaks compatibility.** Task envelope, passport, and promotion record schemas will evolve. Breaking changes disrupt the pipeline. | Medium | Medium | Version all schemas (`ipai.task.v1`, `ipai.passport.v1`). Require backward-compatible changes. Old versions remain parseable. Breaking changes require migration scripts and major version bump. |
| R6 | **Evaluation drift.** Evaluation scenarios become stale as the platform evolves. Agents pass evaluations that no longer reflect real-world conditions. | Medium | Medium | Quarterly evaluation suite review. Automated drift detection comparing eval scenarios against actual task payloads. Flag divergence > 20% as stale. |
| R7 | **Premature agent proliferation.** Low barrier to agent creation leads to many L0-L1 agents that never reach production. | Medium | Low | Require qualification gate (FR-011) that validates purpose distinctness from existing agents. Quarterly orphan agent review. Auto-retire agents stalled at L0-L1 for > 90 days without activity. |
| R8 | **Azure runtime coupling.** Heavy reliance on Azure-specific services (Foundry, ACA, Key Vault, Monitor) makes migration expensive. | Low | High | Constitution P10 mandates cloud-agnostic core, Azure-native runtime. Agent contracts, policies, and evaluations are portable YAML. Only runtime bindings are Azure-specific. Migration cost is contained to the runtime plane. |

---

## 13. Out of Scope

The following are explicitly excluded from this version of the Agent Factory:

| Item | Reason | Future Consideration |
|------|--------|---------------------|
| **Multi-tenant agent isolation.** Each tenant getting isolated agent instances. | Single-tenant platform. One operator, one portfolio. | If the platform serves external customers. |
| **Agent marketplace.** Publishing or consuming agents from external registries. | No external consumers or suppliers in current operating model. | If the platform opens to third-party agents. |
| **Natural language policy authoring.** Defining policies in natural language instead of YAML schemas. | Ambiguity risk. Policies must be machine-verifiable. | After core schema-based policies are stable. |
| **Real-time agent collaboration.** Agents working together synchronously on a shared task. | Violates P6 (task bus is the backbone). All coordination is async via task bus. | Only if async proves insufficient for specific domain. |
| **Cost optimization engine.** Automated model routing based on cost/quality tradeoffs. | Premature optimization. Focus on correctness first. | After L4+ agents demonstrate stable cost profiles. |
| **Agent cloning / forking.** Creating new agents by cloning an existing agent's passport and contract. | Risks identity confusion. New agents should go through intake. | After naming and registry governance is proven. |
| **GUI for lifecycle management.** Web-based dashboard for managing agent lifecycle (promotion, demotion, retirement). | CLI-first, CI-first operating model. GUI adds maintenance burden. | After CLI workflows are stable and if operator efficiency demands it. |
| **Cross-repo agent orchestration.** Agents spanning multiple repositories. | Single monorepo model. All agents live in the same repo. | If multi-repo topology (per memory: `project_target_state_repos.md`) is adopted. |

---

## 14. Dependencies

### Internal Dependencies

| Dependency | Owned By | Required For | Status |
|-----------|----------|-------------|--------|
| `packages/agents/` | Platform team | Control plane implementation (registry, gates, promotions) | Exists (scaffold) |
| `packages/taskbus/` | Platform team | Task bus implementation (routing, state machine, dead letter) | Exists (scaffold) |
| `agents/registry/agents.yaml` | Platform team | Agent registry SSOT | Exists (6 agents registered) |
| `agents/foundry/` | Platform team | Agent contracts, tools, policies, gates | Exists (partial) |
| `spec/agent-factory/constitution.md` | Platform team | Normative doctrine for all platform behavior | Exists (v1.0, 2026-03-19) |
| `.github/workflows/` | Platform team | CI enforcement of registry validation, gate checks, naming lint | Exists (355 workflows, agent-specific gates TBD) |
| Supabase `ops.*` tables | Platform team | Task state persistence, agent memory, policy override logs | Exists (self-hosted on Azure VM) |

### External Dependencies

| Dependency | Provider | Required For | Risk |
|-----------|----------|-------------|------|
| Azure AI Foundry | Microsoft | Agent runtime execution, model hosting | Medium -- proprietary runtime. Mitigated by P10 (cloud-agnostic core). |
| Azure Container Apps | Microsoft | Agent deployment target | Medium -- standard container runtime. Portable to any container orchestrator. |
| Azure Key Vault | Microsoft | Secret resolution for tool bindings | Low -- standard secret management. Replaceable with any vault. |
| Azure Monitor | Microsoft | Telemetry ingestion (traces, metrics, logs) | Low -- OTLP protocol is standard. Replaceable with any OTLP-compatible backend. |
| Sentry | Sentry.io | Error tracking and alerting | Low -- supplementary to Azure Monitor. |
| Slack | Salesforce | Operator notifications, escalation alerts, kill switch commands | Low -- notification channel. Replaceable with any webhook-capable system. |
| PostgreSQL 16 | Azure managed | Supabase backing store for `ops.*` tables | Low -- standard database. |

---

## Appendix A: Schemas

### A.1 Task Envelope Schema (ipai.task.v1)

See section 10.1 for the full TypeScript interface and YAML equivalent.

### A.2 Agent Passport Schema (ipai.passport.v1)

```yaml
schema: ipai.passport.v1
agent_id: "<kebab-case, globally unique, immutable>"
name: "<Display Name>"
version: "<semver>"
domain: "<erp|devops|data|frontend|platform|finance>"
purpose: "<one-line description of what this agent does>"
owners:
  - "<github-user-or-team>"
current_stage: "S<nn>"
maturity_level: "L<n>"
contract_ref: "agents/foundry/agents/<agent-id>.manifest.yaml"
skills:
  - "agents/skills/<skill-name>/SKILL.md"
tools:
  - "agents/foundry/tools/<tool-name>.manifest.yaml"
policies:
  - "agents/foundry/policies/<policy-name>.policy.yaml"
task_types:
  - "task.<domain>.<action>"
memory_contract:
  store: "supabase"
  table: "ops.agent_memory"
  retention_days: 90
kill_switch:
  enabled: true                        # mandatory for L3+
  endpoint: "/agents/<agent-id>/kill"
  fallback: "task-bus-drain"
promotion_history:
  - ref: "agents/promotions/<agent-id>/<timestamp>.yaml"
evaluation_history:
  - ref: "agents/evals/<agent-id>/results/<run-id>.json"
created_at: "<ISO8601>"
updated_at: "<ISO8601>"
```

### A.3 Promotion Decision Schema (ipai.promotion.v1)

```yaml
schema: ipai.promotion.v1
agent_id: "<kebab-case>"
timestamp: "<ISO8601>"
from_level: "L<n>"
to_level: "L<n+1>"
from_stage: "S<nn>"
to_stage: "S<nn>"
type: "promotion"                      # or "demotion"
evidence:
  - path: "agents/evals/<agent-id>/results/<run-id>.json"
    hash: "<sha256>"
    type: "eval-result"
  - path: "agents/evals/<agent-id>/judge-reviews/<run-id>.json"
    hash: "<sha256>"
    type: "judge-review"
gate_results:
  - gate: "<gate-id>"
    result: "pass"                     # or "fail"
    detail: "<one-line description of what was checked>"
    checked_at: "<ISO8601>"
approver:
  type: "judge-agent"                  # or "human"
  id: "<approver-id>"
reason: "<one-line justification for this promotion/demotion>"
rollback_trigger: "<condition that would trigger rollback of this promotion>"
supersedes: null                       # or ref to previous promotion record if correcting
```

---

*Schema version: 1.0*
*Effective date: 2026-03-19*
*Owner: @Insightpulseai-net/platform*
*Review cadence: Quarterly or on structural change to the agent platform*
*Companion document: `spec/agent-factory/constitution.md`*
