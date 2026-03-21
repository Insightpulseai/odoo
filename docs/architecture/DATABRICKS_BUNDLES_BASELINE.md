# Databricks Bundles Baseline Architecture

## Purpose

This document defines the architecture baseline for Databricks Asset Bundle delivery in the InsightPulse AI platform. It is governed by `spec/databricks-bundles-foundation/constitution.md`.

## Architecture Position

### Role Split

| Platform | Role | Owns |
|----------|------|------|
| **Databricks** | Data engineering, governed data products | Jobs, pipelines, SQL serving, notebooks, DLT |
| **Fabric / Power BI** | Downstream semantic and reporting consumption | Semantic models, reports, dashboards, OneLake mirroring |
| **Azure (infra)** | Substrate provisioning | Networking, storage, Key Vault, Entra, workspace provisioning |

### Why This Boundary Exists

1. **Databricks bundles are the deployable contract** for all data engineering workloads. They define what runs in the workspace.
2. **Fabric/Power BI is consumption-only** from the bundle perspective. Bundles do not deploy to Fabric.
3. **Azure infra is substrate** — bundles assume the workspace, storage, and identity layer exist. They do not provision them.

This separation ensures that:
- A bundle change cannot accidentally break networking or storage
- A Fabric change cannot accidentally break a Databricks job
- Each layer can be versioned, tested, and promoted independently

## Canonical Directory Layout

```text
databricks/
  README.md                          # Operating rules, directory map
  shared/
    variables.yml                    # Common variables (catalog, schemas, etc.)
    README.md                        # Rules for shared assets
  bundles/
    foundation_python/               # Python-driven engineering workloads
      databricks.yml                 # Bundle definition with env targets
      pyproject.toml                 # Python package config
      src/
        ipai_data_intelligence/
          __init__.py
          jobs/
          transforms/
          quality/
      tests/
      resources/
        jobs/
    lakeflow_ingestion/              # DLT/Lakeflow ingestion pipelines
      databricks.yml
      pyproject.toml
      src/
        lakeflow_ingestion_etl/
      resources/
        pipelines/
        jobs/
    sql_warehouse/                   # SQL-first marts and serving
      databricks.yml
      src/
        sql/
          marts/
      resources/
        jobs/
    patterns/                        # Reference docs (not deployable)
      README.md
      KNOWLEDGE_BASE_CROSSWALK.md
```

## Bundle Taxonomy

### Lane 1: `foundation_python`

**Purpose**: Core Python library for medallion transforms, data quality checks, and shared engineering jobs.

**Contains**: Python source (`src/ipai_data_intelligence/`), jobs, tests, wheel build config.

**Deploys**: Python wheel + job definitions to Databricks workspace.

### Lane 2: `lakeflow_ingestion`

**Purpose**: DLT/Lakeflow ingestion pipelines for Bronze layer population.

**Contains**: Pipeline definitions, Python ETL source, job triggers.

**Deploys**: DLT pipelines + triggering jobs to Databricks workspace.

### Lane 3: `sql_warehouse`

**Purpose**: SQL-first Gold/Platinum marts, serving views, and dashboard-supporting assets.

**Contains**: SQL files, SQL task job definitions.

**Deploys**: SQL tasks executed via SQL Warehouse to Databricks workspace.

### Lane 4: `patterns` (reference only)

**Purpose**: Documents mapping upstream `databricks/bundle-examples` to the local layout.

**Contains**: Markdown reference files only. Never deployed.

## Shared Folder Rules

The `databricks/shared/` directory holds common configuration consumable by all bundles.

**Allowed**:
- `variables.yml` — common variable definitions (catalog, schemas, workspace host)
- Shared Python utility libraries (if needed in the future)

**Disallowed**:
- Job definitions
- Pipeline definitions
- Resource files
- Anything that would be deployed independently

**Consumption**: Each bundle's `databricks.yml` includes shared files via relative path:
```yaml
include:
  - ../../shared/*.yml
```

## Environment Model

Every deployable bundle must define three targets:

| Target | Purpose | Catalog |
|--------|---------|---------|
| `dev` | Development iteration | `ipai_dev` |
| `staging` | Pre-production validation | `ipai_staging` |
| `prod` | Production workloads | `ipai` |

Environment-specific values (workspace host, catalog, default cluster config) are parameterized in the bundle's target section and override shared variables.

## Anti-Drift Rules

The following are considered drift and must be prevented or remediated:

1. **Workspace-only resources** — Production jobs or pipelines that exist only in the workspace with no bundle source. Prohibited per constitution.
2. **Manual resource changes** — Bundle resources changed via UI/API without corresponding source updates. Detected by comparing bundle state to workspace state.
3. **Missing environment targets** — A deployable bundle that lacks any of the three required targets. Caught by CI validation.
4. **Documentation mismatch** — Architecture docs that contradict the implemented bundle taxonomy. Checked by CI spec alignment step.

## CI Contract

The CI pipeline (`.github/workflows/databricks-bundles-ci.yml`) enforces:

1. **Changed-bundle detection** — Only validates bundles with changed files.
2. **Bundle validation** — `databricks bundle validate` must pass for each changed bundle.
3. **Python tests** — `pytest` runs for bundles with a `tests/` directory.
4. **Doc/spec alignment** — Checks that required documentation exists and is consistent.

## Decision Guide

### When to create a new bundle

Create a new sibling bundle when:
- Ownership changes materially (different team owns it)
- Release cadence differs materially (daily vs. monthly)
- Runtime surface differs materially (Python vs. SQL vs. DLT)
- Blast radius would otherwise become too large

### When to add to an existing bundle

Add to an existing bundle when:
- The new asset shares the same owner, cadence, and runtime surface
- The new asset is a natural extension of the bundle's capability lane
- Adding it does not materially increase blast radius

### When to use shared/

Use `databricks/shared/` when:
- A variable or config is consumed by two or more bundles
- The shared asset has no independent deployment lifecycle
- The shared asset does not create coupling between bundles' release schedules
