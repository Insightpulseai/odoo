# Pulser for Odoo — Boards Backlog Packs

Authoritative backlog packs for the Pulser/Odoo program, organized by epic.
Each pack translates a D365 / Microsoft reference track into Odoo-on-Azure
**displacement, implementation, and operations** work — not D365 implementation work.

## Packs

| File | Epic | Source reference |
|---|---|---|
| [`epic-01-migration-uat-golive.md`](epic-01-migration-uat-golive.md) | Migration, UAT, and Go-Live Readiness | D365 F&O migration/go-live learning path |
| [`epic-02-architecture-dev-hardening.md`](epic-02-architecture-dev-hardening.md) | Architecture, Development, and Platform Hardening | D365 F&O developer track |
| [`epic-03-azure-postgresql-foundation.md`](epic-03-azure-postgresql-foundation.md) | Azure PostgreSQL Foundation and Resilience | Azure Samples (FastAPI+PG, Resiliency, postgres-agents) |
| [`epic-04-azure-pipelines-github.md`](epic-04-azure-pipelines-github.md) | Azure Pipelines and GitHub Delivery Integration | microsoft/azure-pipelines-yaml, Azure/pipelines action |
| [`epic-05-admin-tooling-ui-test.md`](epic-05-admin-tooling-ui-test.md) | Admin Tooling and UI Test Automation (secondary) | MS model-driven app dev tools page + Easy Repro testing page |

## Status

- **Format:** Markdown-readable backlog with Epic / Feature / Story hierarchy
- **Next step (optional):** consolidated deduplicated backlog map across all 4 packs
- **Next step (optional):** ADO CLI scripted import into Azure Boards (`insightpulseai/ipai-platform`)
- **Cross-reference:** every story description should cite the Pulser doctrine set:
  - `CLAUDE.md` §"Odoo extension and customization doctrine"
  - `spec/pulser-odoo/prd.md` §0 Architecture Doctrine
  - `ssot/benchmarks/parity_matrix.yaml`

## Governance

Every backlog item MUST be framed as Odoo-on-Azure displacement, **not** D365 implementation. D365 concepts are translated, not cloned. Explicit "not applicable / substitute pattern" notes required where D365 assumptions don't fit Odoo.
