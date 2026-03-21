# PRD — Databricks Bundles Foundation

## Document Control

| Field | Value |
|-------|-------|
| Status | Approved |
| Constitution | `spec/databricks-bundles-foundation/constitution.md` |
| Plan | `spec/databricks-bundles-foundation/plan.md` |
| Tasks | `spec/databricks-bundles-foundation/tasks.md` |
| Architecture | `docs/architecture/DATABRICKS_BUNDLES_BASELINE.md` |

## Problem

The current Databricks layout uses a single monolithic directory (`infra/databricks/`) with no bundle structure, no per-lane isolation, no CI validation, and no environment parameterization. This prevents safe promotion, makes blast radius unpredictable, and blocks the team from adopting Databricks best-practice patterns.

## Goal

Deliver a multi-bundle Databricks Asset Bundle layout with:
- Three baseline capability lanes (`foundation_python`, `lakeflow_ingestion`, `sql_warehouse`)
- Shared configuration layer
- Per-bundle environment targets (`dev`, `staging`, `prod`)
- CI pipeline that validates changed bundles on every pull request
- Architecture documentation and anti-drift controls

## Non-Goals

- Provisioning Azure networking, storage accounts, or Key Vault
- Provisioning the Databricks workspace itself
- Provisioning Fabric workspaces
- Authoring Power BI semantic models
- Migrating existing legacy notebooks (separate effort)

## Users

| Role | Interaction |
|------|-------------|
| Data Engineer | Authors transforms, jobs, pipelines inside bundles |
| Platform Engineer | Manages shared config, CI pipeline, environment targets |
| Data Analyst | Consumes Gold/Platinum SQL views via SQL Warehouse bundle |
| AI/ML Engineer | Extends foundation_python with model training jobs |
| DevOps | Reviews and merges bundle changes, monitors CI |

## Target Outcome

A developer can:
1. Create a new job or pipeline inside the correct bundle
2. Run `databricks bundle validate` locally
3. Open a pull request
4. See CI automatically detect the changed bundle, validate it, and run tests
5. Merge and have the bundle deploy to the target environment

## Functional Requirements

### FR-1: Bundle Taxonomy
Three baseline bundles must exist:
- `foundation_python` — Python-driven engineering workloads
- `lakeflow_ingestion` — DLT/Lakeflow ingestion pipelines
- `sql_warehouse` — SQL-first marts, serving views, dashboards

### FR-2: Shared Configuration
A `databricks/shared/` directory must hold common variables (catalog, schemas, workspace host) consumable by all bundles via `include`.

### FR-3: Environment Targets
Each deployable bundle must define `dev`, `staging`, and `prod` targets with parameterized values.

### FR-4: Bundle Validation
Each bundle must pass `databricks bundle validate` with no errors.

### FR-5: CI Pipeline
A GitHub Actions workflow must:
- Detect which bundles changed using path filters
- Run `databricks bundle validate` on each changed bundle
- Run Python tests for bundles with a `tests/` directory
- Check documentation/spec alignment

### FR-6: Smoke Job
`foundation_python` must include a smoke job that validates the runtime environment.

### FR-7: Pipeline Stub
`lakeflow_ingestion` must include a pipeline resource definition and a placeholder entrypoint.

### FR-8: SQL Mart Stub
`sql_warehouse` must include at least one example SQL view in `src/sql/marts/`.

### FR-9: Patterns Directory
A `databricks/bundles/patterns/` directory must contain reference documentation (not deployable assets) mapping upstream Databricks bundle-examples to the local layout.

### FR-10: Dual CI surface support
The repository must support Databricks bundle validation from either:
- GitHub Actions
- Azure Pipelines

The chosen CI executor may change by environment or governance model, but the Databricks bundle contract must remain identical.

### FR-11: Odoo.sh benchmark staging behavior
The staging environment must validate against sanitized production-like data and must neutralize or redirect external side effects.

### FR-12: Promotion-only production
Production may only deploy a revision that has already passed development validation and staging verification.

### FR-13: Deterministic rollback reference
The delivery system must persist a last-known-good production release reference for deterministic rollback.

### FR-14: Reference-architecture dataflow alignment
The baseline bundle model must support a Microsoft-aligned dataflow:

- ingestion from streaming, lake, and federated relational sources
- bronze / silver / gold transformation
- governed Delta Lake storage
- Databricks SQL / AI serving
- downstream Fabric / Power BI consumption

### FR-15: Governance anchor
The architecture must treat Unity Catalog as the primary governance anchor for Databricks-managed data products.

### FR-16: Platform integration separation
Purview publishing, identity, secrets, monitoring, cost controls, and security controls must remain outside Databricks bundle roots.

## Non-Functional Requirements

### NFR-1: No Manual Workspace Resources
All production Databricks resources must be defined in bundle source. Manual-only resources are prohibited per the constitution.

### NFR-2: No Substrate Provisioning
Bundles must not provision Azure networking, storage, Key Vault, Entra objects, or Databricks workspaces.

### NFR-3: Deterministic CI
CI must produce the same result for the same commit. No flaky tests, no external service dependencies during validation.

### NFR-4: Documentation Alignment
Architecture docs must match the implemented bundle taxonomy. Drift is a CI failure.

## Acceptance Criteria

- [ ] `databricks/` directory exists with `README.md`, `shared/`, and `bundles/`
- [ ] Three bundles exist: `foundation_python`, `lakeflow_ingestion`, `sql_warehouse`
- [ ] `databricks/shared/variables.yml` defines common variables
- [ ] Each bundle has `databricks.yml` with `dev`, `staging`, `prod` targets
- [ ] `foundation_python` has a smoke job resource and Python source
- [ ] `lakeflow_ingestion` has a pipeline resource and placeholder entrypoint
- [ ] `sql_warehouse` has a SQL mart example
- [ ] `.github/workflows/databricks-bundles-ci.yml` exists and runs on PR
- [ ] `docs/architecture/DATABRICKS_BUNDLES_BASELINE.md` exists
- [ ] `spec/databricks-bundles-foundation/` has all four spec files

## Success Metrics

| Metric | Target |
|--------|--------|
| Bundle validation pass rate | 100% on merge |
| CI detection accuracy | All changed bundles detected |
| Time to add a new job | < 30 minutes including CI pass |
| Manual workspace resources | 0 (excluding documented exceptions) |

## Risks

| Risk | Mitigation |
|------|------------|
| Databricks CLI version drift | Pin CLI version in CI workflow |
| Shared config becomes a monolith | Constitution rule limits shared scope |
| Teams bypass bundles for quick fixes | Anti-drift CI check, workspace audits |
| Environment target misconfiguration | Validation step in CI catches missing targets |

## Open Questions

| # | Question | Status |
|---|----------|--------|
| 1 | Should ML/serving bundles be added now or later? | Deferred — add when ownership is clear |
| 2 | Should Fabric mirroring config live in bundles? | No — Fabric is downstream consumption |
| 3 | Should legacy notebooks be migrated in this effort? | No — separate migration effort |
