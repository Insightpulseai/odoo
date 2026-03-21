# Constitution: Databricks Bundles Foundation

> Non-negotiable principles governing Databricks Asset Bundle delivery for the InsightPulse AI platform.
> This document is the authority for all bundle-related decisions. No downstream spec, plan, or task may contradict it.

---

## Principle 1: Bundles Are the Unit of Deployment

Every deployable Databricks artifact (job, pipeline, SQL dashboard, model serving endpoint) must belong to exactly one Databricks Asset Bundle. Loose notebooks, ad-hoc jobs created in the workspace UI, and untracked resources are prohibited in staging and production targets. The `databricks bundle deploy` command is the only sanctioned deployment mechanism.

**Implication**: No console-only resource creation. Every resource has a YAML definition checked into Git.

---

## Principle 2: Unity Catalog Is the Governance Plane

All tables, views, volumes, functions, and models must be registered in Unity Catalog. Hive metastore (`hive_metastore`) is banned for new development. Catalog names follow the environment convention: `dev_ppm`, `staging_ppm`, `ppm` (production). Schema names follow the medallion convention: `bronze`, `silver`, `gold`, `platinum`.

**Implication**: Every `databricks.yml` must declare `catalog` and `schema` as variables resolved per target.

---

## Principle 3: Medallion Architecture Is Mandatory

All data transformations follow the Bronze-Silver-Gold-Platinum layering:

| Layer | Purpose | Write Pattern | Read Access |
|-------|---------|---------------|-------------|
| Bronze | Raw ingestion, append-only | Streaming or batch append | Data engineers only |
| Silver | Cleaned, deduplicated, typed | Merge/upsert (SCD Type 1/2) | Data engineers + analysts |
| Gold | Business aggregates, KPIs | Incremental materialization | Analysts + BI tools |
| Platinum | Serving views, API surfaces | Read-only views over Gold | Power BI, agents, APIs |

No transformation may skip a layer (e.g., Bronze direct to Gold is banned).

---

## Principle 4: Environments Are Isolated by Catalog

Dev, staging, and production share the same Databricks workspace but are isolated by Unity Catalog:

- `dev_ppm.*` - development (current user root path)
- `staging_ppm.*` - staging (shared root path)
- `ppm.*` - production (shared root path, service principal, permissions locked)

Cross-environment reads are prohibited. A Gold table in dev must never reference a Silver table in prod.

---

## Principle 5: CI/CD Is Bundle-Native

The CI/CD pipeline uses `databricks bundle validate` and `databricks bundle deploy` as first-class steps. Bundle validation runs on every PR that touches `databricks/**`. Deployment to staging requires PR approval. Deployment to production requires PR approval plus passing staging tests.

**Pipeline stages**:
1. `validate` - syntax and schema check (`databricks bundle validate -t <target>`)
2. `test` - unit tests for Python bundles (`pytest`)
3. `deploy-dev` - automatic on merge to `main` (dev target)
4. `deploy-staging` - manual trigger or tag-based
5. `deploy-prod` - manual trigger with approval gate

---

## Principle 6: Secrets Never Enter Bundle Definitions

Bundle YAML files must never contain literal secrets, tokens, or passwords. All sensitive values are resolved at runtime via:

- Databricks secret scopes (for notebook/job runtime)
- Azure Key Vault references (for CI/CD pipelines)
- Environment variables in CI runners

Secret scope naming: `ipai-<environment>` (e.g., `ipai-dev`, `ipai-prod`).

---

## Principle 7: One Bundle Per Concern

Each bundle owns a single deployment concern:

| Bundle | Concern |
|--------|---------|
| `foundation_python` | Core Python libraries, shared utilities, medallion transforms |
| `lakeflow_ingestion` | LakeFlow/DLT ingestion pipelines (Bronze layer) |
| `sql_warehouse` | SQL-based transforms, marts, serving views, dashboards |

Bundles may depend on shared Python packages (published as wheels) but must not cross-reference each other's resource definitions.

---

## Principle 8: Documentation and Spec Travel with Code

Every bundle directory contains its own `databricks.yml`, `pyproject.toml` (for Python bundles), and resource definitions. Architecture decisions are recorded in `docs/architecture/DATABRICKS_BUNDLES_BASELINE.md`. The spec kit (`spec/databricks-bundles-foundation/`) governs the overall pattern. Changes to bundle structure require a spec update in the same PR.

**Implication**: A PR that adds a new bundle without updating the spec kit or architecture doc is incomplete.

---

## Boundary Conditions

- **Upstream dependency**: Databricks CLI >= 0.230.0 (bundle v2 schema support)
- **Workspace**: Single workspace, multi-catalog isolation
- **Compute**: Shared clusters for dev, job clusters for staging/prod
- **Region**: `southeastasia` (Azure)
- **Service principal**: `finance-ppm-service-principal` (prod only)
- **Existing assets**: `infra/databricks/` is the legacy monolithic layout; `databricks/bundles/` is the canonical target

---

*Spec bundle: `spec/databricks-bundles-foundation/`*
*Last updated: 2026-03-22*
