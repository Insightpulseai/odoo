# Constitution: Root Boundary Cleanup Sprint

**Version**: 1.0
**Effective**: 2026-02-24
**Scope**: Root-level directory boundary drift — inventory, relocate, archive, guard.

---

## Non-Negotiable Rules

1. **No mass moves.** Every directory relocation is individually approved in `ssot/root_cleanup_move_map.yaml` before execution. Bulk `mv` or `git mv` of unapproved paths is forbidden.

2. **No deletion without inventory.** Every root-level entry must appear in `ssot/root_boundary_inventory.yaml` with a classification before any action is taken. Unlisted paths are frozen until inventoried.

3. **No import path refactors without reference audit.** Before moving any directory, all CI workflows, scripts, CLAUDE.md references, Dockerfiles, and `package.json`/`pyproject.toml` paths that reference the source path must be identified and updated atomically with the move.

4. **`addons/` is the primary runtime boundary — do not touch.** This sprint does not modify, move, rename, or restructure anything under `addons/`. Odoo module paths are governed by separate specs (`spec/ee-oca-parity/`, `spec/repo-chores/`).

5. **`supabase/` is the embedded control-plane — do not touch.** Supabase migrations, functions, and config are out of scope. Governed by `spec/supabase-auth-ssot/` and related specs.

6. **Archive-first, never delete-first.** Stale or misplaced directories move to `archive/root-cleanup-YYYYMMDD/` with their original relative path preserved. Direct `rm -rf` of any root directory is forbidden.

7. **Every move must have a rollback strategy.** The move map must include the inverse operation for each relocation. If a move breaks CI, the rollback is executed immediately — no debugging under broken state.

8. **CI path references must be updated before or with the move.** A move commit that breaks a workflow file is a failed move. Reference updates and the `git mv` must be in the same commit or an atomic commit sequence.

9. **Moves are gated by `ssot/root_cleanup_move_map.yaml` approval.** The `approved: true` field in the move map is the sole authority. No agent may execute a move where `approved: false` or the entry is absent.

10. **Scope is root-level boundary drift only.** This sprint addresses directories sitting at repo root (`/`) that belong elsewhere. It does not restructure subdirectories, refactor code, change module behavior, or modify database schemas.

---

## Constraints

- No new runtime dependencies introduced
- No changes to Odoo module behavior or install sets
- No changes to Supabase schema or Edge Functions
- CI workflows must pass before and after each phase
- All operations must be executable via CLI (no UI steps)
- Python 3.12+ / Bash (consistent with repo baseline)

---

## Protected Paths (Explicitly Out of Scope)

These root directories are canonical and must not be moved, renamed, or archived:

| Path | Reason |
|------|--------|
| `addons/` | Odoo runtime boundary |
| `supabase/` | Embedded control-plane |
| `.github/` | CI/CD workflows |
| `.devcontainer/` | Dev environment |
| `docs/` | Documentation root |
| `scripts/` | Automation scripts |
| `spec/` | Spec bundles |
| `config/` | Configuration SSOT |
| `infra/` | Infrastructure-as-code |
| `web/` | Web apps and frontend |
| `packages/` | Shared packages |
| `apps/` | Application projects |
| `deploy/` | Deployment configs |
| `ssot/` | Single source of truth files |

---

## Amendment Process

Changes to this constitution require:
1. PR with rationale
2. Passing CI gates
3. Team lead approval
