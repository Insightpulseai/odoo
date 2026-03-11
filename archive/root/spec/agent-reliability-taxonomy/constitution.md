# Constitution — Agent Reliability Taxonomy (Errors, Failure Modes, Troubleshooting, Smol Training)

## Purpose
Establish a single, enforceable reliability system for IPAI agents:
- standard error envelope + error codes taxonomy
- failure mode registry with runbook linkage
- deterministic troubleshooting + resolution documentation
- a Smol Training Playbook–style improvement loop for agent performance (ablations + preference optimization)

## Principles
1. **Truth by construction**: Every reliability claim must be enforced by CI gates and/or ops tables.
2. **Single code identity**: Every error must map to exactly one `failure_mode` code (or `UNKNOWN.*`).
3. **Deterministic resolution**: A runbook must define a finite procedure + verification checklist + prevention.
4. **Evidence-first**: Every incident/run must have a `run_id`, a timeline of events, and at least one artifact link.
5. **No silent success**: A "green" state must not hide skipped steps (use explicit `status=skipped` with reason).
6. **PR-only remediation**: Automated fixes produce PRs; no direct writes to main.
7. **Separation of layers**: Transport codes (HTTP) are not domain error codes; domain error codes are stable and versioned.
8. **Incremental adoption**: Start with top failure modes and expand; never block core shipping on "perfect taxonomy".

## Non-negotiable constraints
- All HTTP endpoints return JSON on error using a single envelope format.
- All agent failures are logged into `ops.agent_errors` (deduped by fingerprint).
- All failures are classified to a `failure_mode` code in SSOT (`ssot/errors/failure_modes.yaml`).
- Every `failure_mode` has a runbook path (`docs/runbooks/failures/<CODE>.md`).
- Every incident produces a resolution record (`docs/resolutions/YYYY/MM/<date>_<code>.md`).
- FixBot must enforce governance (`ssot/agents/fixbot_policy.yaml`) and is PR-only.
- Smol training experiments must be reproducible: fixed dataset snapshots, fixed benchmark sets, and recorded variants.

## Out of scope
- Training a model from scratch (pretraining from random init).
- Replacing vendor-wide standards (HTTP/gRPC codes).
- Building a complete observability stack (Grafana, Sentry, etc.) — we only require structured logging + artifacts in ops.
