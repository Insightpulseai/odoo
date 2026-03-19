# Constitution — Ops Control Room (Parallel Runbook Executor)

## 0. Purpose
Build a production-grade, parallel execution control room (Claude Code Web / Codex Web–style) for runbooks, agentic tasks, and deployment automation — backed by Supabase (Postgres + Realtime + Edge Functions) with workers deployable to DigitalOcean/K8s and UI deployable to Vercel.

## 1. Core Principles (Non-negotiables)
1) **Determinism + Proofs**: Every run must produce auditable evidence (events + artifacts).  
2) **Concurrency Safety**: No run may be executed twice; use atomic claiming with `FOR UPDATE SKIP LOCKED`.  
3) **Operational Recoverability**: Heartbeats + stuck-run recovery + cancellation are first-class.  
4) **Explicit Interfaces**: Control plane APIs are versioned and typed; templates use strict schemas.  
5) **Deploy Anywhere**: UI on Vercel; control plane on Supabase; workers on DO/DOKS/GHA.  
6) **Spec Kit Compliance**: This project must always ship with `constitution.md`, `prd.md`, `plan.md`, `tasks.md` in `spec/<slug>/`.

## 2. Scope Boundaries
### In scope (v1)
- Sessions + lanes (A/B/C/D)
- Run templates + params schema
- Atomic claiming + worker execution
- Heartbeats, stuck recovery, retries
- Cancellation
- Realtime UI (runboard)
- Artifacts (files/markdown/json/links)
- Spec Kit generation/validation as a run type

### Out of scope (v1)
- Browser-based full IDE
- Billing/subscriptions
- Secret management UI (use platform secrets)

## 3. Security + Keys Policy
- UI uses `SUPABASE_ANON_KEY` only.
- Workers and Edge Functions may use `service_role` keys **server-side only**.
- Never store secrets in git; use Vercel env, Supabase secrets, DO secrets.

## 4. Data Contract Invariants
- Canonical run lifecycle: `queued → claimed → running → {succeeded|failed|cancelled|timed_out}`
- `claimed_by`, `claimed_at`, `heartbeat_at` are mandatory for claimed/running states.
- Stuck policy is explicit and automated.

## 5. Schema Strategy (Decision)
**Adopt public schema strategy (implemented).**
- All tables reside in `public` schema for PostgREST compatibility.
- Client queries use: `supabase.from('<table>')`.
- Simpler than ops schema exposure; works out of the box.

Rationale: reduces complexity; no custom schema exposure config needed; PostgREST defaults work.

## 6. Deployment Tenets
- **Supabase**: migrations in `supabase/migrations`; executor in `supabase/functions/ops-executor`.
- **Vercel**: UI deploy; no server secrets.
- **DigitalOcean/DOKS**: stateless workers; horizontal scaling is safe by claim semantics.
- **GitHub Actions**: CI enforces Spec Kit presence and validates structure.

## 7. Compatibility / Future Targets
- System must remain compatible with:
  - Supabase Postgres + Realtime
  - Vercel edge/runtime constraints
  - DO App Platform / DOKS
  - Odoo 18/19 ops automation workflows (snapshots, upgrades, module gates) as templates

## 8. Pulser SDK Requirement
Docs must include a section instructing how to install the Pulser SDK (adapter layer), even if the runtime wiring is added later.
