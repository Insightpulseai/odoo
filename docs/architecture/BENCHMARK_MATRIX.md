# Benchmark Matrix — Consolidated

## Four-Tier Benchmark Hierarchy

1. **SAP on Azure** → product surface, decision matrices, ops-as-product
2. **OCA** → addon taxonomy, governance, lifecycle separation, manifest discipline
3. **Odoo.sh containers** → runtime/container contract, filesystem layout, debug procedures
4. **odoo/odoo** → core composition, addon loading conventions

## Path-Level Mapping

| Path | Primary Benchmark | Secondary | Hard Rule |
|------|-------------------|-----------|-----------|
| `addons/oca/` | OCA domain repos | odoo/odoo addon loading | Only OCA/community modules or clean vendorized forks |
| `addons/ipai/` | SAP service-category model | Odoo.sh runtime contract | One module = one bridge capability + one runtime contract |
| `addons/local/` | Exception lane | odoo/odoo as warning | Every entry needs written justification |
| `spec/<slug>/constitution.md` | SAP top-level offering | — | No implementation detail dump |
| `spec/<slug>/prd.md` | SAP decision/support model | OCA domain taxonomy | Must include decision matrix + phased path |
| `spec/<slug>/plan.md` | OCA maintainer/OpenUpgrade | Odoo.sh operational commands | Must separate build, rollout, upgrade, rollback |
| `spec/<slug>/tasks.md` | OCA maintainer workflow | — | Every task maps to files + verification |
| `docs/product/<product>/index.md` | SAP overview page | — | Publish surface, not internal README |
| `docs/product/<product>/*/overview.md` | SAP recursive doc tree | — | Every publishable capability gets its own page |
| `docs/product/<product>/*/quickstart.md` | SAP quickstart | Odoo.sh shell/install | Must be runnable and bounded |
| `docs/product/<product>/*/how-to.md` | SAP how-to | Odoo.sh runtime/logs | Must point to observable evidence |
| `docs/product/<product>/*/faq.md` | SAP FAQ model | — | Only durable questions |
| `docs/architecture/runtime-container-contract.md` | Odoo.sh containers | odoo/odoo layout | Runtime contract must be machine-checkable |
| `docs/architecture/addon-taxonomy.md` | OCA | odoo/odoo | Every addon class must have ownership + lifecycle rules |
| `docs/runbooks/*` | Odoo.sh operational contract | SAP ops-as-product | Every runtime surface must have a runbook |
| `ssot/odoo/addons.manifest.yaml` | OCA apps-store | OCA maintainer tooling | No addon known only by directory name |
| `ssot/odoo/oca-baseline.yaml` | OCA domain taxonomy | — | Group by capability domain + install intent |
| `ssot/odoo/oca.lock.ce19.json` | OCA/OpenUpgrade lifecycle | — | Lock must be versioned and diffable |
| `ssot/odoo/runtime_contract.yaml` | Odoo.sh containers | — | Source of truth for runtime parity checks |
| `.github/workflows/addon-governance.yml` | OCA maintainer-tools | OCA apps-store | CI fails on manifest/catalog drift |
| `.github/workflows/runtime-contract.yml` | Odoo.sh containers | — | CI must prove paths, not just builds |
| `tests/test_addon_inventory.py` | OCA manifest discipline | odoo/odoo | No unmanaged addon directories |
| `tests/test_runtime_contract.py` | Odoo.sh containers | — | Fails if addon-path parity not provable |

## Classification Model

Use in `ssot/odoo/addons.manifest.yaml`:

- `core` — first-party Odoo runtime modules
- `oca` — community modules by OCA domain
- `bridge` — thin `ipai_*` integration modules
- `local` — exceptional repo-local modules with expiry
- `l10n` — country/regulatory modules
- `experimental` — non-production, behind flag

## One-Line Doctrine Per Bucket

- `addons/oca/`: community capability plane
- `addons/ipai/`: thin product bridge plane
- `addons/local/`: exception plane
- `spec/`: product contract plane
- `docs/product/`: publish plane
- `docs/architecture/`: technical truth plane
- `ssot/odoo/`: machine-governed truth plane
- `.github/workflows/`: enforcement plane
- `tests/`: parity proof plane

## Minimal Repo Changes to Align

### Add

- `docs/product/odoo-copilot-on-azure/index.md`
- `docs/product/odoo-copilot-on-azure/runtime-overview.md`
- `docs/product/odoo-copilot-on-azure/grounding-search.md`
- `docs/product/odoo-copilot-on-azure/operations.md`
- `docs/product/odoo-copilot-on-azure/security-governance.md`
- `docs/product/odoo-copilot-on-azure/changelog.md`
- `docs/architecture/runtime-container-contract.md`
- `docs/architecture/addon-taxonomy.md`
- `ssot/odoo/runtime_contract.yaml`

### Enforce

- Every addon classified in `ssot/odoo/addons.manifest.yaml`
- Every `ipai_*` module mapped to one bounded bridge capability
- Every publishable surface documented under `docs/product/`
- Every runtime surface covered by runbook + parity test
