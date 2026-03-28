# Benchmark Matrix — Repo Structure

Three-tier benchmark hierarchy:
1. **SAP on Azure** → product docs, decision matrices, ops surface
2. **OCA** → addon taxonomy, governance, lifecycle separation
3. **odoo/odoo** → core runtime conventions

## Path-Level Mapping

| Path | Primary Benchmark | Acceptance Rule |
|------|-------------------|-----------------|
| `addons/oca/` | OCA domain repos | Only OCA/community modules or clean vendorized forks |
| `addons/ipai/` | OCA governance + SAP service boundaries | Each module = one bounded bridge capability |
| `addons/local/` | Last-resort isolation | New entries require written justification |
| `spec/<slug>/constitution.md` | SAP top-level offering | Reads like product charter |
| `spec/<slug>/prd.md` | SAP service overview + decision matrix | Includes decision matrix + phased rollout |
| `spec/<slug>/plan.md` | OpenUpgrade discipline | Has rollout, upgrade impact, regression guards |
| `spec/<slug>/tasks.md` | OCA maintainer workflow | Every task maps to file path + verification |
| `ssot/odoo/addons.manifest.yaml` | OCA apps-store | Every addon declared with source, class, owner |
| `ssot/odoo/oca-baseline.yaml` | OCA domain taxonomy | Grouped by capability domain |
| `ssot/odoo/oca.lock.ce19.json` | OpenUpgrade + OCA branches | Diffable, versioned, tied to Odoo major |
| `docs/product/` | SAP recursive doc tree | Navigable recursively by capability |
| `docs/architecture/` | SAP service categories | Scope, interfaces, deps, ops notes |
| `docs/runbooks/` | SAP operations surface | Every runtime surface has a runbook |
| `.github/workflows/` | OCA bot automation | CI fails on manifest/catalog drift |
| `tests/` | OCA/OpenUpgrade quality gates | Addon discovery + upgrade + smoke coverage |

## Classification Model

Use in `ssot/odoo/addons.manifest.yaml`:

- `core` — first-party Odoo runtime modules
- `oca` — community modules by OCA domain
- `bridge` — thin `ipai_*` integration modules
- `local` — exceptional repo-local modules with expiry
- `l10n` — country/regulatory modules
- `experimental` — non-production, behind flag

## One-Line Rules

- `addons/oca/`: community capability, not custom logic
- `addons/ipai/`: thin bridge, not parity module
- `addons/local/`: exception lane, not default lane
- `spec/`: product contract, not implementation dump
- `ssot/`: machine truth, not prose
- `docs/product/`: publish surface, not internal notes
- `.github/workflows/`: enforce the model, don't just describe it
