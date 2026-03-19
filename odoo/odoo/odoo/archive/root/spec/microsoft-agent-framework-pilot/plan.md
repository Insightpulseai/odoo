# Implementation Plan: Microsoft Agent Framework Pilot

### Phase 1: Adapter Boundary + SSOT Mapping

- Define runtime adapter interface for orchestration execution.
- Map framework run lifecycle to Supabase ops tables (runs, run_events, artifacts).
- Add feature flag / config toggle for pilot enablement.

### Phase 2: Pilot Workflow Build

- Implement one bounded workflow graph (task assignment notification pipeline).
- Integrate Odoo trigger ingress via existing connector/bridge path.
- Implement idempotency key strategy and retry behavior.

### Phase 3: Observability + Evidence

- Enable tracing/telemetry and correlation IDs.
- Persist execution evidence to standard evidence paths.
- Add CI validation for adapter contract and workflow smoke tests.

### Phase 4: Evaluation + Decision

- Compare reliability, latency, debuggability, and operational burden against current runtime.
- Document failure modes, rollback behavior, and migration feasibility.
- Produce go/no-go recommendation and next-step roadmap.

### Risks

- Framework maturity / API churn
- Integration complexity with existing Supabase run model
- Duplicate orchestration semantics with existing agents
- Hidden operational overhead (telemetry, hosting, runtime packaging)

### Mitigations

- Pilot-only scope
- Adapter isolation and feature flagging
- Contract tests for SSOT writes
- Explicit rollback path to current orchestration runtime
