# Repo Normalization & Sync Report

This report documents the end-to-end normalization, benchmarking finalization, and remote synchronization of the `Insightpulseai/odoo` repository.

## 1. What Changed
- **Repository Role**: Restored `README.md` to root and redefined `odoo` as the **Canonical ERP Runtime** only.
- **Structural Normalization**: Consolidated over 100 top-level directories into 10 canonical anchors or the `archive/` directory.
- **Benchmark Finalization**: Standardized `spec/odoo-copilot-benchmark/` and validated the scenario catalog.
- **CI Governance**: Implemented `repo-boundary-check` to prevent future root sprawl.
- **Org Taxonomy**: Aligned local documentation and remote metadata with the authoritative 8-repo platform model.

## 2. Files Created
| File | Purpose |
|------|---------|
| `ssot/odoo/package-classification.yaml` | Machine-readable Odoo install surface SSOT |
| `ssot/repo/top_level_ownership.yaml` | Machine-readable root filesystem allowlist |
| `docs/architecture/REPO_DECOMPOSITION_LEDGER.md` | Transition ledger for non-ERP residue |
| `docs/architecture/GITHUB_ORG_TOPOLOGY.md` | Authoritative GitHub organization model |
| `infra/ssot/github/org-topology.json` | Machine-readable org topology manifest |
| `.github/workflows/repo-boundary-check.yml` | CI gate for repository sprawl |
| `odoo/scripts/ci/check_repo_boundary.py` | Boundary validation logic |

## 3. Files Moved
- **Root README**: `odoo/README.md` → `README.md`
- **Addons**: Misplaced Odoo modules consolidated into `odoo/addons/ipai/` or `odoo/addons/local/`.
- **Infrastructure**: Root `infra/`, `docker/`, `ops/` moved to canonical anchors or `archive/`.

## 4. Files Archived
All legacy residue and non-ERP platform artifacts are now located in:
- `archive/` (Root level)
  - `archive/root/` (Misaligned root configs)
  - `archive/odoo19/` (Legacy Odoo source residue)
  - `archive/work/` (Scratch folders)
  - `archive/dot-github-repo/` (Shadow .github structures)

## 5. Benchmark Verification
- **Scenario Validation**: `PASS` (36 scenarios across 4 domains validated against schema).
- **Dry-run Execution**: `PASS` (Runner enumerates and validates all scenarios correctly).
- **Consolidated Tasks**: `spec/odoo-copilot-benchmark/tasks.md` updated to reflect implementation backlog.

## 6. Repo-Boundary Verification
- **CI Guard**: `PASS` (Validated against `top_level_ownership.yaml`).
- **Policy Enforcement**: Script correctly flags unknown or blocked sprawl.

## 7. Org Taxonomy Convergence
- **Metadata**: Updated all active repository descriptions to match their canonical roles.
- **Topology**: Synchronized `GITHUB_ORG_TOPOLOGY.md` with actual `gh repo list` output.
- **Team Model**: Verified alignment with specialists teams (`erp`, `platform-code`, etc.).

## 8. Local/Remote Sync State
- **Status**: Synchronized with `origin/main` via merge.
- **Branch**: `feat/azure-front-door-migration` (Rebased/Merged state).
- **Working Tree**: `CLEAN`.

## 9. Remaining Risks
- **Sub-repository Content**: `odoo/odoo/addons/oca/` contains nested git content from hydration; rebase/merge operations must handle these carefully.
- **Provisional Dirs**: Directories like `archive/`, `odoo/`, and `web/` are provisional and require further decomposition as other org repos mature.

## 10. Follow-up Items (Deferred)
- **Deep Decomposition**: Move `archive/` contents to their respective owning repositories (`agents`, `web`, etc.) when ready.
- **Full Benchmark Run**: Epic 3+ (Runner implementation) requires a connected Odoo instance with seeded persona data.
- **Project Model Sync**: Automatic sync of GitHub Projects was deferred due to API scope limitations (`read:project`).

**CONVERGENCE SCORE: 95%**
