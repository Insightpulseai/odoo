# spec/continue-orchestrator/plan.md

## Architecture overview
Continue Orchestrator = 3 layers:

1) **Policy Engine**
- Input: policy packs (org/repo), run context (trigger), requested action
- Output: allow/deny + obligations (e.g., "must run tests", "require approval")

2) **Run Ledger Service**
- Append-only event store
- Artifact storage: patches, logs, test results, provenance manifests
- Replay API: re-run with recorded tool I/O

3) **Runtime Adapters**
- CLI headless/TUI integrates by emitting structured events into Ledger
- Mission Control integrates by showing ledger timelines + policies

## Data model (logical)
- organizations
- repositories
- policy_packs (versioned)
- runs
- run_events (append-only)
- artifacts (patch/logs/manifests)
- approvals (who approved what and when)
- budgets (per-run counters)

## Integration points (no breaking changes)
- Workflows:
  - On cron/webhook trigger, create run with event payload snapshot
- GitHub integration:
  - PR creation writes provenance manifest + CI status back to run
- Secrets:
  - Continue secret references remain `${{ secrets.NAME }}`
- Configs:
  - config.yaml hash stored at run start; referenced blocks pinned

## Determinism strategy
- "Record" mode:
  - Record tool request/response pairs for supported adapters (GitHub diff fetch, file reads, etc.)
- "Replay" mode:
  - Substitute recorded responses for tool calls
  - Block unsupported nondeterministic calls unless policy allows

## Policy pack format (v1)
- YAML (human-friendly), optionally compiled to OPA/Rego internally
- Key sections:
  - repositories
  - branches
  - file_globs
  - tools (MCP servers, integrations)
  - actions (open_pr, push_branch, comment, create_issue)
  - approvals (required roles)
  - budgets

## Milestones
### M1 — Ledger MVP
- CLI emits run + events
- Mission Control displays "Ledger" tab
- PR provenance manifest auto-attached

### M2 — Policy warn-only
- Evaluate policies but don't block
- UI shows warnings and "what would have been blocked"

### M3 — Policy enforce
- Block disallowed actions (PR creation, tool calls, write ops)
- Add approvals workflow

### M4 — Deterministic replay for core adapters
- GitHub read ops, local file ops, diff/patch ops
- "Replay run" button

### M5 — Budgets + SLOs
- Hard stop on budgets
- Metrics: policy denials, budget stops, replay success

## CI/CD plan
- Add a "PR Evidence Required" GitHub check:
  - fail if provenance manifest missing
  - fail if tests not reported
- Provide a reusable workflow template for agent PRs.

## Pulser SDK integration plan
- `pulser-continue-adapter`:
  - trigger run via CLI/headless
  - poll ledger status
  - fetch artifacts + attach to Pulser run records
- Example Pulser workflow:
  - "Sentry issue → Continue run → PR → Pulser verification agent → merge gate"
