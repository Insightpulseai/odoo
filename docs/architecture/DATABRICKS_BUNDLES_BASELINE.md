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

## Odoo.sh Benchmark Model

> **Benchmark:** "Odoo.sh-style promotion semantics on Azure DevOps for Databricks bundles: dev validates fast, staging replays against fresh sanitized production-like state, prod promotes only validated revisions, and rollback restores the last known good release."

This repository adopts **Odoo.sh-style stage semantics** as the benchmark for Databricks delivery:

- **Development**
  - branch/PR-oriented validation
  - isolated target
  - non-production data
  - fast feedback: bundle validation, unit tests, smoke tests

- **Staging**
  - production-like validation target
  - refreshed from sanitized production-like data
  - side effects neutralized or redirected to test integrations
  - used for final pre-production verification

- **Production**
  - promotion only from a previously validated revision
  - environment-gated deployment
  - rollback to the last known good deployed revision if production validation fails

## Side-effect Neutralization Rule

Staging must not perform irreversible or external-production side effects.
Examples:
- no live outbound notifications
- no live payment or billing side effects
- no live external mutations unless explicitly test-scoped

## Promotion Rule

A revision must pass:
1. dev validation
2. staging deployment + integration checks
3. production approval/check gates

before it becomes the active production revision.

## Rollback Rule

Production rollback must restore the last known good deployed bundle revision/manifest.
Do not rely on ad hoc manual reconstruction.

### Supported execution surfaces

The repository supports both:
- GitHub Actions
- Azure Pipelines

Selection rule:
- Use GitHub Actions when the repository is operating in GitHub-native delivery mode.
- Use Azure Pipelines when release governance, service connections, variable groups, approvals, or enterprise Azure DevOps controls are the governing surface.

This mirrors Microsoft's Azure DevOps setup pattern for enterprise automation, where project assets, service connections, pipelines, permissions, and variable groups are part of the delivery contract.

### Azure DevOps-specific rule

If Azure Pipelines is enabled for bundle validation/deployment:
- service connections must be environment-scoped
- variable groups must hold non-secret environment configuration references
- secrets must remain in the canonical secret backend and be injected at runtime
- bundle validation must still remain path-scoped by changed bundle root

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

## Microsoft Reference Architecture Alignment

This repository aligns to Microsoft's "Data Intelligence End-to-End with Azure Databricks and Microsoft Fabric" reference architecture.

### Canonical platform split

- **Azure Databricks** is the primary engineering plane for:
  - streaming and batch ingestion
  - Delta Live Tables / Lakeflow-style pipelines
  - Auto Loader ingestion from ADLS Gen2
  - Lakehouse Federation from relational sources
  - medallion processing (bronze / silver / gold)
  - Databricks SQL serving
  - notebooks, MLflow, Feature Store, Vector Search, Model Serving, Lakehouse Monitoring, and Workflows

- **Microsoft Fabric / Power BI** is the downstream semantic and reporting plane for:
  - published semantic models
  - analyst-facing reports and dashboards
  - Copilot-assisted BI consumption

- **Azure platform services** provide the control envelope:
  - Entra ID
  - Key Vault
  - Azure Monitor
  - Cost Management
  - Azure DevOps / GitHub
  - Defender for Cloud

### Governance model

- Databricks bundle roots define deployable data and AI workloads.
- Unity Catalog is the governance anchor for governed data products.
- Purview metadata publishing is a platform integration concern, not a bundle-local ownership concern.

### Dataflow model

The default repository dataflow assumes:
1. ingestion from Event Hubs, ADLS Gen2, and federated relational sources
2. transformation through bronze / silver / gold
3. governed storage in Delta Lake on ADLS Gen2
4. SQL / AI serving from Databricks
5. downstream semantic/report consumption through Fabric / Power BI

## IDE Project Selection Rule

When multiple Databricks project roots are detected in the workspace:

- choose `infra/databricks` only for substrate/IaC work
- choose a specific bundle root for workload delivery work
- do not use nested duplicate paths such as `odoo/.../odoo/.../infra/databricks`

Nested duplicate detections indicate workspace-root drift or recursive folder inclusion and must not be treated as canonical project roots.

Default selection for general Databricks engineering work: `databricks/bundles/foundation_python`.
