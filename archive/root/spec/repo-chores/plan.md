# Plan: Repo Hygiene & Drift Gates

**Spec Bundle**: `spec/repo-chores/`

---

## Phase 1: Spec Bundle + Quarantine

1. Create `spec/repo-chores/{constitution,prd,plan,tasks}.md`
2. Create `addons/_deprecated/.gitkeep`
3. Create `scripts/validate_no_deprecated_installed.sh`
4. Create `docs/governance/DEPRECATED_ADDONS.md`

## Phase 2: Drift Gates

5. Add `.github/workflows/repo-tree-drift.yml` — runs `gen_repo_tree.sh` and fails on diff
6. Confirm `scripts/gen_repo_tree.sh` is the sole generator (already true)

## Phase 3: Lint Unification

7. Add `.yamllint.yml` (repo-root, replaces inline config)
8. Add `.markdownlint-cli2.jsonc` (repo-root)
9. Create `scripts/lint_all.sh` — single entrypoint for all lint checks
10. Add `.github/workflows/lint.yml` — CI workflow for unified lint

## Phase 4: Chore Runner

11. Create `scripts/chore_repo.sh` — idempotent: regen + lint + deprecated checks
12. Add `make chore` target to Makefile

## Phase 5: Agentic Maturity Gates

13. Add `.github/workflows/agentic-maturity.yml`
14. Create `scripts/agentic/validate_agent_registry.py`
15. Create `scripts/agentic/validate_memory_contracts.py`
16. Create `agents/registry/agents.json` (machine-readable SSOT)
17. Create supporting agent scaffolding (personas, loops, policies for registered agents)

## Phase 6: Platform Memory Contract

18. Create `platform/db/contracts/memory_contract.json`
19. Create `platform/db/migrations/20260215_000001_memory_v1.sql`

## Phase 7: Ship

20. Commit all changes
21. Push to feature branch
22. Create PR

---

## Risk Mitigations

- **Lint noise**: Configs are set to relaxed/pragmatic defaults; strict mode opt-in
- **CI flakiness**: All checks are deterministic; no network calls in lint/drift gates
- **Backward compat**: No existing files modified except Makefile (additive target only)
- **RLS placeholder**: Memory schema RLS policies are clearly marked for tenant claim wiring
