# InsightPulse Odoo CE – ERP Platform (CE + OCA + IPAI)

[![odoo-ce-ci](https://github.com/jgtolentino/odoo-ce/actions/workflows/ci-odoo-ce.yml/badge.svg)](https://github.com/jgtolentino/odoo-ce/actions/workflows/ci-odoo-ce.yml)

Self-hosted **Odoo 18 Community Edition** + **OCA** stack with InsightPulseAI custom modules (IPAI) for:
- PH Expense & Travel (Concur replacement)
- Equipment booking (Cheqroom parity)
- Finance month-end close + PH tax filing task automation
- Canonical, versioned data-model artifacts (DBML/ERD/ORM maps) with CI drift gates

Production URL: https://erp.insightpulseai.net

---

## Key Constraints (Non-negotiable)

- ✅ **CE + OCA only** (no Enterprise modules, no IAP dependencies)
- ✅ **No odoo.com upsells** (branding/links rewired)
- ✅ **Self-hosted** via Docker/Kubernetes (DigitalOcean supported)
- ✅ **Deterministic docs + seeds** (generated artifacts are versioned + drift-checked)

---

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

## Modules (IPAI)

### Expense & Travel (PH)
- **Module**: `ipai_expense` (in `addons/ipai/`)
- Replaces Concur-style flows: requests → approvals → finance posting

### Equipment Booking
- **Module**: `ipai_equipment` (in `addons/ipai/`)
- Cheqroom parity MVP: catalog, bookings, check-in/out, incidents

### Finance Close Seed Data
- **Module**: `ipai_finance_close_seed` (in `addons/`)
- Seeds:
  - Projects: `BIR Tax Filing`, `Month-End Close Template`, etc.
  - Task category tags
  - PH holidays (calendar leaves) for working-day computations
  - Month-end close template tasks + BIR filing tasks

### Finance PPM & Month-End
- **Modules**: `ipai_finance_ppm`, `ipai_finance_month_end`, `ipai_ppm_monthly_close`
- Project Portfolio Management for finance teams
- Month-end close orchestration and task tracking

### CE Cleaner & Branding
- **Modules**: `ipai_ce_cleaner`, `ipai_ce_branding`
- Hides "Upgrade to Enterprise" banners
- Removes IAP credit/SMS/email upsell menus
- Rewires help links to InsightPulse docs or OCA

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

## Install IPAI Finance Close Module

### Install seed

```bash
./odoo-bin -d <db> -i ipai_finance_close_seed --stop-after-init
```

### Verify seed counts

```bash
./odoo-bin shell -d <db> <<'PY'
P=env['project.project'].sudo()
T=env['project.task'].sudo()
print("Projects:", P.search_count([]))
print("Tasks:", T.search_count([]))
PY
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
- Docs: https://docs.insightpulseai.net/erp
