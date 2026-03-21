# Databricks Bundles Baseline Architecture

> Architecture decision record for the multi-bundle Databricks Asset Bundle layout.
> Spec: `spec/databricks-bundles-foundation/`
> Canonical path: `databricks/bundles/`

---

## 1. Context

InsightPulse AI uses Databricks on Azure (Southeast Asia region) for data engineering, transformation, and serving. The Finance PPM Control Room is the primary workload, consuming data from Odoo PostgreSQL and serving aggregates to Power BI.

The existing layout (`infra/databricks/`) is a monolithic configuration with a single `databricks.yml`, loose notebooks, and ad-hoc SQL files. This creates deployment coupling, testing gaps, and drift risk.

---

## 2. Decision

Adopt the Databricks Asset Bundle (DAB) pattern with a multi-bundle repository layout. Each bundle is independently deployable, testable, and validatable. The layout follows upstream `databricks/bundle-examples` patterns.

---

## 3. Bundle Inventory

```
databricks/
  bundles/
    foundation_python/       # Core Python library + medallion transforms
      databricks.yml         # Bundle definition (default_python pattern)
      pyproject.toml         # Python packaging
      src/ipai_data_intelligence/
      tests/
      fixtures/
      resources/
        jobs/
        pipelines/

    lakeflow_ingestion/      # LakeFlow/DLT ingestion (Bronze layer)
      databricks.yml         # Bundle definition (lakeflow_pipelines_python pattern)
      pyproject.toml
      src/lakeflow_ingestion_etl/
      resources/
        pipelines/
        jobs/

    sql_warehouse/           # SQL transforms, marts, serving views
      databricks.yml         # Bundle definition (default_sql pattern)
      src/sql/
        schemas/
        marts/
        serving/
      resources/
        jobs/
        dashboards/

    patterns/                # Reference patterns (not deployable)
      README.md
      KNOWLEDGE_BASE_CROSSWALK.md
```

---

## 4. Environment Model

| Target | Catalog | Root Path | Mode | Identity |
|--------|---------|-----------|------|----------|
| dev | `dev_ppm` | `/Workspace/Users/${current_user}/` | development | Current user |
| staging | `staging_ppm` | `/Workspace/Shared/<bundle>-staging` | development | Current user |
| prod | `ppm` | `/Workspace/Shared/<bundle>` | production | `finance-ppm-service-principal` |

All targets share the same Databricks workspace. Isolation is enforced by Unity Catalog (separate catalogs per environment) and workspace root paths.

---

## 5. Medallion Architecture Mapping

```
Bronze (append-only)          Silver (merge/upsert)          Gold (aggregate)          Platinum (serve)
  ${catalog}.bronze.*    -->    ${catalog}.silver.*    -->    ${catalog}.gold.*    -->    ${catalog}.platinum.*

lakeflow_ingestion           foundation_python              foundation_python          sql_warehouse
  DLT pipelines              Python transforms              Python transforms          SQL views
  JDBC extractors            Dedup / SCD                    KPI rollups               Power BI serving
```

---

## 6. CI/CD Pipeline

```
PR opened (databricks/**)
  |
  v
detect-bundles (dorny/paths-filter)
  |
  +---> foundation_python changed? ---> validate + pytest
  +---> lakeflow_ingestion changed? ---> validate + pytest
  +---> sql_warehouse changed? -------> validate
  |
  v
merge to main
  |
  v
deploy-dev (automatic, all changed bundles)
  |
  v
tag / manual trigger
  |
  v
deploy-staging (approval required)
  |
  v
deploy-prod (approval + staging tests pass)
```

**CI Workflow**: `.github/workflows/databricks-bundles-ci.yml`

---

## 7. Dependency Graph

```
foundation_python (wheel artifact)
  ^           ^
  |           |
  |           |
lakeflow_ingestion    sql_warehouse (no Python dependency)
  (imports wheel)
```

- `foundation_python` produces a wheel artifact (`ipai_data_intelligence`)
- `lakeflow_ingestion` can reference the wheel in its cluster libraries
- `sql_warehouse` has no Python dependencies; it uses SQL tasks only

---

## 8. Secret Management

| Scope | Environment | Source |
|-------|-------------|--------|
| `ipai-dev` | dev | Databricks secret scope, populated from Azure Key Vault |
| `ipai-staging` | staging | Databricks secret scope, populated from Azure Key Vault |
| `ipai-prod` | prod | Databricks secret scope, populated from Azure Key Vault |

Secrets referenced in notebooks/jobs: `dbutils.secrets.get(scope="ipai-<env>", key="<key>")`

CI/CD secrets: GitHub Actions secrets, injected as environment variables for `databricks bundle deploy`.

---

## 9. Migration from Legacy Layout

| Legacy Path | Target Bundle | Status |
|-------------|---------------|--------|
| `infra/databricks/notebooks/bronze/` | `lakeflow_ingestion` | Pending |
| `infra/databricks/notebooks/silver/` | `foundation_python` | Pending |
| `infra/databricks/notebooks/gold/` | `foundation_python` | Pending |
| `infra/databricks/sql/` | `sql_warehouse` | Pending |
| `infra/databricks/dlt/` | `lakeflow_ingestion` | Pending |
| `infra/databricks/resources/jobs/` | Per-bundle `resources/jobs/` | Pending |
| `infra/databricks/resources/pipelines/` | Per-bundle `resources/pipelines/` | Pending |
| `infra/databricks/databricks.yml` | Replaced by per-bundle `databricks.yml` | Pending |

---

## 10. Upstream Pattern Alignment

| Our Bundle | Upstream Pattern | Source |
|-----------|-----------------|--------|
| `foundation_python` | `default_python` | `databricks/bundle-examples` |
| `lakeflow_ingestion` | `lakeflow_pipelines_python` | `databricks/bundle-examples` |
| `sql_warehouse` | `default_sql` | `databricks/bundle-examples` |

Deviations from upstream patterns:
- Multi-catalog variable substitution (upstream uses single catalog)
- Service principal `run_as` in prod target (upstream uses current user)
- Wheel artifact cross-bundle consumption (upstream bundles are standalone)

---

## 11. Compute Model

| Bundle | Dev Compute | Staging/Prod Compute |
|--------|------------|---------------------|
| `foundation_python` | Shared interactive cluster | Job cluster (auto-terminated) |
| `lakeflow_ingestion` | DLT pipeline cluster (managed) | DLT pipeline cluster (managed) |
| `sql_warehouse` | SQL warehouse (serverless) | SQL warehouse (serverless) |

---

## 12. Open Questions

1. **Fabric mirroring**: Should Platinum serving views be mirrored to OneLake via Databricks-Fabric connector? (Deferred to Phase 5+)
2. **Streaming**: Should `lakeflow_ingestion` support streaming ingestion, or batch-only? (Batch-first per constitution)
3. **Dashboard migration**: Should existing Superset dashboards be recreated as Lakeview dashboards? (No -- Power BI is primary)

---

*Last updated: 2026-03-22*
