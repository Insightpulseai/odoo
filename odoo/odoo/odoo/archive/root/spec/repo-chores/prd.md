# PRD: Repo Hygiene & Drift Gates

**Status**: Active
**Owner**: Platform team
**Spec Bundle**: `spec/repo-chores/`

---

## Goals

1. **Deterministic repo state**: Any generated artifact (spec.md tree, lint output) is reproducible and CI-verified.
2. **Zero-drift docs**: CI fails if generated docs diverge from committed state.
3. **CI-enforced hygiene**: Formatting, linting, and structural checks are gated in CI — not optional local steps.
4. **Deprecated addon quarantine**: Modules in `addons/_deprecated/` are blocked from install sets and bundle references.
5. **Single chore entrypoint**: `scripts/chore_repo.sh` runs all regen + lint + validation in one idempotent pass.

## Non-Goals

- No functional business logic changes
- No database migrations
- No Odoo module behavior changes
- No runtime dependency additions

---

## Scope

### 1. Repo Tree / Spec Drift Gate
- `scripts/gen_repo_tree.sh` is the sole generator for the tree section in `spec.md`
- CI workflow runs generator and fails on `git diff --exit-code spec.md`

### 2. Deprecated Addons Quarantine
- `addons/_deprecated/` directory with `.gitkeep`
- `scripts/validate_no_deprecated_installed.sh` blocks references to deprecated modules in install sets, CI configs, and bundle files
- CI integration to fail PRs that reference deprecated addons

### 3. Unified Lint/Format (Python + YAML + Markdown)
- Python: existing `.flake8`, `pyproject.toml` (ruff), `.pre-commit-config.yaml` (black/isort)
- YAML: `.yamllint.yml` (repo-root config, replaces inline `-d relaxed` in pre-commit)
- Markdown: `.markdownlint-cli2.jsonc` (repo-root config)
- `scripts/lint_all.sh` as single lint entrypoint

### 4. Deterministic Docs Regen
- Repo tree regeneration is checked for drift in CI
- Future: sitemap/data-model regen hooks (out of scope for v1)

### 5. Chore Runner
- `scripts/chore_repo.sh`: idempotent, runs regen + lint + deprecated checks
- Optional `make chore` target

---

## Success Criteria

- [ ] `scripts/chore_repo.sh` runs idempotently (no drift after second run)
- [ ] CI fails on spec.md tree drift
- [ ] CI fails if deprecated addons are referenced in install sets
- [ ] `scripts/lint_all.sh` passes locally and in CI
- [ ] No business logic changes in the diff

---

## Agentic Architecture Augmentation

This chore package also includes first-class agentic infrastructure:

### 6. Agent Maturity CI Gate
- `.github/workflows/agentic-maturity.yml` validates agent registry completeness
- Every registered agent must have: persona, loop, policies, memory contract (no prompt-only agents)
- `scripts/agentic/validate_agent_registry.py` enforces required fields and file refs
- `scripts/agentic/validate_memory_contracts.py` validates memory schema compatibility

### 7. Agent Registry (JSON SSOT)
- `agents/registry/agents.json` as machine-readable registry alongside existing `agents.yaml`
- Required fields: id, name, owner, status, persona_ref, loop_ref, policies_ref, memory_contract, skills

### 8. Platform Memory Contract
- `platform/db/contracts/memory_contract.json` defines supported memory schema versions
- `platform/db/migrations/20260215_000001_memory_v1.sql` creates `memory.*` schema (pgvector)
- Tables: `memory.items`, `memory.sessions`, `memory.semantic_cache`
- Function: `memory.search_items()` for vector retrieval
- RLS enabled with placeholder policies for tenant isolation
