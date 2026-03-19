# Plan: Root Boundary Cleanup

**Spec Bundle**: `spec/repo-root-cleanup/`

---

## Phase 1: Inventory (Read-Only)

**Goal**: Complete classification of all root directories. No file system changes.

1. Enumerate every top-level directory in the repo root
2. Classify each as: `canonical`, `duplicate`, `misplaced`, `stale`, or `unknown`
3. Write classification to `ssot/root_boundary_inventory.yaml`
4. For directories classified as `duplicate` or `misplaced`, identify the canonical target
5. Build `ssot/root_cleanup_move_map.yaml` with: source, destination, rationale, rollback command, `approved: false`
6. Run path reference audit: for each candidate-move directory, list all files that reference it

**Exit criteria**: Both SSOT YAML files committed. No directories moved.

---

## Phase 2: Safe Moves (Low-Risk Relocations)

**Goal**: Execute approved, low-risk moves with atomic reference updates.

7. Review move map; team lead sets `approved: true` on low-risk entries
8. For each approved move (in dependency order):
   a. Update all CI workflows, scripts, and docs that reference the source path
   b. Execute `git mv <source> <destination>`
   c. Commit reference updates + move atomically
   d. Run `git grep <source-basename>` to confirm zero remaining references
9. Run full CI locally or via `scripts/ci_local.sh` after each batch

**Exit criteria**: All Phase 2 approved moves complete. CI green.

---

## Phase 3: Archive (Stale Directory Quarantine)

**Goal**: Move stale/throwaway directories to archive with provenance.

10. Create `archive/root-cleanup-YYYYMMDD/` (using current date)
11. For each directory classified as `stale` in the inventory:
    a. `git mv <dir> archive/root-cleanup-YYYYMMDD/<dir>`
    b. Update any references (likely none for truly stale dirs)
    c. Commit with message: `chore(repo): archive stale root dir <dir>`
12. Update `ssot/root_boundary_inventory.yaml` to reflect archived status

**Exit criteria**: All stale directories archived. Inventory updated. CI green.

---

## Phase 4: Guardrails (CI Enforcement)

**Goal**: Prevent future root-boundary drift with automated enforcement.

13. Create `scripts/ci/check_root_boundary_drift.py`:
    - Reads `ssot/root_boundary_inventory.yaml` as allowlist
    - Compares against actual root directories
    - Exits non-zero if unlisted directory found at root
    - Ignores dotfiles/dotdirs (`.github/`, `.devcontainer/`, etc.)
14. Create `.github/workflows/root-boundary-drift.yml`:
    - Triggers on PR and push to main
    - Runs the drift check script
    - Fails PR if new unregistered root directory introduced
15. Update `ssot/root_boundary_inventory.yaml` to reflect final post-cleanup state
16. Run final gate: `python scripts/ci/check_root_boundary_drift.py` and confirm PASS

**Exit criteria**: CI guard active and passing. Inventory matches reality. Sprint complete.

---

## Risk Mitigations

- **Atomic commits**: Reference updates and moves are never in separate commits
- **Rollback-ready**: Every move map entry has an inverse command
- **Incremental execution**: Phases are sequential; each must pass CI before the next begins
- **No mass operations**: Each move is individually tracked and approved
- **Protected paths**: Constitution explicitly lists directories that must not be touched
