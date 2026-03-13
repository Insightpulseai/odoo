# Tasks — Agent Reliability Taxonomy (Errors, Failure Modes, Troubleshooting, Smol Training)

## Phase 1 — SSOT: error codes + failure modes (P0)
1. Create `ssot/errors/error_codes.md` (human-readable naming rules + examples).
2. Create `ssot/errors/failure_modes.yaml` with initial top 12 failure modes.
3. Add CI validator `scripts/ci/check_failure_modes_ssot.py`:
   - validates schema
   - validates `runbook` paths exist
   - validates code naming convention (A-Z + dots + underscores)
4. Add `docs/runbooks/_template.md` and `docs/resolutions/_template.md`.

## Phase 2 — Runbooks: top 12 failure modes (P0)
5. Create runbooks for top 12 codes under `docs/runbooks/failures/`:
   - CI.CACHE_PATH_MISSING
   - CI.CONFIG_TRIGGER_STALE
   - MIGRATION.VALIDATION_FAILED
   - MIGRATION.APPLY_FAILED
   - FUNCTION.DEPLOY_FAILED
   - ENV.KEY_MISSING
   - VAULT.KEY_MISSING
   - WEBHOOK.SIGNATURE_INVALID
   - WEBHOOK.DELIVERY_DUPLICATE
   - DEPLOY.VERCEL.BUILD_FAILED
   - DNS.RECORD_MISSING
   - DNS.PLACEHOLDER_ACTIVE
6. Add `docs/runbooks/index.md` describing the troubleshooting loop.

## Phase 3 — Ops schema: agent errors + scoring (P0)
7. Add migration: `ops.agent_errors` (fingerprint dedupe, `count` increment helper) + indexes.
8. Add migration: `ops.agent_benchmark_results`.
9. Add PL/pgSQL helper: `ops.upsert_agent_error(...)` increments `count` on duplicate fingerprint.

## Phase 4 — Integration: capture errors from key surfaces (P0)
10. Wrap Supabase Edge Functions with standardized error envelope + logging to `ops.agent_errors`.
11. Update Odoo connector (`ipai_pulser_connector`) to:
    - write failure envelope to intent result
    - upsert `ops.agent_errors` with `source=odoo`
12. Add CI job step to ingest GitHub Actions failures and upsert into `ops.agent_errors`.

## Phase 5 — Resolution documentation flow (P0)
13. Add "resolution required" guidance to PR template or runbook policy.
14. Add CI check: if PR fixes a failure mode, require a resolution record path reference in PR body.

## Phase 6 — Benchmark suite (P1)
15. Create `ssot/agents/benchmark.yaml`:
    - categories + weights
    - tier thresholds (baseline/established/optimized)
16. Implement scorer job that writes `ops.agent_benchmark_results` per run/PR:
    - evidence format compliance
    - diff minimality + risky-path touch score
    - CI pass/fail + time-to-green

## Phase 7 — Smol Training Playbook adoption for agent improvement (P1)
17. Create `docs/agents/smol_playbook_adoption.md`:
    - compass, ablations, dataset mixtures, preference optimization mapping to ops.
18. Implement ablation harness:
    - `variant_id` stored in `ops.agent_runs.metadata`
    - A/B scoring comparisons in `ops.agent_benchmark_results`
19. Create dataset export job:
    - exports (prompt/context/patch/outcome) to storage for training
20. (Optional) Preference optimization training pipeline skeleton:
    - consumes exported dataset
    - produces a ranker or policy artifact
    - re-integrates into FixBot dispatch decisioning

## Phase 8 — UI surfaces (P1)
21. Add Ops Console page: Observability → Agent Errors.
22. Add Ops Console page: Agents → Benchmark.
23. Add Ops Console page: Runbooks (links to docs) + "create resolution record" helper.

## Phase 9 — Quality gates (P1)
24. Add CI guard: forbid `lifecycle=active` DNS entries containing placeholders (`<...>`). ✅ Done (PR #449)
25. Add CI guard: enforce PR evidence block format `[CONTEXT] [CHANGES] [EVIDENCE] [DIFF SUMMARY]`.

## Done criteria
- Top 12 failure modes exist + runbooks exist + SSOT validator passes.
- A failure is logged and classified and appears in Ops Console.
- A benchmark score is produced for at least 3 recent PRs.
- At least one ablation variant comparison is recorded.

## Status tracking
| Task | Status | PR |
|------|--------|-----|
| DNS placeholder guard (task 24) | ✅ shipped | #449 |
| Failure modes SSOT v1 (task 2) | 🔄 in progress | agent aa82fe7 |
| Runbooks top 7 (task 5 partial) | 🔄 in progress | agent aa82fe7 |
| Secrets registry + scanner (related) | 🔄 in progress | agent a5b8470 |
