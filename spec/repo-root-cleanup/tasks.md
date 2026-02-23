# Tasks: Root Boundary Cleanup

**Spec Bundle**: `spec/repo-root-cleanup/`

---

## Phase 1: Inventory

- [ ] T1: Build `ssot/root_boundary_inventory.yaml`
  - **What**: Enumerate all root-level directories, classify each as `canonical | duplicate | misplaced | stale | unknown`
  - **Acceptance**: Every directory at repo root has an entry. No `unknown` entries remain after review.
  - **Assigned**: @inventory-builder

- [ ] T2: Build `ssot/root_cleanup_move_map.yaml`
  - **What**: For every `duplicate`, `misplaced`, or `stale` directory, define: source, destination (or `archive/`), rationale, rollback command, approved flag
  - **Acceptance**: All non-canonical directories have a move map entry. All entries start with `approved: false`.
  - **Assigned**: @inventory-builder

- [ ] T3: Create `spec/repo-root-cleanup/` bundle
  - **What**: Write constitution.md, prd.md, plan.md, tasks.md following repo spec-kit conventions
  - **Acceptance**: All 4 files present and internally consistent. References SSOT files from T1/T2.
  - **Assigned**: @speckit-writer

## Phase 2: Reference Audit

- [ ] T4: Path reference audit for candidate-move directories
  - **What**: For each directory in the move map, search `.github/workflows/`, `scripts/`, `CLAUDE.md`, `Makefile`, `package.json`, `pyproject.toml`, `Dockerfile*`, `docker-compose*`, `vercel.json`, and `tsconfig*` for references to the source path
  - **Acceptance**: Audit report listing every file that references each candidate-move directory. No unaudited moves proceed to Phase 2.
  - **Assigned**: @path-ref-auditor

## Phase 3: Execute Moves

- [ ] T5: Execute Phase 2 approved moves
  - **What**: For each `approved: true` entry in the move map, update all references and `git mv` atomically
  - **Acceptance**: All approved moves complete. `git grep` confirms zero remaining references to source paths. CI passes.
  - **Assigned**: @move-implementer

- [ ] T6: Archive Phase 3 stale directories
  - **What**: Move all `stale`-classified directories to `archive/root-cleanup-YYYYMMDD/` preserving original relative path
  - **Acceptance**: All stale directories archived. No stale directories remain at root. CI passes.
  - **Assigned**: @move-implementer

## Phase 4: Guardrails

- [ ] T7: Add root-boundary drift guard
  - **What**: Create `scripts/ci/check_root_boundary_drift.py` and `.github/workflows/root-boundary-drift.yml`
  - **Acceptance**: Script reads inventory YAML as allowlist, exits non-zero on unlisted root dirs. Workflow triggers on PR and push to main.
  - **Assigned**: @policy-guard-writer

- [ ] T8: Update `ssot/root_boundary_inventory.yaml` to post-cleanup state
  - **What**: Reflect all moves and archives in the inventory. Remove entries for archived dirs or mark as `status: archived`.
  - **Acceptance**: Inventory matches `ls -1d */` at repo root. Drift check passes.
  - **Assigned**: @inventory-builder

## Phase 5: Verification

- [ ] T9: Verify no broken CI references post-move
  - **What**: Run `git grep` for all source paths from the move map. Verify all CI workflows parse successfully. Run `scripts/ci_local.sh` or equivalent.
  - **Acceptance**: Zero references to moved source paths. CI green.
  - **Assigned**: @path-ref-auditor

- [ ] T10: Final gate — run `check_root_boundary_drift.py` and confirm PASS
  - **What**: Execute the drift guard script and verify exit code 0
  - **Acceptance**: Script exits 0. Inventory and root directory listing are in sync. Sprint complete.
  - **Assigned**: Team lead
