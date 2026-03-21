# Tasks: Databricks Bundles Foundation

> Execution backlog with checkboxes. Each task maps to a phase from the plan.
> Governed by: `spec/databricks-bundles-foundation/constitution.md`

---

## Phase 1: Scaffold and Validate

- [ ] Create `databricks/bundles/` directory structure
- [ ] Write `databricks/bundles/foundation_python/databricks.yml` with dev/staging/prod targets and Unity Catalog variables
- [ ] Write `databricks/bundles/foundation_python/pyproject.toml` with hatchling, pytest, ruff, black
- [ ] Write `databricks/bundles/foundation_python/src/ipai_data_intelligence/__init__.py` with version
- [ ] Create `databricks/bundles/foundation_python/tests/.gitkeep`
- [ ] Create `databricks/bundles/foundation_python/fixtures/.gitkeep`
- [ ] Create `databricks/bundles/foundation_python/resources/jobs/.gitkeep`
- [ ] Create `databricks/bundles/foundation_python/resources/pipelines/.gitkeep`
- [ ] Write `databricks/bundles/lakeflow_ingestion/databricks.yml` with DLT pipeline stubs
- [ ] Write `databricks/bundles/lakeflow_ingestion/pyproject.toml`
- [ ] Write `databricks/bundles/lakeflow_ingestion/src/lakeflow_ingestion_etl/__init__.py`
- [ ] Create `databricks/bundles/lakeflow_ingestion/resources/pipelines/.gitkeep`
- [ ] Create `databricks/bundles/lakeflow_ingestion/resources/jobs/.gitkeep`
- [ ] Write `databricks/bundles/sql_warehouse/databricks.yml` with SQL task resources
- [ ] Create `databricks/bundles/sql_warehouse/src/sql/schemas/.gitkeep`
- [ ] Create `databricks/bundles/sql_warehouse/src/sql/marts/.gitkeep`
- [ ] Create `databricks/bundles/sql_warehouse/src/sql/serving/.gitkeep`
- [ ] Create `databricks/bundles/sql_warehouse/resources/jobs/.gitkeep`
- [ ] Create `databricks/bundles/sql_warehouse/resources/dashboards/.gitkeep`
- [ ] Write `databricks/README.md` with operating rules and bundle inventory
- [ ] Write `databricks/bundles/patterns/README.md` with reference pattern docs
- [ ] Write `databricks/bundles/patterns/KNOWLEDGE_BASE_CROSSWALK.md` mapping upstream patterns
- [ ] Write `docs/architecture/DATABRICKS_BUNDLES_BASELINE.md`
- [ ] Validate all three bundles: `databricks bundle validate -t dev`
- [ ] Update `spec/databricks-bundles-foundation/tasks.md` with Phase 1 completion evidence

---

## Phase 2: CI Pipeline

- [ ] Write `.github/workflows/databricks-bundles-ci.yml`
- [ ] Add `detect-bundles` job using `dorny/paths-filter` to identify changed bundles
- [ ] Add `validate-bundles` job running `databricks bundle validate` per changed bundle
- [ ] Add `test-python-bundles` job running `pytest` for Python bundles
- [ ] Add `enforce-doc-spec-alignment` placeholder job
- [ ] Install Databricks CLI via `databricks/setup-cli` action in CI
- [ ] Test CI on a PR touching `databricks/bundles/foundation_python/`
- [ ] Verify CI skips unchanged bundles
- [ ] Document CI pipeline in architecture doc

---

## Phase 3: Foundation Python Package

- [ ] Create `src/ipai_data_intelligence/transforms/__init__.py`
- [ ] Implement `BronzeTransform` base class (append-only, schema validation)
- [ ] Implement `SilverTransform` base class (merge/upsert, deduplication)
- [ ] Implement `GoldTransform` base class (aggregation, incremental materialization)
- [ ] Create `src/ipai_data_intelligence/quality/__init__.py`
- [ ] Implement `NullCheckRule` - validates non-null columns
- [ ] Implement `SchemaCheckRule` - validates DataFrame schema against expected
- [ ] Implement `FreshnessCheckRule` - validates data recency
- [ ] Create `src/ipai_data_intelligence/utils/__init__.py`
- [ ] Implement `catalog_helper.py` - Unity Catalog name resolution per environment
- [ ] Implement `config_loader.py` - YAML/env config reader
- [ ] Implement `logging_utils.py` - structured logging for Databricks
- [ ] Write `tests/test_transforms.py` with mock DataFrame tests
- [ ] Write `tests/test_quality.py` with quality rule tests
- [ ] Write `tests/conftest.py` with shared fixtures
- [ ] Add sample fixtures to `fixtures/`
- [ ] Configure wheel artifact in `databricks.yml`
- [ ] Write `resources/jobs/daily_medallion_refresh.yml`
- [ ] Verify pytest coverage >= 60%
- [ ] Deploy foundation_python to dev target and verify

---

## Phase 4: Ingestion and SQL Bundles

### lakeflow_ingestion

- [ ] Create `src/lakeflow_ingestion_etl/extractors/__init__.py`
- [ ] Implement `OdooJdbcExtractor` - JDBC extraction from Odoo PostgreSQL
- [ ] Implement `RestApiExtractor` - Generic REST API ingestion
- [ ] Create `src/lakeflow_ingestion_etl/loaders/__init__.py`
- [ ] Implement `BronzeTableWriter` - Append-only Delta table writer
- [ ] Create `src/lakeflow_ingestion_etl/schema_registry/__init__.py`
- [ ] Implement schema evolution tracker (column adds, type changes)
- [ ] Write `resources/pipelines/odoo_bronze_ingest.yml` - DLT pipeline definition
- [ ] Write `resources/jobs/daily_bronze_ingest.yml` - Scheduled ingestion job
- [ ] Write tests for extractors and loaders
- [ ] Deploy lakeflow_ingestion to dev target

### sql_warehouse

- [ ] Write `src/sql/schemas/create_schemas.sql` - DDL for all medallion schemas
- [ ] Write `src/sql/marts/finance_kpis.sql` - Finance KPI Gold aggregations
- [ ] Write `src/sql/marts/project_status.sql` - Project status Gold rollups
- [ ] Write `src/sql/serving/pbi_finance_summary.sql` - Power BI Platinum view
- [ ] Write `src/sql/serving/pbi_project_dashboard.sql` - Power BI project view
- [ ] Write `resources/jobs/daily_mart_refresh.yml` - SQL task job
- [ ] Deploy sql_warehouse to dev target
- [ ] Verify Power BI can connect to Platinum serving views

---

## Phase 5: Migration and Deprecation

- [ ] Inventory all resources in `infra/databricks/` (notebooks, jobs, pipelines, SQL)
- [ ] Map each resource to target bundle (foundation_python, lakeflow_ingestion, sql_warehouse)
- [ ] Migrate `infra/databricks/notebooks/bronze/` to lakeflow_ingestion
- [ ] Migrate `infra/databricks/notebooks/silver/` to foundation_python transforms
- [ ] Migrate `infra/databricks/notebooks/gold/` to foundation_python transforms
- [ ] Migrate `infra/databricks/sql/` to sql_warehouse
- [ ] Migrate `infra/databricks/dlt/` to lakeflow_ingestion pipelines
- [ ] Migrate `infra/databricks/resources/jobs/` to appropriate bundle resources
- [ ] Migrate `infra/databricks/resources/pipelines/` to appropriate bundle resources
- [ ] Validate all migrated resources in dev target
- [ ] Deploy all bundles to staging and verify
- [ ] Create `infra/databricks/DEPRECATED.md` with migration pointer
- [ ] Add CI guard preventing new files in `infra/databricks/` (optional)
- [ ] Update CLAUDE.md to reflect `databricks/bundles/` as canonical path
- [ ] Update `docs/architecture/DATABRICKS_BUNDLES_BASELINE.md` with migration evidence
- [ ] Final validation: all prod resources deployed via bundles, zero workspace drift

---

## Cross-Cutting Tasks

- [ ] Document bundle naming conventions in `databricks/README.md`
- [ ] Document environment variable requirements for CI
- [ ] Create Databricks secret scopes: `ipai-dev`, `ipai-staging`, `ipai-prod`
- [ ] Verify service principal `finance-ppm-service-principal` has required permissions
- [ ] Add `databricks/` to `.gitignore` exclusions if needed (ensure `.gitkeep` files track)
- [ ] Register spec bundle in platform contracts index

---

*Spec bundle: `spec/databricks-bundles-foundation/`*
*Last updated: 2026-03-22*
