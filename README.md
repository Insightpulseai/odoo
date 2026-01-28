# InsightPulse Odoo CE – ERP Platform (CE + OCA + IPAI)

[![odoo-ce-ci](https://github.com/jgtolentino/odoo-ce/actions/workflows/ci-odoo-ce.yml/badge.svg)](https://github.com/jgtolentino/odoo-ce/actions/workflows/ci-odoo-ce.yml)

Self-hosted **Odoo 18 Community Edition** + **OCA** stack with InsightPulseAI custom modules (IPAI) for:
- PH expense & travel management
- Equipment booking & inventory
- Finance month-end close and PH BIR tax filing task automation (Finance PPM)
- Canonical, versioned data-model artifacts (DBML / ERD / ORM maps) with CI-enforced drift gates

**Production URL:** https://erp.insightpulseai.net
**Documentation:** https://jgtolentino.github.io/odoo-ce/

---

## Quick Start

**Three canonical environments. See [SANDBOX.md](./SANDBOX.md) for complete documentation.**

```bash
# Local dev sandbox (default)
cd sandbox/dev && docker compose up -d

# Prod-connection sandbox (DO Managed Postgres)
cd sandbox/dev && docker compose -f docker-compose.production.yml --env-file .env.production up -d

# Production deploy (droplet only)
cd deploy && docker compose -f docker-compose.prod.yml up -d
```

---

## Key Constraints (Non-negotiable)

- ✅ **CE + OCA only** (no Enterprise modules, no IAP dependencies)
- ✅ **No odoo.com upsells** (branding/links rewired)
- ✅ **Self-hosted** via Docker/Kubernetes (DigitalOcean supported)
- ✅ **Deterministic docs + seeds** (generated artifacts are versioned + drift-checked)

---

<!-- CURRENT_STATE:BEGIN -->

## Current State (Authoritative)

**Canonical IPAI strategy (single-bridge + vertical bundles):**

| Module | Role | Description |
|--------|------|-------------|
| `ipai_enterprise_bridge` | Bridge | Thin cross-cutting layer: config, approvals, AI/infra integration, shared mixins |
| `ipai_scout_bundle` | Vertical | Meta-bundle for Scout retail ops + analytics (depends-only, no business logic) |
| `ipai_ces_bundle` | Vertical | Meta-bundle for CES creative effectiveness ops (depends-only, no business logic) |

**Detected in repo:**

- Canonical modules present: `ipai_enterprise_bridge`
- Other IPAI modules (feature/legacy): 66
- Non-IPAI modules at addons root: 1

**Policy:**
- Only canonical modules define the platform surface area
- Feature modules must be explicitly referenced by a bundle dependency
- Deprecated modules should be moved to `addons/_deprecated/` and blocked by CI

**Install canonical stack:**
```bash
docker compose exec -T odoo odoo -d odoo_dev -i ipai_enterprise_bridge --stop-after-init
docker compose exec -T odoo odoo -d odoo_dev -i ipai_scout_bundle --stop-after-init
docker compose exec -T odoo odoo -d odoo_dev -i ipai_ces_bundle --stop-after-init
```

<!-- CURRENT_STATE:END -->

## Repository Layout

```
odoo-ce/
├── addons/                    # Custom InsightPulse modules
│   ├── ipai/                  # IPAI namespace (nested modules)
│   │   ├── ipai_expense/      # PH expense & travel workflows
│   │   ├── ipai_equipment/    # Equipment booking system
│   │   ├── ipai_ce_cleaner/   # Enterprise/IAP removal
│   │   ├── ipai_finance_*     # Finance PPM, BIR compliance, month-end
│   │   ├── ipai_ppm*/         # Project Portfolio Management
│   │   └── ...                # Additional IPAI modules
│   ├── ipai_finance_close_seed/   # Finance close seed data
│   ├── ipai_*                 # Flat IPAI modules (various)
│   └── ...
├── oca/                       # OCA community addons (submodules)
├── deploy/                    # Deployment configurations
│   ├── docker-compose.yml     # Docker Compose stack
│   ├── odoo.conf              # Odoo CE configuration
│   └── nginx/                 # Nginx reverse proxy configs
├── docs/                      # Documentation
│   └── data-model/            # Canonical DBML/ERD/ORM maps + JSON index
├── scripts/                   # Deterministic generators + automation
├── spec/                      # Spec bundles (constitution, PRD, plan, tasks)
├── .github/workflows/         # CI/CD guardrails + drift gates
├── spec.md                    # Project specification
├── plan.md                    # Implementation plan
└── tasks.md                   # Task checklist
```

---

## Module Architecture

### Canonical Stack (Install These)

The platform surface is defined by **three canonical modules** only:

```
ipai_enterprise_bridge     # Base layer: config, approvals, AI/infra glue
    ├── ipai_scout_bundle  # Retail vertical (POS, inventory, sales)
    └── ipai_ces_bundle    # Creative services vertical (projects, timesheets)
```

Installing a bundle installs all its dependencies transitively.

### Bridge Module

**`ipai_enterprise_bridge`** — Thin glue layer for CE+OCA parity:
- Configuration policies and settings
- Approval tier validation mixins
- AI/infrastructure connector stubs
- Shared security groups

### Vertical Bundles

| Bundle | Focus | CE Modules Included |
|--------|-------|---------------------|
| `ipai_scout_bundle` | Retail ops | `sale_management`, `purchase`, `stock`, `point_of_sale`, `account` |
| `ipai_ces_bundle` | Creative ops | `project`, `hr`, `hr_timesheet`, `mail`, `portal` |

### Feature Modules (Optional)

Feature modules are **not part of the canonical surface**. They must be:
1. Explicitly depended on by a bundle, OR
2. Installed manually for specific use cases

| Category | Examples | Purpose |
|----------|----------|---------|
| Finance | `ipai_finance_ppm`, `ipai_finance_month_end`, `ipai_bir_compliance` | PH tax, month-end close |
| Expense | `ipai_expense`, `ipai_expense_ocr` | PH expense workflows |
| Equipment | `ipai_equipment` | Cheqroom-style booking |
| AI | `ipai_ai_core`, `ipai_ai_agents` | AI platform integrations |
| Branding | `ipai_ce_cleaner`, `ipai_ce_branding` | Remove Enterprise upsells |

### Deprecated Modules

Modules that are no longer maintained should be moved to `addons/_deprecated/` and blocked by CI.

---

## Quick Start (Production - DigitalOcean)

Recommended for fresh Ubuntu 22.04/24.04 droplet.

```bash
curl -fsSL https://raw.githubusercontent.com/jgtolentino/odoo-ce/main/deploy_m1.sh.template -o deploy_m1.sh
chmod +x deploy_m1.sh
sudo ./deploy_m1.sh
```

Access:
- https://erp.insightpulseai.net/web
- Secrets:

```bash
cat /opt/odoo-ce/deploy/.env
tail -f /var/log/odoo_deploy.log
```

---

## Quick Start (Local Dev)

```bash
git clone https://github.com/jgtolentino/odoo-ce.git
cd odoo-ce
cd deploy
docker compose up -d
docker compose logs -f odoo
```

---

## Install IPAI Modules

### Install canonical stack (recommended)

```bash
# Install bridge first (required by all bundles)
docker compose exec -T odoo odoo -d odoo_dev -i ipai_enterprise_bridge --stop-after-init

# Install verticals as needed
docker compose exec -T odoo odoo -d odoo_dev -i ipai_scout_bundle --stop-after-init    # Retail
docker compose exec -T odoo odoo -d odoo_dev -i ipai_ces_bundle --stop-after-init      # Creative
```

### Install optional feature modules

```bash
# Finance close seed data
docker compose exec -T odoo odoo -d odoo_dev -i ipai_finance_close_seed --stop-after-init

# Other feature modules as needed
docker compose exec -T odoo odoo -d odoo_dev -i ipai_expense --stop-after-init
docker compose exec -T odoo odoo -d odoo_dev -i ipai_equipment --stop-after-init
```

### Verify installation

```bash
docker compose exec -T db psql -U odoo -d odoo_dev -c "
SELECT name, state FROM ir_module_module
WHERE name IN ('ipai_enterprise_bridge','ipai_scout_bundle','ipai_ces_bundle')
ORDER BY name;"
```

---

## Canonical Data Model (DBML / ERD / ORM maps)

Canonical, machine-readable outputs live in:

- `docs/data-model/`
  - `ODOO_CANONICAL_SCHEMA.dbml` — DBML schema for dbdiagram.io
  - `ODOO_ERD.mmd` — Mermaid ER diagram
  - `ODOO_ERD.puml` — PlantUML ER diagram
  - `ODOO_ORM_MAP.md` — ORM map linking models, tables, fields
  - `ODOO_MODULE_DELTAS.md` — Per-module schema deltas
  - `ODOO_MODEL_INDEX.json` — Machine-readable index

Regenerate deterministically:

```bash
python scripts/generate_odoo_dbml.py
git diff --exit-code docs/data-model/
```

---

## Deterministic Seed Generator (from Excel)

If you update the source Excel or want to refresh seed artifacts:

```bash
python scripts/seed_finance_close_from_xlsx.py
git diff --exit-code addons/ipai_finance_close_seed
```

---

## CI/CD Guardrails (What must stay green)

CI enforces:

- **Odoo 18 CE / OCA CI** — Lint, static checks, and unit tests
- **guardrails** — Block Enterprise modules and odoo.com links
- **repo-structure** — Repo tree in spec.md must match generator
- **data-model-drift** — `docs/data-model/` must match generator output
- **seed-finance-close-drift** — `addons/ipai_finance_close_seed` must match `seed_finance_close_from_xlsx.py` output
- **spec-kit-enforce** — Spec bundles must have complete 4-file structure
- **infra-validate** — Infrastructure template validation

### Key workflows:

| Workflow | Purpose |
|----------|---------|
| `ci-odoo-ce.yml` | Main guardrails + data-model drift |
| `repo-structure.yml` | Repo tree consistency |
| `spec-kit-enforce.yml` | Spec bundle validation |
| `infra-validate.yml` | Infrastructure templates |
| `auto-sitemap-tree.yml` | Auto-update SITEMAP.md/TREE.md |

If CI fails, reproduce locally by running the same generator commands + `git diff --exit-code` checks above.

---

## Docs

- `spec.md` — Project spec / repo snapshot
- `plan.md` — Implementation plan
- `tasks.md` — Task checklist
- `docs/` — Architecture + deployment docs
- `docs/data-model/` — Canonical schema outputs

---

## License

- IPAI modules: **AGPL-3**
- OCA modules: See each upstream repo/license

---

## Support

- Issues: [GitHub Issues](https://github.com/jgtolentino/odoo-ce/issues)
- Docs: https://jgtolentino.github.io/odoo-ce/
