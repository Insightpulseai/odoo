# Databricks Bundles

> Canonical location for Databricks Asset Bundle definitions.
> Replaces the legacy monolithic layout at `infra/databricks/`.
> Spec: `spec/databricks-bundles-foundation/`
> Architecture: `docs/architecture/DATABRICKS_BUNDLES_BASELINE.md`

---

## Operating Rules

1. **Every deployable artifact belongs to a bundle.** No loose notebooks or ad-hoc jobs.
2. **Deploy via CLI only.** `databricks bundle deploy -t <target>` is the only sanctioned mechanism.
3. **Unity Catalog governs all data.** `hive_metastore` is banned for new development.
4. **Secrets never enter YAML.** Use Databricks secret scopes or environment variables.
5. **One PR per bundle change.** Cross-bundle changes in a single PR are allowed but must validate all affected bundles.
6. **Tests run in CI.** Python bundles must have pytest coverage; SQL bundles must pass validation.

---

## Bundle Inventory

| Bundle | Pattern | Purpose | Deploy Targets |
|--------|---------|---------|----------------|
| `foundation_python` | `default_python` | Core Python library, medallion transforms, data quality | dev, staging, prod |
| `lakeflow_ingestion` | `lakeflow_pipelines_python` | LakeFlow/DLT ingestion pipelines (Bronze) | dev, staging, prod |
| `sql_warehouse` | `default_sql` | SQL transforms, marts (Gold), serving views (Platinum) | dev, staging, prod |

The `patterns/` directory contains reference documentation only and is not deployable.

---

## Environment Model

| Target | Catalog | Mode | Identity |
|--------|---------|------|----------|
| `dev` | `dev_ppm` | development | Current user |
| `staging` | `staging_ppm` | development | Current user |
| `prod` | `ppm` | production | `finance-ppm-service-principal` |

---

## Quick Start

```bash
# Validate a bundle
cd databricks/bundles/foundation_python
databricks bundle validate -t dev

# Deploy to dev
databricks bundle deploy -t dev

# Run tests (Python bundles)
cd databricks/bundles/foundation_python
pip install -e ".[dev]"
pytest

# Deploy to staging (requires workspace access)
databricks bundle deploy -t staging

# Deploy to prod (requires service principal)
databricks bundle deploy -t prod
```

---

## Medallion Layer Mapping

```
Bronze                    Silver                    Gold                    Platinum
(append-only)            (merge/upsert)           (aggregate)            (serve)

lakeflow_ingestion  -->  foundation_python  -->  foundation_python  -->  sql_warehouse
  DLT pipelines          Python transforms       Python transforms      SQL views
  JDBC extractors        Dedup / SCD             KPI rollups           Power BI serving
```

---

## CI/CD

CI runs on every PR touching `databricks/**`:
- Bundle validation (`databricks bundle validate`)
- Python tests (`pytest`)
- Doc/spec alignment check

See `.github/workflows/databricks-bundles-ci.yml`.

---

## Migration from Legacy

The legacy layout at `infra/databricks/` is being migrated resource-by-resource to this bundle structure. During migration, both paths may coexist but must never deploy the same resource. See Phase 5 of the spec plan for migration details.

---

## Directory Structure

```
databricks/
  README.md                              # This file
  bundles/
    foundation_python/
      databricks.yml                     # Bundle config (dev/staging/prod)
      pyproject.toml                     # Python packaging
      src/ipai_data_intelligence/        # Python package
      tests/                             # pytest suite
      fixtures/                          # Test data
      resources/
        jobs/                            # Job definitions
        pipelines/                       # DLT pipeline definitions

    lakeflow_ingestion/
      databricks.yml                     # Bundle config
      pyproject.toml                     # Python packaging
      src/lakeflow_ingestion_etl/        # Python package
      resources/
        pipelines/                       # DLT pipeline definitions
        jobs/                            # Job definitions

    sql_warehouse/
      databricks.yml                     # Bundle config
      src/sql/
        schemas/                         # Schema DDL
        marts/                           # Gold-layer SQL
        serving/                         # Platinum serving views
      resources/
        jobs/                            # SQL task jobs
        dashboards/                      # Lakeview dashboards

    patterns/
      README.md                          # Reference patterns
      KNOWLEDGE_BASE_CROSSWALK.md        # Upstream pattern mapping
```
