# Plan — Enterprise Target State

## Execution Order

1. Phase 1: Create `ssot/governance/enterprise_okrs.yaml`
2. Phase 2 (parallel):
   - 2a: Update `ssot/github/desired-end-state.yaml` (org_layers, repo_metadata_required)
   - 2b: Update `ssot/plane/config.yaml` (project_taxonomy, work_item_hierarchy)
   - 2c: Update `ssot/databricks/workspace.yaml` (maturity_phases)
3. Phase 3: Update governance docs (ENTERPRISE_OPERATING_MODEL.md, ERP_POSITIONING.md)
4. Phase 4: Create spec bundle (this directory)
5. Phase 5: Create CI validator (`scripts/ci/validate_enterprise_okrs.py`)
6. Phase 6: Cross-reference updates (PLATFORM_REPO_TREE.md, KPI_MODEL.md, STACK_INDEX.md)

## Artifacts

| Phase | Action | File |
|-------|--------|------|
| 1 | Create | `ssot/governance/enterprise_okrs.yaml` |
| 2a | Update | `ssot/github/desired-end-state.yaml` |
| 2b | Update | `ssot/plane/config.yaml` |
| 2c | Update | `ssot/databricks/workspace.yaml` |
| 3 | Update | `docs/governance/ENTERPRISE_OPERATING_MODEL.md` |
| 3 | Update | `docs/governance/ERP_POSITIONING.md` |
| 4 | Create | `spec/enterprise-target-state/{constitution,prd,plan,tasks}.md` |
| 5 | Create | `scripts/ci/validate_enterprise_okrs.py` |
| 6 | Update | `docs/architecture/PLATFORM_REPO_TREE.md` |
| 6 | Update | `docs/governance/ENTERPRISE_KPI_MODEL.md` |
| 6 | Update | `docs/governance/ENTERPRISE_STACK_INDEX.md` |

Total: 6 new files, 7 updated files.

## Verification

1. `python3 scripts/ci/validate_enterprise_okrs.py` — PASS
2. `python3 -m py_compile scripts/ci/validate_enterprise_okrs.py` — compiles
3. All kpi_ref values resolve to IDs in `control_room_kpis.yaml`
4. `ssot/governance/enterprise_okrs.yaml` is valid YAML
5. Spec bundle passes `scripts/spec_validate.sh`
