# Constitution: Microsoft Agent Framework Pilot

## 1. Core Principle

Evaluate the Microsoft Agent Framework as an orchestration substrate without destabilizing existing Supabase (SSOT/queues) and Odoo (ERP System of Record) architectures.

### Agent Orchestration Runtime Principle

- Agent orchestration frameworks (e.g., Microsoft Agent Framework) may be adopted as execution/orchestration substrates only.
- Supabase remains the control-plane SSOT for runs, events, artifacts, queue state, and policy enforcement.
- Odoo remains the ERP system of record; any orchestration runtime interacts via approved bridges/connectors only.
- No framework adoption may bypass existing observability, audit trail, or deterministic execution evidence requirements.
- Framework pilots must be reversible and isolated behind an adapter boundary.

## 2. Non-Goals

- Replacing Supabase, Odoo, Vercel, or existing infrastructure with an agent framework.
- Immediate migration of all existing agents/workflows to a new runtime.
- Introducing framework-specific lock-in without an adapter abstraction and rollback path.

## 3. Observability First

All evaluated agent workflows MUST utilize the framework's built-in OpenTelemetry tracing. This ensures transparent, auditable evidence of agent reasoning and execution before any broader rollout is considered.
