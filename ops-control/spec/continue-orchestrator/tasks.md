# spec/continue-orchestrator/tasks.md

## Task conventions
- IDs are stable.
- Each task has: scope, owner role, deps, acceptance.

---

### T-001 Create spec folder + lint
- Scope: repo scaffolding for spec bundle
- Owner: platform
- Deps: none
- Acceptance: spec/continue-orchestrator/* exists and passes markdown lint

### T-010 Run Ledger schema + storage
- Scope: define tables/collections for runs/run_events/artifacts/approvals
- Owner: backend
- Deps: T-001
- Acceptance: can create a run, append events, attach artifacts, query by repo/org

### T-020 CLI instrumentation
- Scope: emit run lifecycle + tool calls from CLI headless/TUI
- Owner: cli
- Deps: T-010
- Acceptance: `cn ...` produces a complete ledger timeline for one run

### T-030 Mission Control: Ledger UI
- Scope: per-run timeline view + artifact download + replay CTA (disabled)
- Owner: frontend
- Deps: T-010
- Acceptance: user can open a run and inspect events, diffs, logs

### T-040 Provenance manifest + PR template
- Scope: auto-generate provenance.md + attach to PR body/files
- Owner: backend
- Deps: T-020
- Acceptance: any agent PR includes run id + hashes + test results summary

### T-050 Policy pack format v1
- Scope: YAML schema + validation + examples
- Owner: platform
- Deps: T-001
- Acceptance: policy packs validate, can be versioned per org/repo

### T-060 Policy evaluation (warn-only)
- Scope: evaluate allow/deny but do not block
- Owner: backend
- Deps: T-050, T-020
- Acceptance: ledger records "policy_warnings" with actionable detail

### T-070 Policy enforcement (block)
- Scope: hard stop on disallowed tool calls / write actions
- Owner: backend
- Deps: T-060
- Acceptance: forbidden PR creation is blocked with clear error + remediation

### T-080 Approvals workflow
- Scope: require admin approval for sensitive actions
- Owner: product/backend
- Deps: T-070
- Acceptance: run pauses pending approval; resumes after approval logged

### T-090 Budgets
- Scope: enforce token/time/tool-call budgets
- Owner: backend
- Deps: T-020
- Acceptance: runs stop on budget with consistent "budget_exceeded" event

### T-100 Deterministic record/replay adapters
- Scope: implement record/replay for GitHub read ops + local file ops
- Owner: runtime
- Deps: T-020, T-010
- Acceptance: replay run produces identical diff artifacts for supported tasks

### T-110 Metrics extensions
- Scope: add policy denials, budget stops, replay success to Metrics
- Owner: frontend/backend
- Deps: T-090, T-070, T-100
- Acceptance: Metrics page shows new counters & trends

### T-120 Pulser SDK adapter
- Scope: pulser-continue-adapter + example workflow
- Owner: platform
- Deps: T-020, T-010
- Acceptance: Pulser can trigger a Continue run, read ledger, download artifacts
