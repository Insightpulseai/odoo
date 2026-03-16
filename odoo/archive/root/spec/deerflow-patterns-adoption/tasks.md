# Tasks — DeerFlow Patterns Adoption
## spec/deerflow-patterns-adoption · 2026-03-02

---

## Phase 1 — SSOT + Schema ✅ code-complete (not yet deployed)

- [x] Write `ssot/agents/skills.yaml` — 3 starter skills (pulser-patch, fixbot-triage, ops-advisor-scan)
- [x] Write `ssot/errors/failure_modes.yaml` — 12 initial failure codes
- [x] Write `ssot/agents/benchmark.yaml` — tier thresholds + metric weights
- [x] Write `docs/runbooks/failures/*.md` — 12 runbook files (one per code)
- [x] Write `supabase/migrations/20260302000040_deerflow_patterns.sql` — skills, memory, errors, benchmark tables + `ops.runs.skill_id` column
- [x] Write `scripts/ci/validate_skills_registry.py` — JSON-Schema validation of skills YAML
- [x] Write spec bundle (constitution, prd, plan, tasks)

## Phase 2 — GitHub Actions ⏳ code-complete (deploy on merge to main)

- [x] Write `.github/workflows/skills-sync.yml` — POST YAML → ops.skills on merge + manual trigger
- [x] Write `.github/workflows/benchmark-runner.yml` — run benchmarks for changed skills
- [x] Write `supabase/functions/ops-memory-write/index.ts`
- [x] Write `supabase/functions/ops-memory-read/index.ts`

## Phase 3 — Deploy Checklist ⏳ manual after merge

- [ ] `supabase db push` (migration 20260302000040)
- [ ] `supabase functions deploy ops-memory-write ops-memory-read`
- [ ] Trigger `skills-sync` action manually to seed `ops.skills` from YAML
- [ ] Verify `ops.skills` contains 3 rows
- [ ] Smoke test: POST to `ops-memory-write`, GET from `ops-memory-read`
- [ ] Verify `ops.runs.skill_id` column exists in schema

## Phase 4 — Agent Wiring ⏳ follow-on PRs

- [ ] Pulser: emit `skill_id` = `pulser-patch` on `ops.runs` inserts
- [ ] Pulser: implement PLAN→PATCH→VERIFY→PR state machine with `run_events`
- [ ] FixBot: emit `skill_id` = `fixbot-triage`, write `ops.agent_errors` on failure
- [ ] OpsAdvisor: emit `skill_id` = `ops-advisor-scan`, write `ops.agent_benchmark_results`
- [ ] CI gate: block skill calls for `skill_id` values not in `ops.skills`
