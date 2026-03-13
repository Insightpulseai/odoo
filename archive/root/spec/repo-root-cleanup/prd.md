# PRD: Root Boundary Cleanup

**Status**: Active
**Owner**: Platform team
**Spec Bundle**: `spec/repo-root-cleanup/`

---

## Problem Statement

The repo root contains 100+ top-level directories. Many are misplaced (should be nested under a canonical parent), duplicated (e.g., `specs/` vs `spec/`, `catalogs/` vs `catalog/`), or stale (prototypes, scratch work, one-off experiments). This creates:

- Navigation confusion for humans and agents
- Ambiguous SSOT ownership
- CI path fragility
- Onboarding friction

## Goals

1. **Canonical root entries only**: Root contains only directories listed in `ssot/root_boundary_inventory.yaml` with `status: canonical`.
2. **Duplicate directories resolved**: Plural/singular conflicts merged (e.g., `specs/` content into `spec/`, `catalogs/` into `catalog/`).
3. **Misplaced directories relocated**: Directories that belong under a canonical parent are moved (e.g., `mcp/` to `agents/mcp/`, `n8n/` to `infra/n8n/`).
4. **Stale directories archived**: Throwaway, scratch, and prototype directories archived to `archive/root-cleanup-YYYYMMDD/`.
5. **Root-boundary drift CI guard active**: A CI workflow prevents new unregistered root directories from being introduced.
6. **Inventory reflects post-cleanup state**: `ssot/root_boundary_inventory.yaml` is updated to match the final directory structure.
7. **No broken CI references**: All workflow files, scripts, and configuration that reference moved paths are updated atomically.

## Non-Goals

- Restructuring subdirectories within canonical parents
- Modifying Odoo module behavior or install sets
- Changing Supabase schema or Edge Functions
- Refactoring Python/JS import paths within application code
- Adding new features or runtime dependencies

---

## Success Criteria

- [ ] `ssot/root_boundary_inventory.yaml` classifies every root directory
- [ ] `ssot/root_cleanup_move_map.yaml` documents all relocations with rollback
- [ ] All approved moves executed with atomic reference updates
- [ ] Stale directories archived to `archive/root-cleanup-YYYYMMDD/`
- [ ] `.github/workflows/root-boundary-drift.yml` passes on main
- [ ] `scripts/ci/check_root_boundary_drift.py` exits 0 post-cleanup
- [ ] No CI workflow failures caused by the cleanup
- [ ] Zero references to moved source paths remain in `.github/workflows/`, `scripts/`, `CLAUDE.md`, `Makefile`, `package.json`, `pyproject.toml`

---

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Broken CI from stale path references | High | Reference audit before every move; atomic commits |
| Data loss from premature deletion | High | Archive-first policy; no `rm -rf`; rollback in move map |
| Scope creep into module restructuring | Medium | Constitution hard-scopes to root boundary only |
| Agent confusion from path changes | Medium | Update CLAUDE.md and SSOT docs in same PR |
| Merge conflicts with in-flight PRs | Medium | Coordinate timing; execute during low-activity window |
