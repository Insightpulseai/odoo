# OdooOps Sh Constitution

**Purpose**: Odoo.sh-style control plane for self-hosted Odoo environments

**Core Principles**:
1. **Queue First**: All executions through ops.runs queue with worker claiming
2. **State Machine Fidelity**: queued → claimed → running → succeeded|failed
3. **Append-Only Logging**: ops.run_events immutable audit trail
4. **Storage Separation**: Artifacts in Supabase Storage, metadata in ops.run_artifacts
5. **Worker Idempotency**: ops.claim_next_run() uses SELECT FOR UPDATE SKIP LOCKED

**Scope**: Control plane (projects, workflows, runs, events, artifacts, tools, advisories)

**Out of Scope**: Odoo business logic, Docker orchestration

**SSOT Boundaries**:
- **Odoo Database**: Business data (res.partner, account.move)
- **Supabase ops.***: Control plane state
- **Supabase Storage**: Binary artifacts

**Integration Points**: scripts/odooops/*.sh, CI workflows, Console UI (future)
