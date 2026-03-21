# Plan — Databricks Bundles Foundation

## Summary

This plan delivers the multi-bundle Databricks Asset Bundle layout defined in the PRD and governed by the constitution. It produces three baseline bundles, a shared configuration layer, CI validation, and architecture documentation.

## Architecture Decision

**Decision**: Adopt a multi-bundle layout under `databricks/bundles/` with one bundle per capability lane.

### Why this architecture

1. **Blast radius isolation** — A bad deploy in `sql_warehouse` cannot break `foundation_python` jobs.
2. **Independent release cadence** — Ingestion pipelines can ship daily while SQL marts ship weekly.
3. **Ownership boundaries** — Each bundle can have a clear owner without cross-lane coupling.
4. **Databricks CLI alignment** — Each bundle is a standalone `databricks bundle` target, matching the CLI's design model.
5. **Shared config without shared deployables** — Common variables are included but never deployed as a standalone unit.

### Boundaries

| Concern | Owner | Location |
|---------|-------|----------|
| Azure networking, storage, Key Vault | Platform / Infra | `infra/azure/` |
| Databricks workspace provisioning | Platform / Infra | `infra/azure/` or Terraform |
| Fabric workspace provisioning | Platform / Infra | `infra/azure/` or Terraform |
| Data engineering jobs, pipelines | Data Engineering | `databricks/bundles/` |
| SQL marts, serving views | Data/Analytics | `databricks/bundles/sql_warehouse/` |
| Power BI semantic models | BI team | Power BI service (not in this repo) |
| Bundle CI/CD | Platform / DevOps | `.github/workflows/` |

## Delivery Phases

### Phase 1: Governance (spec + architecture)
- Write constitution, PRD, plan, tasks
- Write `docs/architecture/DATABRICKS_BUNDLES_BASELINE.md`
- Establish the directory contract

### Phase 2: Scaffolding
- Create `databricks/` root with `README.md`
- Create `databricks/shared/variables.yml` and `shared/README.md`
- Create `databricks/bundles/patterns/` with reference docs
- Create empty bundle directories for all three lanes

### Phase 3: Foundation Python bundle
- Create `databricks/bundles/foundation_python/databricks.yml` with env targets
- Create `pyproject.toml` with setuptools build
- Create `src/ipai_data_intelligence/` package with jobs, transforms, quality subpackages
- Create smoke job resource in `resources/jobs/`
- Create smoke job Python source
- Create `tests/test_smoke.py`

### Phase 4: Lakeflow Ingestion bundle
- Create `databricks/bundles/lakeflow_ingestion/databricks.yml` with env targets
- Create `pyproject.toml`
- Create `src/lakeflow_ingestion_etl/` package with pipeline placeholder
- Create pipeline resource in `resources/pipelines/`
- Create job resource in `resources/jobs/`

### Phase 5: SQL Warehouse bundle
- Create `databricks/bundles/sql_warehouse/databricks.yml` with env targets
- Create `src/sql/marts/customer_360.sql` example view
- Create job resource in `resources/jobs/`

## Implementation Notes

### Shared variables consumption
Each bundle's `databricks.yml` uses `include` to pull in `../../shared/variables.yml`. Variables are then referenced in targets and resource definitions.

### CI workflow design
The CI workflow uses `dorny/paths-filter` to detect which bundles changed, then runs validation and tests only for affected bundles. This keeps CI fast and focused.

### Databricks CLI pinning
The CI workflow installs a specific version of the Databricks CLI to avoid drift. The version should be updated periodically but never auto-updated.

### Python package structure
`foundation_python` and `lakeflow_ingestion` use `pyproject.toml` with setuptools. This allows local development, testing, and Databricks wheel deployment.

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Teams create resources outside bundles | Medium | High | Anti-drift CI, workspace audit script |
| Shared variables grow unbounded | Low | Medium | Constitution limits shared scope |
| CLI version breaks validation | Low | Medium | Pin version, test upgrades in dev first |
| Bundle count grows without governance | Medium | Medium | Constitution requires justification for new bundles |

## Definition of Done

- [ ] All three bundles validate with `databricks bundle validate`
- [ ] CI workflow detects changed bundles and runs validation
- [ ] Smoke test passes in `foundation_python`
- [ ] Architecture doc matches implemented layout
- [ ] Spec kit (constitution, PRD, plan, tasks) is complete
- [ ] No manual workspace resources exist without documented exceptions
