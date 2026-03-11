# Plan — Agent Reliability Taxonomy (Errors, Failure Modes, Troubleshooting, Smol Training)

## Architecture

### Layer 1 — Error representation (HTTP)
Use a Problem Details–style JSON error envelope at all HTTP boundaries:

```json
{
  "type": "urn:ipai:failure:ENV.KEY_MISSING",
  "title": "Required environment variable missing",
  "status": 503,
  "detail": "PLANE_WEBHOOK_SECRET is not set in this environment",
  "instance": "/api/webhooks/plane",
  "ipai": {
    "code": "ENV.KEY_MISSING",
    "retryable": false,
    "where": "vercel:odooops-console",
    "correlation_id": "...",
    "run_id": "..."
  }
}
```

This becomes the single parsing contract for:
- Supabase Edge Functions
- webhook receivers
- internal APIs (ops-console API routes)

### Layer 2 — Failure mode taxonomy (SSOT)
SSOT file: `ssot/errors/failure_modes.yaml`

Fields per entry:
- `code`, `category`, `severity`, `retryable`
- `detect.sources`: `supabase_fn|github_actions|vercel|odoo|dns|terraform|agent_runner`
- `detect.patterns`: list of substring/regex
- `runbook`: path to `docs/runbooks/failures/<CODE>.md`
- `remediate.kind`: `checklist|fixbot|guardrail`
- `escalate.after_count` + destination

### Layer 3 — Logging & evidence (ops schema)

#### New tables
- `ops.agent_errors` — deduped by `fingerprint`, increment `count` on repeats
- `ops.agent_benchmark_results` — score + breakdown per run/variant

#### Error fingerprint
`fingerprint = sha256(source + phase + code + message + top_frame)`

This permits dedupe while allowing distinct errors to be tracked separately.
Repeated occurrences increment `count`; first seen is preserved as `first_seen_at`.

#### Existing tables used
- `ops.maintenance_runs` + `ops.maintenance_run_events` — scanner run records
- `ops.convergence_findings` — emitted for blocking/critical issues
- `ops.agent_runs` — FixBot dispatch records

### Layer 4 — Runbooks + resolution docs
```
docs/runbooks/failures/<CODE>.md      # how to fix
docs/runbooks/index.md                # troubleshooting loop entry point
docs/resolutions/YYYY/MM/<date>_<CODE>_<slug>.md  # post-incident record
docs/runbooks/_template.md            # template for new runbooks
docs/resolutions/_template.md         # template for resolution records
```

### Layer 5 — Improvement loop (Smol Training Playbook mapping)

#### Compass & Ablations
Controlled variants stored in `ops.agent_runs.metadata.variant_id`:
- prompt templates
- retrieval context policy
- forbidden paths policy strictness
- verification strictness

A/B scoring comparisons in `ops.agent_benchmark_results`.

#### Data mixture (training data from ops)
Each ops run produces a training example:
- **input**: prompt + retrieved context pointers + tool calls
- **output**: patch diff + verification outputs + PR outcome
- **labels**: failure_mode codes + reviewer accept/reject reason

Dataset exported to object storage for:
- SFT (format/style/tool calling)
- preference optimization (rank good patches over bad)

#### Post-training (optional)
DPO/GRPO-like optimization over preference pairs derived from benchmark outcomes.
Produces a ranker or policy model artifact re-integrated into FixBot dispatch decisioning.

## Interfaces

### Failure mode classification (v1 — pattern matching)
Input: raw error message + source + phase
Output: `failure_mode.code` + confidence + matched pattern

Implementation v1: iterate SSOT patterns (substring/regex match).
Implementation v2: ML classifier trained on labeled errors from `ops.agent_errors`.

### FixBot integration
If `remediate.kind=fixbot`, dispatch:
1. create `ops.agent_runs` entry with policy reference
2. attach failure mode + evidence
3. open PR only (no direct main writes)

## Security & governance
- No secrets stored in repo; SSOT references only.
- FixBot forbidden paths enforced via `ssot/agents/fixbot_policy.yaml`.
- Runbooks must not include secret values, only names/locations.

## Risks
| Risk | Mitigation |
|------|-----------|
| Taxonomy drift | CI validators on failure_modes.yaml |
| Over-classification | Allow `UNKNOWN.*` but require triage promotion |
| Training mis-optimization | Prefer preference optimization on verified outcomes, not CoT aesthetics |
| Agent over-merge via `--admin` | Failure mode `CI.AUTOMATION.PROJECT_BOARD_FAILED` → `ci_behavior: non_blocking` |
