# Plan: Databricks Bundles Foundation

> Implementation plan with 5 phases for establishing the multi-bundle Databricks layout.
> Governed by: `spec/databricks-bundles-foundation/constitution.md`
> Requirements: `spec/databricks-bundles-foundation/prd.md`

---

## Phase 1: Scaffold and Validate (Week 1)

**Objective**: Create the bundle directory structure, write `databricks.yml` for each bundle, and confirm all three bundles pass `databricks bundle validate`.

### Deliverables

1. `databricks/bundles/foundation_python/databricks.yml` with dev/staging/prod targets
2. `databricks/bundles/foundation_python/pyproject.toml` with hatchling build system
3. `databricks/bundles/foundation_python/src/ipai_data_intelligence/__init__.py` with version marker
4. `databricks/bundles/lakeflow_ingestion/databricks.yml` with DLT pipeline resources
5. `databricks/bundles/lakeflow_ingestion/pyproject.toml` with DLT dependencies
6. `databricks/bundles/lakeflow_ingestion/src/lakeflow_ingestion_etl/__init__.py`
7. `databricks/bundles/sql_warehouse/databricks.yml` with SQL task resources
8. `databricks/bundles/sql_warehouse/src/sql/` directory structure (schemas, marts, serving)
9. `databricks/README.md` with operating rules
10. `docs/architecture/DATABRICKS_BUNDLES_BASELINE.md` with architecture decisions

### Validation Gate

```bash
cd databricks/bundles/foundation_python && databricks bundle validate -t dev
cd databricks/bundles/lakeflow_ingestion && databricks bundle validate -t dev
cd databricks/bundles/sql_warehouse && databricks bundle validate -t dev
```

All three must exit 0.

---

## Phase 2: CI Pipeline (Week 1-2)

**Objective**: Add GitHub Actions CI that detects changed bundles and runs validation + tests.

### Deliverables

1. `.github/workflows/databricks-bundles-ci.yml` with:
   - Path-scoped trigger on `databricks/**`
   - Bundle change detection (dorny/paths-filter)
   - `databricks bundle validate` for changed bundles
   - `pytest` for Python bundles
   - Doc/spec alignment check (placeholder)
2. Databricks CLI installation step (official `databricks/setup-cli` action)
3. Python environment setup with bundle-specific `pyproject.toml`

### Validation Gate

- CI workflow passes on a PR that touches `databricks/bundles/foundation_python/`
- CI workflow skips bundles not touched by the PR

---

## Phase 3: Foundation Python Package (Week 2-3)

**Objective**: Implement the core `ipai_data_intelligence` Python package with medallion transform utilities and data quality checks.

### Deliverables

1. `src/ipai_data_intelligence/transforms/` - Base classes for Bronze/Silver/Gold transforms
2. `src/ipai_data_intelligence/quality/` - Data quality check framework (null checks, schema validation, freshness)
3. `src/ipai_data_intelligence/utils/` - Shared utilities (catalog helpers, config loaders, logging)
4. `tests/test_transforms.py` - Unit tests for transform base classes
5. `tests/test_quality.py` - Unit tests for quality checks
6. `fixtures/` - Sample DataFrames for testing
7. `resources/jobs/daily_medallion_refresh.yml` - Job definition for daily pipeline run
8. Wheel artifact configuration in `databricks.yml`

### Validation Gate

```bash
cd databricks/bundles/foundation_python
pip install -e ".[dev]"
pytest --cov=src/ipai_data_intelligence --cov-report=term-missing
# Coverage >= 60%
```

---

## Phase 4: Ingestion and SQL Bundles (Week 3-4)

**Objective**: Implement LakeFlow ingestion pipelines and SQL warehouse marts.

### Deliverables (lakeflow_ingestion)

1. `src/lakeflow_ingestion_etl/extractors/` - JDBC extractor for Odoo PostgreSQL
2. `src/lakeflow_ingestion_etl/loaders/` - Bronze table writers with append semantics
3. `src/lakeflow_ingestion_etl/schema_registry/` - Schema evolution tracking
4. `resources/pipelines/odoo_bronze_ingest.yml` - DLT pipeline for Odoo extraction
5. `resources/jobs/daily_bronze_ingest.yml` - Scheduled job wrapping the DLT pipeline

### Deliverables (sql_warehouse)

1. `src/sql/schemas/create_schemas.sql` - DDL for bronze/silver/gold/platinum schemas
2. `src/sql/marts/finance_kpis.sql` - Gold-layer finance KPI aggregations
3. `src/sql/marts/project_status.sql` - Gold-layer project status rollups
4. `src/sql/serving/pbi_finance_summary.sql` - Platinum serving view for Power BI
5. `resources/jobs/daily_mart_refresh.yml` - SQL task job for mart refresh
6. `resources/dashboards/` - Lakeview dashboard definitions (if applicable)

### Validation Gate

```bash
databricks bundle validate -t dev  # Both bundles
pytest  # lakeflow_ingestion tests
```

---

## Phase 5: Migration and Deprecation (Week 4-5)

**Objective**: Migrate remaining resources from `infra/databricks/` to the bundle layout and mark the legacy path as deprecated.

### Deliverables

1. Resource-by-resource migration inventory (spreadsheet or YAML)
2. Each migrated resource validated in dev target before legacy removal
3. `infra/databricks/DEPRECATED.md` with pointer to `databricks/bundles/`
4. CI guard preventing new files in `infra/databricks/` (optional workflow)
5. Updated `CLAUDE.md` and SSOT docs reflecting canonical path change
6. Architecture doc updated with migration evidence

### Validation Gate

- All resources in `databricks/bundles/` deploy successfully to dev
- No orphaned resources in workspace (compare `databricks bundle validate` output vs workspace list)
- `infra/databricks/` contains only `DEPRECATED.md` and historical files

---

## Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Legacy notebooks have undocumented dependencies | High | Medium | Inventory all imports before migration |
| DLT pipeline schema changes break downstream | Medium | High | Schema evolution tracking in lakeflow_ingestion |
| CI runners lack Databricks CLI | Low | High | Use official `databricks/setup-cli` action |
| Service principal permissions insufficient | Medium | Medium | Pre-validate with `databricks bundle validate -t prod` |
| Bundle examples upstream change schema | Low | Low | Pin CLI version, document deviations |

---

## Timeline Summary

| Phase | Duration | Dependency | Output |
|-------|----------|------------|--------|
| 1 - Scaffold | 1 week | None | Bundle directories, YAML, architecture doc |
| 2 - CI Pipeline | 1 week | Phase 1 | GitHub Actions workflow |
| 3 - Foundation Python | 1-2 weeks | Phase 2 | Python package, tests, wheel |
| 4 - Ingestion + SQL | 1-2 weeks | Phase 3 | DLT pipelines, SQL marts |
| 5 - Migration | 1 week | Phase 4 | Legacy deprecated, bundles canonical |

Total estimated: 5-7 weeks (overlapping phases possible after Phase 2).

---

*Spec bundle: `spec/databricks-bundles-foundation/`*
*Last updated: 2026-03-22*
