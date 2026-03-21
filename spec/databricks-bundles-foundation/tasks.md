# Tasks — Databricks Bundles Foundation

## Phase 1: Governance

- [x] Write `spec/databricks-bundles-foundation/constitution.md`
- [x] Write `spec/databricks-bundles-foundation/prd.md`
- [x] Write `spec/databricks-bundles-foundation/plan.md`
- [x] Write `spec/databricks-bundles-foundation/tasks.md`
- [x] Write `docs/architecture/DATABRICKS_BUNDLES_BASELINE.md`

## Phase 2: Scaffolding

- [x] Create `databricks/README.md`
- [x] Create `databricks/shared/variables.yml`
- [x] Create `databricks/shared/README.md`
- [x] Create `databricks/bundles/patterns/README.md`
- [x] Create `databricks/bundles/patterns/KNOWLEDGE_BASE_CROSSWALK.md`
- [x] Create empty bundle directories for `foundation_python`, `lakeflow_ingestion`, `sql_warehouse`

## Phase 3: Foundation Python Bundle

- [x] Create `databricks/bundles/foundation_python/databricks.yml` with dev/staging/prod targets
- [x] Create `databricks/bundles/foundation_python/pyproject.toml`
- [x] Create `databricks/bundles/foundation_python/src/ipai_data_intelligence/__init__.py`
- [x] Create `databricks/bundles/foundation_python/src/ipai_data_intelligence/jobs/__init__.py`
- [x] Create `databricks/bundles/foundation_python/src/ipai_data_intelligence/jobs/smoke.py`
- [x] Create `databricks/bundles/foundation_python/src/ipai_data_intelligence/transforms/__init__.py`
- [x] Create `databricks/bundles/foundation_python/src/ipai_data_intelligence/quality/__init__.py`
- [x] Create `databricks/bundles/foundation_python/tests/test_smoke.py`
- [x] Create `databricks/bundles/foundation_python/resources/jobs/foundation_python.job.yml`

## Phase 4: Lakeflow Ingestion Bundle

- [x] Create `databricks/bundles/lakeflow_ingestion/databricks.yml` with dev/staging/prod targets
- [x] Create `databricks/bundles/lakeflow_ingestion/pyproject.toml`
- [x] Create `databricks/bundles/lakeflow_ingestion/src/lakeflow_ingestion_etl/__init__.py`
- [x] Create `databricks/bundles/lakeflow_ingestion/src/lakeflow_ingestion_etl/pipeline.py`
- [x] Create `databricks/bundles/lakeflow_ingestion/resources/pipelines/lakeflow_ingestion.pipeline.yml`
- [x] Create `databricks/bundles/lakeflow_ingestion/resources/jobs/lakeflow_ingestion.job.yml`

## Phase 5: SQL Warehouse Bundle

- [x] Create `databricks/bundles/sql_warehouse/databricks.yml` with dev/staging/prod targets
- [x] Create `databricks/bundles/sql_warehouse/src/sql/marts/customer_360.sql`
- [x] Create `databricks/bundles/sql_warehouse/resources/jobs/sql_warehouse.job.yml`

## Phase 6: Shared Configuration

- [x] Verify all bundles include `../../shared/variables.yml`
- [x] Verify variable references are consistent across bundles

## Phase 7: CI Pipeline

- [x] Create `.github/workflows/databricks-bundles-ci.yml`
- [ ] Verify CI detects changed bundles correctly
- [ ] Verify CI runs validation on each changed bundle
- [ ] Verify CI runs tests for Python bundles

## Phase 8: Hardening

- [ ] Run `databricks bundle validate` locally for each bundle
- [ ] Confirm no manual workspace resources exist without exceptions
- [ ] Review anti-drift rules against implemented layout
- [ ] Final spec-to-implementation alignment check
