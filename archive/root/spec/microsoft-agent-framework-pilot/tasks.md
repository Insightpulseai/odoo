# Microsoft Agent Framework Pilot Tasks

### T1 — Define orchestration adapter contract

- [ ] Create interface for `start_run`, `append_event`, `write_artifact`, `complete_run`, `fail_run`
- [ ] Define correlation/idempotency requirements
- [ ] Document boundary rules (no direct Odoo DB writes)

### T2 — Implement Supabase SSOT mapping layer

- [ ] Map workflow lifecycle states to `ops.runs`
- [ ] Map step events to `ops.run_events`
- [ ] Map outputs/log metadata to `ops.artifacts`
- [ ] Add contract tests for state transition integrity

### T3 — Implement Microsoft Agent Framework pilot runtime wrapper

- [ ] Add isolated runtime module/package for framework integration
- [ ] Implement graph/workflow for bounded pilot use case
- [ ] Add feature flag/config switch

### T4 — Integrate Odoo bridge trigger + callback

- [ ] Accept task assignment trigger through existing bridge endpoint/event path
- [ ] Validate payload schema + auth
- [ ] Write result back through approved connector path

### T5 — Add observability and evidence capture

- [ ] Correlation IDs propagated end-to-end
- [ ] Trace/log linkage stored in SSOT artifacts metadata
- [ ] Evidence bundle output documented and generated in staging run

### T6 — CI/CD gates for pilot

- [ ] Adapter contract tests in CI
- [ ] Workflow smoke test in CI (mocked dependencies)
- [ ] Secret scanning / config validation for new runtime files

### T7 — Staging validation and evaluation report

- [ ] Run staged pilot test window
- [ ] Record success/failure metrics and latency
- [ ] Document rollback test
- [ ] Publish go/no-go recommendation
