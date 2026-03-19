# WorkbenchX — Task Breakdown

## P0 — Foundations

- [ ] **Task 1**: Create `ops.*` schema for projects/sessions/experiments/models/apps/artifacts/run_events (migration)
- [ ] **Task 2**: Define SSOT for approved runtimes (container images) and compute profiles (`ssot/workbench/runtimes.yaml`)
- [ ] **Task 3**: Define SSOT for provider adapters (sandbox + inference) — `ssot/providers/vercel/sandbox.yaml`, `ssot/providers/ai/provider.yaml` ✅ **Done (this PR)**
- [ ] **Task 4**: Implement JSON-only API contract validation for all internal workbench endpoints

## P0 — Sessions

- [ ] **Task 5**: Implement session runner abstraction: create session, attach logs, enforce idle timeout
- [ ] **Task 6**: Integrate notebook UI (embedded) with authenticated session token
- [ ] **Task 7**: Store session events in `ops.run_events` and output artifacts in `ops.artifacts`

## P0 — Experiments

- [ ] **Task 8**: Implement experiment run submission (params + dataset ref + code sha + runtime)
- [ ] **Task 9**: Persist metrics + artifacts per run
- [ ] **Task 10**: Add experiment compare view to ops-console

## P0 — Model deployments

- [ ] **Task 11**: Implement model endpoint deployment (versioned, policy-protected)
- [ ] **Task 12**: Add basic metrics ingestion (latency/errors) per endpoint

## P0 — Analytical Apps

- [ ] **Task 13**: Implement app deployment type (streamlit/flask/nextjs)
- [ ] **Task 14**: Provide versioned releases + logs per app deployment

## P1 — Templates (Accelerators)

- [ ] **Task 15**: Add AMP-like project templates:
  - RAG starter
  - model serving starter
  - app starter
  - notebook starter

## P1 — AI Studios equivalents

- [ ] **Task 16**: RAG pipeline job type (ingest → chunk → embed → retrieve → answer)
- [ ] **Task 17**: Fine-tune pipeline job type (dataset → train → eval → deploy)
- [ ] **Task 18**: Multi-agent workflow job type (planner/executor/evaluator)

## P1 — Governance & audit

- [ ] **Task 19**: Implement lineage views (run → artifacts → model/app)
- [ ] **Task 20**: Add access audit surfacing (who accessed which dataset/run)
- [ ] **Task 21**: Add quotas + compute budgets per project

## P2 — Enterprise hardening

- [ ] **Task 22**: Multi-workspace org support + approval workflows for promotions (run → model, staging → prod)

---

## Streaming AI (foundation — this PR)

- [x] **Task F1**: `ops.sandbox_runs` migration (`20260301000080`) — Vercel Sandbox execution ledger
- [x] **Task F2**: `apps/ops-console/app/api/ai/stream/route.ts` — `streamText` via Vercel AI Gateway
