# Spec Alignment Repair Log

Tracking the normalization of `spec/**` files to align with the canonical architecture.

## Canonical Replacements

| Deprecated Term | Canonical Replacement | Reason |
|-----------------|-----------------------|--------|
| `Tableau` | `Power BI` | Settled BI authority |
| `Superset` | `Power BI` / `Azure Workbooks` | BI/Logging alignment |
| `ops-platform` (repo) | `platform` | Repo naming normalization |
| `design-system` (repo) | `design` | Repo naming normalization |
| `lakehouse` (repo) | `data-intelligence` | Repo naming normalization |
| `lakehouse` (product) | `Data Intelligence` | Naming alignment |
| `M365 Agents SDK` | `Channel Layer` | Architectural boundary enforcement |
| `M365 Copilot` | `Productivity Surface` | Architectural boundary enforcement |
| `Copilot Studio` | `Delivery Surface` | Architectural boundary enforcement |
| `Odoo Copilot UI` | `Productivity Surface` | ERP integration capabilities mapped |

## Patched Specs

| Spec Bundle | Files Patched | Changes |
|-------------|---------------|---------|
| `adls-etl-reverse-etl` | `tasks.md`, `prd.md`, `plan.md` | Tableau -> Power BI, closed decide tasks |
| `finance-unified` | `tasks.md` | Superset -> Power BI |
| `odoo-sh-azure-equivalent`| `tasks.md` | Superset -> Power BI/Workbooks |
| `plane-unified-docs` | `tasks.md` | Superset -> Power BI |
| `seed-dedup-remediation` | `plan.md`, `tasks.md` | ops-platform -> platform |
| `odoo-copilot-azure-runtime`| `constitution.md` | ops-platform -> platform |
| `fluent-designer-agent` | `plan.md` | design-system -> design |
| `azure-selfhost-migration` | `plan.md`, `tasks.md`, `prd.md`, `constitution.md` | ops-platform -> platform |
| `docs-platform` | `constitution.md` | design-system -> design |
| `docs/architecture/` | `enterprise_data_platform.md` | Tableau/Superset -> Power BI |
| `docs/delivery/` | `GO_LIVE_ACCELERATION_PLAN.md` | Tableau -> Power BI |
| `agent-platform` | `constitution.md`, `plan.md`, `tasks.md`, `prd.md` | Odoo + M365 Capability Map added |
| `infra/docs/` | `IDENTITY_TARGET_STATE.md` | M365 admin governance |

## Verification Status

- [x] **Subtree Document Sync**: Synchronized `odoo/README.md` and `odoo/CLAUDE.md` with root versions to ensure consistent governance and "Hard Rules" enforcement in the Odoo runtime subtree.
- [x] **Global sweep**: Run full `check_spec_architecture_terms.sh` sweep. (PASS)
- [x] **M365 Boundary Gate**: Verified M365 SDK vs Runtime distinction across all docs.
- [x] **Spec Alignment**: Address all stale `plan.md`, `prd.md`, or `tasks.md` files where tasks depend on them.
