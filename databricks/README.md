# Databricks Bundles

> Canonical location for Databricks Asset Bundle definitions.
> Spec: `spec/databricks-bundles-foundation/`
> Architecture: `docs/architecture/DATABRICKS_BUNDLES_BASELINE.md`

## Operating Rule

All Databricks workspace resources must be defined and promoted through bundle-managed source files. Manual workspace-only production resources are prohibited unless explicitly documented as a temporary exception.

## Directory Map

```text
databricks/
  README.md                 # This file
  shared/
    variables.yml           # Common variables consumed by all bundles
    README.md               # Rules for shared assets
  bundles/
    foundation_python/      # Python-driven engineering workloads
    lakeflow_ingestion/     # DLT/Lakeflow ingestion pipelines
    sql_warehouse/          # SQL-first marts and serving
    patterns/               # Reference docs (not deployable)
```

## Bundle Creation Rules

1. Each bundle is a standalone `databricks bundle` target
2. Each bundle must have `databricks.yml` with `dev`, `staging`, `prod` targets
3. Each bundle must pass `databricks bundle validate` with no errors
4. New bundles require justification per the constitution

## Environment Rules

| Target | Catalog | Purpose |
|--------|---------|---------|
| `dev` | `ipai_dev` | Development iteration |
| `staging` | `ipai_staging` | Pre-production validation |
| `prod` | `ipai` | Production workloads |

## Shared Asset Rules

- `shared/variables.yml` holds common variables (catalog, schemas, workspace host)
- Bundles consume shared config via `include: [../../shared/*.yml]`
- Shared directory must not contain deployable resources (jobs, pipelines)

## Do Not

- Create resources directly in the Databricks workspace without bundle source
- Put Azure infrastructure provisioning in bundles (use `infra/azure/`)
- Put Fabric/Power BI config in bundles (Fabric is downstream consumption)
- Deploy shared config as a standalone bundle
- Add new bundles without updating the spec and architecture docs
