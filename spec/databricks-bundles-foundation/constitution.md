# Databricks Bundles Constitution

## Status
Approved

## Purpose
Standardize how the `data-intelligence` repository defines, validates, deploys, and promotes Azure Databricks workloads using Declarative Automation Bundles.

## Scope
This constitution governs:
- Databricks bundle structure
- Databricks CI/CD conventions
- Environment target conventions
- Shared code/config boundaries
- Documentation and anti-drift controls

This constitution does **not** govern:
- Azure landing zone / network provisioning
- Databricks workspace provisioning
- Fabric workspace provisioning
- Power BI semantic model authoring details
- Cross-repo platform orchestration

## Principles

### 1. Bundles are the deployable Databricks contract
All Databricks workspace resources must be defined and promoted through bundle-managed source files.
Examples include:
- jobs
- Lakeflow / pipeline resources
- SQL assets
- dashboards
- serving-related configs where applicable

Manual workspace-only production resources are prohibited unless explicitly documented as a temporary exception with an owner and expiry date.

### 2. Separate capability lanes into separate bundles
A bundle must represent a bounded delivery capability, not the entire workspace estate.

Canonical baseline lanes:
- `foundation_python`: shared Python-driven engineering workloads
- `lakeflow_ingestion`: ingestion and pipeline-centric workloads
- `sql_warehouse`: SQL-first marts, serving, and dashboard-supporting assets

A new sibling bundle must be created when:
- ownership changes materially
- release cadence differs materially
- runtime surface differs materially
- blast radius would otherwise become too large

### 3. Keep substrate outside bundle ownership
Bundles do not provision:
- Azure networking
- storage accounts
- Key Vault
- Entra objects
- Databricks workspaces
- Fabric workspaces

Those concerns belong to `infra` / platform provisioning layers.

### 4. Environment isolation is mandatory
Every deployable bundle must support isolated targets:
- `dev`
- `staging`
- `prod`

Environment-specific values must be parameterized, not hardcoded.

### 5. Version everything required for promotion
The same repository change must capture, where relevant:
- source code
- tests
- bundle configuration
- resource definitions
- environment overlays
- architecture / spec changes for contract-affecting updates

### 6. Shared code is allowed; shared deployables are not
Common libraries and shared variables may live in a shared location and be synced into multiple bundles.
However:
- deployment ownership stays with the consuming bundle
- shared code must not become an undeclared platform-within-a-platform
- shared files must be explicitly referenced and validated

### 7. Databricks and Fabric have distinct roles
Within this repository contract:
- Databricks owns data engineering, governed data products, pipelines, jobs, and SQL-serving surfaces
- Fabric / Power BI is treated as downstream semantic and reporting consumption, not as a Databricks bundle deployment target

### 8. CI is the gatekeeper
A pull request that changes bundle-managed assets must run:
- changed-bundle detection
- bundle validation
- relevant tests
- documentation/spec alignment checks

### 9. Anti-drift is enforced
The following are considered drift:
- production jobs or pipelines that exist only in the workspace
- bundle resources changed manually without source updates
- environment targets missing from a deployable bundle
- documentation that contradicts the implemented bundle taxonomy

## Required Directory Contract

```text
databricks/
  README.md
  bundles/
    foundation_python/
    lakeflow_ingestion/
    sql_warehouse/
    patterns/
```

## Exceptions

Exceptions must be documented in architecture docs or a Spec Kit artifact and include:
- justification
- owner
- review date
- removal plan

## Amendment Rules

Any change to:
- bundle taxonomy
- target model
- anti-drift rules
- Databricks/Fabric boundary

requires updates to:
- this constitution
- PRD
- plan
- tasks
- architecture baseline doc
