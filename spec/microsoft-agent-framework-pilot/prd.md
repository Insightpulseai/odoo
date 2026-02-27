# Product Requirements Document: Microsoft Agent Framework Pilot

## Feature: Agent Orchestration Pilot (Microsoft Agent Framework)

### Goal

Evaluate Microsoft Agent Framework as a standardized orchestration runtime for multi-agent workflows while preserving the current Supabase-first control plane and Odoo bridge model.

### Scope (Pilot Only)

- One bounded workflow implemented end-to-end using Microsoft Agent Framework.
- Adapter layer to read/write run state/events/artifacts to Supabase control-plane tables.
- Odoo bridge integration via existing APIs/connectors (no direct schema coupling).
- Tracing/telemetry enabled for workflow execution.
- Comparative evaluation against current orchestration approach.

### In Scope

- Workflow graph definition
- Agent runtime wrapper/adapter
- Supabase run-event-artifact mapping
- Observability instrumentation
- Evaluation report + acceptance metrics

### Out of Scope

- Full migration of all 66 agents
- Replacement of existing queue/control-plane primitives
- Production cutover for mission-critical finance or compliance workflows
- Odoo module rewrites for framework-native execution

### Candidate Pilot Workflow (Recommended)

Task assignment notification pipeline:

1. Trigger on task assignment event
2. Classify task/context
3. Generate role-appropriate notification/artifact
4. Persist run/event trace
5. Post result back to target channel/system

### Functional Requirements

- FR-1: Pilot workflow must execute as an explicit graph/workflow definition.
- FR-2: Each execution must persist lifecycle events to Supabase (queued/running/completed/failed).
- FR-3: Each execution must persist artifacts (messages, summaries, payloads, logs metadata) to SSOT.
- FR-4: Workflow must support retry-safe/idempotent behavior for duplicate triggers.
- FR-5: Odoo interactions must occur only through approved bridge APIs.
- FR-6: Traces/metrics/log correlation IDs must be attached to each run.
- FR-7: Pilot can be disabled by config flag without code removal.

### Non-Functional Requirements

- NFR-1: Reversible rollout (feature-flag or route switch)
- NFR-2: Observable execution (trace/log/event evidence)
- NFR-3: Deterministic state transitions in Supabase
- NFR-4: No secrets committed to repo
- NFR-5: Framework-specific code isolated behind adapter interface

### Success Metrics

- ≥95% successful execution rate for pilot workflow in staging during test window
- Mean execution latency within agreed threshold vs current baseline
- 100% run/event/artifact persistence coverage for pilot executions
- Zero unauthorized direct writes to Odoo data outside approved interfaces
- Clear go/no-go recommendation with documented trade-offs
