# Data-Intelligence Repo Split Plan

## Objective

Create `data-intelligence` as the canonical standalone repo for Databricks, lakehouse, semantic, and governed analytical delivery assets.

## Scope

In scope:
- Databricks bundles, jobs, notebooks, pipelines, SQL
- Lakehouse contracts and medallion structure
- Semantic/data-product delivery assets
- CI, SSOT, docs, spec, tests, scripts for the data-intelligence plane

Out of scope:
- Direct Odoo runtime code
- Odoo addon code
- ACA/Azure runtime app deployment code not specific to data-intelligence workloads
- Archived legacy assets unless explicitly reactivated

## Source Surfaces to Migrate

### Primary active surfaces

| Source Path | File Count | Content |
|-------------|-----------|---------|
| `infra/databricks/` | ~100 | Databricks bundle: notebooks, DLT, SQL, jobs, schemas, scripts, pyproject |
| `odoo/infra/databricks/sql/` | ~10 | Medallion SQL (bronze → platinum) + DLT marketing pipeline |
| `lakehouse/contracts/` | 1 | Tableau BI contract stub |

### Legacy / review-only surface

| Source Path | File Count | Content |
|-------------|-----------|---------|
| `archive/work/databricks/` | ~60 | Older notebooks, DAB config, apps, dashboards, terraform state |

## Target Repo Structure

```
data-intelligence/
├── .github/
│   └── workflows/
├── docs/
├── spec/
├── ssot/
├── databricks/
│   ├── bundles/
│   ├── pipelines/
│   ├── jobs/
│   ├── notebooks/
│   └── sql/
├── lakehouse/
│   ├── contracts/
│   ├── bronze/
│   ├── silver/
│   └── gold/
├── semantic/
├── tests/
└── scripts/
```

## Migration Principles

1. **Move active assets, not historical clutter.** Only migrate files that are actively used or have clear future value.
2. **Preserve git history where practical.** Use `git filter-repo` or `git subtree split` to maintain commit history for moved files.
3. **Leave only monorepo integration stubs** where Odoo/runtime coupling is real. Stubs should be thin references, not full copies.
4. **Do not duplicate ownership** between monorepo and standalone repo. Every file has exactly one canonical owner.
5. **Re-point docs, SSOT, passports, and scorecards** in the same change window to prevent reference drift.

## Classification Rules

### Move

Assets whose primary purpose is:
- Databricks workload delivery
- Medallion/lakehouse transformation
- Analytical contracts
- Governed semantic outputs
- Data-intelligence CI/tests/scripts

### Keep in Monorepo

Assets whose primary purpose is:
- Odoo runtime integration (e.g., JDBC connection config referenced by Odoo modules)
- Direct app-runtime configuration
- Thin references/stubs that point to the standalone repo

### Archive or Review

Assets that are:
- Superseded by newer implementations
- Duplicated across paths
- Stale experiments or abandoned prototypes
- Terraform state files (should not be committed)

## Migration Phases

### Phase 0 — Inventory and Classification

- Inventory all candidate files across all 4 source surfaces
- Classify each file as `move` / `keep` / `archive` / `review`
- Identify coupling blockers (files that reference both Odoo and Databricks paths)
- Produce `ssot/data-intelligence/migration_inventory.yaml` with file-level classification

### Phase 1 — Repo Bootstrap

- Create `data-intelligence` repo in the org
- Scaffold canonical top-level directory structure
- Add baseline: CLAUDE.md, spec/, docs/, ssot/, tests/, scripts/, CI workflows
- Add SSOT validation workflow

### Phase 2 — Active Asset Migration

- Move `infra/databricks/` active delivery assets → `databricks/`
- Move `odoo/infra/databricks/sql/` analytical SQL → `databricks/sql/`
- Move `lakehouse/contracts/` governed contracts → `lakehouse/contracts/`
- Update all internal path references

### Phase 3 — Monorepo Cleanup

- Remove migrated files from monorepo
- Leave stubs/references only where Odoo coupling is real
- Update monorepo CI to remove data-intelligence-specific checks
- Update monorepo SSOT to remove data-intelligence ownership

### Phase 4 — Validation and Cutover

- Run CI and SSOT validation in new repo
- Verify no broken references remain in monorepo
- Update agent passport: remove `standalone_repo_not_yet_created` blocker
- Update portfolio scorecard: remove `blocking_gate`
- Update target-state docs

## Exit Criteria

The split is complete when:

- [ ] `data-intelligence` repo exists with canonical structure
- [ ] All active data-intelligence assets are owned in the standalone repo
- [ ] Monorepo retains only valid integration stubs
- [ ] CI and SSOT checks pass in the new repo
- [ ] CI and SSOT checks pass in the monorepo (no broken refs)
- [ ] Passport blocker `standalone_repo_not_yet_created` is removed
- [ ] Portfolio scorecard updated with new repo status
- [ ] data-intelligence agent promoted to L2 / S06

## Related

- Passport: `agents/passports/data-intelligence.yaml`
- Migration manifest: `ssot/data-intelligence/repo_split_manifest.yaml`
- Migration inventory: `ssot/data-intelligence/migration_inventory.yaml`
- Portfolio scorecard: `ssot/agent-platform/portfolio_scorecard.yaml`
- Target-state topology: `ssot/repo/org_topology.yaml`
