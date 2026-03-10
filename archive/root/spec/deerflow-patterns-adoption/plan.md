# Implementation Plan — DeerFlow Patterns Adoption
## spec/deerflow-patterns-adoption · 2026-03-02

---

## Architecture Layers

```
ssot/agents/skills.yaml          ← SSOT (edit here)
    │
    ├─► scripts/ci/validate_skills_registry.py   ← CI enforcer
    ├─► .github/workflows/skills-sync.yml        ← syncs YAML → ops.skills on merge
    │
    ▼
ops.skills (Supabase)            ← live registry
    │
    ├─► ops.runs (kind='agent', skill_id FK)
    │       ├─► ops.run_events
    │       └─► ops.agent_errors  (fingerprint dedup, failure_mode code)
    │
    └─► ops.agent_benchmark_results

ops.memory_entries               ← scoped memory plane (run|project|org)
    └─► ops-memory-write / ops-memory-read Edge Functions

ssot/errors/failure_modes.yaml   ← canonical error codes
    └─► docs/runbooks/failures/<CODE>.md (12 runbooks)

ssot/agents/benchmark.yaml       ← tier thresholds + weights
```

---

## Security Model

| Surface | Auth | Notes |
|---------|------|-------|
| ops-memory-write Edge Fn | JWT (authenticated users) | Rate-limited 100 writes/min |
| ops-memory-read Edge Fn | JWT (authenticated users) | Prefix scan max 100 rows |
| skills-sync GitHub Action | SUPABASE_SERVICE_ROLE_KEY (secret) | Runs on merge to main only |
| benchmark GitHub Action | SUPABASE_SERVICE_ROLE_KEY (secret) | Runs on merge to main only |
| ops.skills RLS | service_role write; authenticated read | anon = no access |
| ops.memory_entries RLS | service_role + authenticated (own rows) | anon = no access |
| ops.agent_errors RLS | service_role write; authenticated read | anon = no access |
| ops.agent_benchmark_results | service_role write; authenticated read | anon = no access |

---

## Migration Strategy

Single migration file: `supabase/migrations/20260302000040_deerflow_patterns.sql`

Tables added (all `CREATE TABLE IF NOT EXISTS`):
- `ops.skills` + `ops.skill_versions`
- `ops.memory_entries`
- `ops.agent_errors`
- `ops.agent_benchmark_results`

Column added to existing table:
```sql
ALTER TABLE ops.runs ADD COLUMN IF NOT EXISTS skill_id TEXT REFERENCES ops.skills(id) ON DELETE SET NULL;
```

No destructive changes; existing `ops.runs` rows unaffected (`skill_id` nullable).

---

## Phase Plan

### Phase 1 — SSOT + Schema (this PR)
- [x] `ssot/agents/skills.yaml` (3 starter skills)
- [x] `ssot/errors/failure_modes.yaml` (12 codes)
- [x] `ssot/agents/benchmark.yaml`
- [x] `docs/runbooks/failures/*.md` (12 files)
- [x] `supabase/migrations/20260302000040_deerflow_patterns.sql`
- [x] `scripts/ci/validate_skills_registry.py`
- [x] Spec bundle (this file)

### Phase 2 — GitHub Actions (code-complete in this PR, deploy on merge)
- [ ] `.github/workflows/skills-sync.yml` — YAML → `ops.skills` on merge to main
- [ ] `.github/workflows/benchmark-runner.yml` — runs benchmarks for changed skills
- [ ] Edge Functions `ops-memory-write` / `ops-memory-read`

### Phase 3 — Agent Wiring (follow-on PRs)
- [ ] Pulser: emit `skill_id` on runs, use state machine `PLAN→PATCH→VERIFY→PR`
- [ ] FixBot: emit skill_id, write errors to `ops.agent_errors`
- [ ] OpsAdvisor: write benchmark results to `ops.agent_benchmark_results`

### Phase 4 — Deploy Checklist
- [ ] `supabase db push` (migration 20260302000040)
- [ ] `supabase functions deploy ops-memory-write ops-memory-read`
- [ ] Seed `ops.skills` from YAML via skills-sync action (manual trigger)
- [ ] Smoke test: insert a run with `skill_id`, query memory
