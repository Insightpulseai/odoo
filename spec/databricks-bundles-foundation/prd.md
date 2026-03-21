# PRD: Databricks Bundles Foundation

> Product Requirements Document for the multi-bundle Databricks Asset Bundle repo layout.
> Governed by: `spec/databricks-bundles-foundation/constitution.md`

---

## 1. Problem Statement

The current Databricks infrastructure lives in `infra/databricks/` as a monolithic configuration: a single `databricks.yml`, scattered notebooks, and ad-hoc resource files. This layout has the following problems:

1. **No isolation**: All jobs, pipelines, and SQL artifacts share a single bundle definition, making it impossible to deploy or validate independently.
2. **No testability**: Python code is not packaged, so unit tests cannot run outside Databricks.
3. **No CI/CD gating**: There is no automated validation of bundle syntax or resource correctness on PRs.
4. **No medallion enforcement**: Bronze, Silver, Gold layers are directory conventions only, not enforced by catalog/schema structure.
5. **Drift risk**: Resources created in the workspace UI are not tracked in Git, creating drift between desired and actual state.

---

## 2. Goal

Establish a multi-bundle repository layout under `databricks/bundles/` that:

- Decomposes the monolith into independently deployable bundles
- Enforces Unity Catalog and medallion architecture via bundle variables
- Enables CI/CD with `databricks bundle validate` and `pytest`
- Provides a clear migration path from `infra/databricks/` to `databricks/bundles/`
- Follows upstream Databricks bundle-examples patterns (default_python, lakeflow_pipelines_python, default_sql)

---

## 3. Users and Personas

| Persona | Role | Interaction |
|---------|------|-------------|
| Data Engineer | Builds and maintains ETL pipelines | Authors Python bundles, defines DLT pipelines |
| Data Analyst | Creates SQL marts and dashboards | Authors SQL bundles, defines serving views |
| Platform Engineer | Manages CI/CD and infrastructure | Configures CI workflows, manages service principals |
| AI Agent (Copilot) | Automates data quality checks | Reads Gold/Platinum tables via SQL warehouse |
| Finance Team | Consumes Power BI reports | Reads Platinum serving views (read-only) |

---

## 4. Bundle Inventory

### 4.1 foundation_python

**Pattern**: `default_python` (from databricks/bundle-examples)

**Purpose**: Core Python library for data engineering. Contains shared utilities, medallion transform base classes, and data quality check functions. Packaged as a wheel and consumed by other bundles.

**Contents**:
- `src/ipai_data_intelligence/` - Python package (transforms, quality, utils)
- `resources/jobs/` - Orchestration jobs (e.g., daily medallion refresh)
- `resources/pipelines/` - DLT pipeline definitions that use the Python package
- `tests/` - pytest suite (runs locally and in CI)
- `fixtures/` - Test data fixtures

**Deployment targets**: dev, staging, prod (all three)

### 4.2 lakeflow_ingestion

**Pattern**: `lakeflow_pipelines_python` (from databricks/bundle-examples)

**Purpose**: LakeFlow Connect and DLT-based ingestion pipelines for Bronze layer population. Handles JDBC extraction from Odoo PostgreSQL, REST API ingestion from external sources, and file-based loading.

**Contents**:
- `src/lakeflow_ingestion_etl/` - Python package (extractors, loaders, schema registry)
- `resources/pipelines/` - DLT pipeline YAML definitions
- `resources/jobs/` - Ingestion job schedules

**Deployment targets**: dev, staging, prod

### 4.3 sql_warehouse

**Pattern**: `default_sql` (from databricks/bundle-examples)

**Purpose**: SQL-based transformations, business marts (Gold), serving views (Platinum), and dashboard definitions. This bundle targets the SQL warehouse compute, not general-purpose clusters.

**Contents**:
- `src/sql/schemas/` - Schema DDL (CREATE SCHEMA IF NOT EXISTS)
- `src/sql/marts/` - Gold-layer mart SQL (aggregations, KPIs)
- `src/sql/serving/` - Platinum-layer serving views (Power BI, API)
- `resources/jobs/` - SQL task job definitions
- `resources/dashboards/` - Lakeview dashboard definitions

**Deployment targets**: dev, staging, prod

---

## 5. Bundle Configuration Contract

Every `databricks.yml` must declare:

```yaml
variables:
  catalog:
    description: Unity Catalog name
  schema_bronze:
    description: Bronze schema name
    default: bronze
  schema_silver:
    description: Silver schema name
    default: silver
  schema_gold:
    description: Gold schema name
    default: gold

targets:
  dev:
    mode: development
    default: true
    variables:
      catalog: dev_ppm
  staging:
    mode: development
    variables:
      catalog: staging_ppm
  prod:
    mode: production
    variables:
      catalog: ppm
    run_as:
      service_principal_name: finance-ppm-service-principal
```

---

## 6. Migration Path

The migration from `infra/databricks/` to `databricks/bundles/` is incremental:

1. **Phase 1**: Create bundle scaffolding (this spec). No removal of legacy.
2. **Phase 2**: Port notebooks and jobs from `infra/databricks/notebooks/` to appropriate bundles.
3. **Phase 3**: Port DLT pipelines from `infra/databricks/dlt/` to `lakeflow_ingestion`.
4. **Phase 4**: Port SQL from `infra/databricks/sql/` to `sql_warehouse`.
5. **Phase 5**: Deprecate `infra/databricks/` (retain as read-only archive, update imports).

At no point are both old and new layouts deploying the same resource. Migration is resource-by-resource with explicit handoff.

---

## 7. Success Criteria

| Criterion | Metric | Target |
|-----------|--------|--------|
| Bundle validation | `databricks bundle validate` passes for all bundles | 100% |
| Python test coverage | pytest coverage for foundation_python | >= 60% |
| CI gate | PRs touching `databricks/**` are validated | 100% |
| Zero drift | All prod resources have a Git-tracked definition | 100% |
| Deployment time | `databricks bundle deploy -t prod` for any single bundle | < 5 min |
| Doc alignment | Architecture doc updated with every structural change | 100% |

---

## 8. Non-Goals

- Migrating the Databricks workspace to a different region
- Implementing real-time streaming (batch-first; streaming is Phase 2+)
- Replacing Power BI with Databricks SQL dashboards (Power BI remains primary; dashboards are supplemental)
- Multi-workspace federation (single workspace with catalog isolation)

---

## 9. Dependencies

| Dependency | Status | Owner |
|-----------|--------|-------|
| Databricks CLI >= 0.230.0 | Available | Platform team |
| Unity Catalog `dev_ppm`, `staging_ppm`, `ppm` | Created | Platform team |
| Service principal `finance-ppm-service-principal` | Exists | Platform team |
| Azure Key Vault `kv-ipai-dev` | Active | Platform team |
| GitHub Actions runners | Active | CI team |

---

*Spec bundle: `spec/databricks-bundles-foundation/`*
*Last updated: 2026-03-22*
