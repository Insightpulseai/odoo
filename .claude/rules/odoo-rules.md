---
paths:
  - "addons/**"
  - "odoo18/**"
  - "scripts/odoo*"
  - "docker-compose*"
---

# Odoo Rules

> Odoo CE 18 rules, canonical setup, module naming, testing, OCA workflow, Docker commands, troubleshooting.

---

## Odoo CE 18 Rules (Self-Hosted)

### Prefer

* `addons/` modules + migrations
* `scripts/odoo_*.sh` wrappers
* CI YAML for deploy (GitHub Actions)
* `--stop-after-init` verification commands

### Avoid

* Explaining how to click through Odoo UI for installs or upgrades
* Any references to Odoo.sh, Odoo Online, or Odoo SaaS platforms
* "Go to Settings -> Technical -> ..." guides

### Task Completion

Whenever an Odoo task is requested, generate:

1. The module / config changes
2. The CLI/CI script to install/update modules:
   ```bash
   docker compose exec odoo odoo -d odoo_dev -u module_name --stop-after-init
   ```
3. A verification command:
   ```bash
   curl -s -o /dev/null -w "%{http_code}" http://localhost:8069/web/health
   ```

---

## Canonical Odoo 18 Setup

**Location**: `odoo18/` directory - **Recommended for all AI agent operations**

**Philosophy**: Deterministic, single-database, zero-ambiguity configuration.

| Problem | Old Setup | Canonical Setup |
|---------|-----------|----------------|
| AI Agent Commands | 36 possible combinations | 1 deterministic command |
| Database Targets | 4 databases (all deprecated) | 1 database per env: `odoo_dev`, `odoo_staging`, `odoo` |
| Container Names | Custom | Project-prefixed (odoo18-web-1, odoo18-db-1) |
| Configuration | Docker volumes (not tracked) | Version-controlled (./config/odoo.conf) |
| Database Selector | Enabled (UI confusion) | Disabled (list_db = False) |

**Quick Start:**
```bash
cd odoo18
docker compose up -d                              # Start stack
docker compose exec -T web odoo -d odoo_dev -i base   # Install module
./scripts/backup_db.sh                            # Backup database
```

**Key Features:**
- Single database target per environment (`db_name = odoo_dev` / `odoo_staging` / `odoo`)
- No database selector (`list_db = False`)
- File-based secrets (no hardcoded passwords)
- Health checks (PostgreSQL guards web startup)
- No container_name (allows scaling/isolation)
- Idempotent backup script
- Version-controlled config

---

## IPAI Module Naming Convention

All custom modules use the `ipai_` prefix organized by domain:

| Domain | Prefix Pattern | Examples |
|--------|---------------|----------|
| AI/Agents | `ipai_ai_*`, `ipai_agent_*` | `ipai_ai_core`, `ipai_ai_copilot`, `ipai_agent`, `ipai_ai_widget` |
| Finance | `ipai_finance_*` | `ipai_finance_ppm`, `ipai_finance_close_seed`, `ipai_finance_tax_return`, `ipai_finance_workflow` |
| Platform | `ipai_platform_*` | `ipai_platform_workflow`, `ipai_platform_audit`, `ipai_platform_approvals` |
| Workspace | `ipai_workspace_*` | `ipai_workspace_core` |
| Studio | `ipai_dev_studio_*`, `ipai_studio_*` | `ipai_dev_studio_base`, `ipai_studio_ai` |
| Industry | `ipai_industry_*` | `ipai_industry_marketing_agency`, `ipai_industry_accounting_firm` |
| WorkOS | `ipai_workos_*` | `ipai_workos_core`, `ipai_workos_blocks`, `ipai_workos_canvas` |
| Theme/UI | `ipai_theme_*`, `ipai_web_*`, `ipai_ui_*` | `ipai_theme_tbwa_backend`, `ipai_ui_brand_tokens` |
| Integrations | `ipai_*_connector` | `ipai_slack_connector`, `ipai_superset_connector`, `ipai_ops_connector`, `ipai_pulser_connector` |
| HR | `ipai_hr_*` | `ipai_hr_payroll_ph`, `ipai_hr_expense_liquidation` |
| BIR Compliance | `ipai_bir_*` | `ipai_bir_tax_compliance`, `ipai_bir_notifications`, `ipai_bir_plane_sync` |
| Mail | `ipai_mail_*`, `ipai_mailgun_*`, `ipai_zoho_*` | `ipai_mailgun_smtp`, `ipai_zoho_mail`, `ipai_mail_bridge_zoho` |
| Design | `ipai_design_*` | `ipai_design_system`, `ipai_design_system_apps_sdk` |
| LLM | `ipai_llm_*` | `ipai_llm_supabase_bridge` |

---

## Key Module Hierarchy (Verified 2026-03-08)

Based on actual `__manifest__.py` dependency analysis:

```
Layer 0 — Independent (no IPAI deps, depend only on base Odoo):
  ipai_foundation              # Foundation layer (Live)
  ipai_ai_core                 # AI core framework (Live, has tests)
  ipai_ai_widget               # AI widget (Live, has tests)
  ipai_enterprise_bridge       # EE parity bridge (Live, has tests)
  ipai_finance_ppm             # Finance PPM (Live)
  ipai_helpdesk                # Helpdesk (Live)
  ipai_hr_expense_liquidation  # HR expense liquidation (Live, has tests)
  ipai_llm_supabase_bridge     # LLM Supabase bridge (Live, has tests)

Layer 1 — Single IPAI dependency:
  ipai_ai_copilot              # -> ipai_ai_widget (Live)
  ipai_agent                   # -> ipai_hr_expense_liquidation (Live, has tests)

Layer 2 — Multiple IPAI dependencies:
  ipai_workspace_core          # -> ipai_foundation + ipai_ai_copilot (Live, has tests, app=True)

Deprecated (installable: False):
  ipai_ai_agent_builder        # Migrated to ipai_enterprise_bridge
  ipai_ai_tools                # Migrated to ipai_enterprise_bridge
  ipai_ai_agents_ui            # Not installable (has tests)
```

---

## Test Coverage (8 of 69 modules have tests)

| Module | Test Files |
|--------|-----------|
| `ipai_ai_core` | `test_ai_core.py` |
| `ipai_ai_widget` | `test_ai_widget.py` |
| `ipai_agent` | `test_agent.py` |
| `ipai_enterprise_bridge` | `test_enterprise_bridge.py` |
| `ipai_hr_expense_liquidation` | `test_form_no.py`, `test_qweb.py` |
| `ipai_llm_supabase_bridge` | `test_install_smoke.py` |
| `ipai_workspace_core` | `test_workspace.py` |
| `ipai_ai_agents_ui` | `test_ai_agents_controller.py` (not installable) |

---

## Module Decision Framework

```
BUILD CUSTOM MODULE WHEN:

  NOT PAYING + NEED FEATURE -> Replace it
     Odoo EE features -> ipai_enterprise_parity

  PAYING + WANT MAX ROI -> Build connector
     Vercel Observability Plus -> ipai_connector_vercel

  NOT PAYING + WORKS AS-IS -> No module needed
     Supabase free tier -> Just use SDK/API directly
     n8n self-hosted -> Just webhooks, no module
```

| Service | Paying? | Module | Purpose |
|---------|---------|--------|---------|
| Odoo EE | No | `ipai_enterprise_parity` | Replace EE-only features |
| Vercel Observability+ | Yes ($10/mo) | `ipai_connector_vercel` | Maximize ROI |
| Supabase | No (free/pro) | None | Use SDK directly |
| n8n | No (self-hosted) | None | Just webhooks |

---

## OCA-Style Workflow

### Non-Negotiables

- **Do NOT run** `copier` in the repo root (it will overwrite structure).
- Use `/tmp/oca-template/` to generate templates and **selectively port** only the needed files.
- New custom modules live under: `addons/ipai/<module_name>/`
- OCA repos cloned under: `addons/oca/*/` are **NOT tracked** (only keep base marker files per `.gitignore`).

### Standard Tooling (Must Stay Green)

```bash
# Pre-commit
pip install -r requirements.txt
pre-commit install
pre-commit run -a

# Local verification (mirror CI)
./scripts/verify_local.sh
```

### Fast Module Scaffolding (mrbob)

```bash
pipx install mrbob
pipx inject mrbob bobtemplates.odoo

# Create addon (then move under addons/ipai/)
mrbob bobtemplates.odoo:addon

# Create model scaffolding inside addon
mrbob bobtemplates.odoo:model
```

---

## Docker Commands

### Development

```bash
# Start core services
docker compose up -d postgres odoo-core

# Run init profiles (first-time setup)
docker compose --profile ce-init up    # Install CE modules
docker compose --profile init up       # Install IPAI modules

# View logs
docker compose logs -f odoo-core

# Restart service
docker compose restart odoo
```

### Database Access

```bash
# Connect to PostgreSQL
docker compose exec db psql -U odoo -d odoo_dev

# Backup database
docker compose exec db pg_dump -U odoo odoo_dev > backup.sql
```

---

## Key Scripts Reference

| Script | Purpose |
|--------|---------|
| `scripts/deploy-odoo-modules.sh` | Deploy IPAI modules to Odoo |
| `scripts/repo_health.sh` | Verify repository structure |
| `scripts/spec_validate.sh` | Validate spec bundle completeness |
| `scripts/ci_local.sh` | Run full local CI suite |
| `scripts/verify_local.sh` | OCA-style local verification (mirrors CI) |
| `scripts/ci/run_odoo_tests.sh` | Execute Odoo unit tests |
| `scripts/ci/module_drift_gate.sh` | Check for module drift |
| `scripts/ce_oca_audit.py` | Comprehensive OCA/CE audit |
| `scripts/generate_odoo_dbml.py` | Generate data model artifacts |
| `scripts/gen_repo_tree.sh` | Auto-generate repo structure docs |
| `scripts/web_sandbox_verify.sh` | Claude Code Web sandbox verification |
| `scripts/db_verify.sh` | Database health verification script |

---

## Data Model Artifacts

Located in `docs/data-model/`:

| File | Format | Purpose |
|------|--------|---------|
| `ODOO_CANONICAL_SCHEMA.dbml` | DBML | Schema for dbdiagram.io |
| `ODOO_ERD.mmd` | Mermaid | Entity-relationship diagram |
| `ODOO_ERD.puml` | PlantUML | UML diagram |
| `ODOO_ORM_MAP.md` | Markdown | Comprehensive ORM field mapping |
| `ODOO_MODEL_INDEX.json` | JSON | Machine-readable model index |

Regenerate with:
```bash
python scripts/generate_odoo_dbml.py
```

---

## Testing

### Odoo Tests

```bash
# Run all tests
./scripts/ci/run_odoo_tests.sh

# Run tests for specific module
./scripts/ci/run_odoo_tests.sh ipai_finance_ppm

# Smoke tests
./scripts/ci_smoke_test.sh
```

### Python Linting

```bash
black --check addons/ipai/
isort --check addons/ipai/
flake8 addons/ipai/
python3 -m py_compile addons/ipai/**/*.py
```

### Node.js

```bash
npm run lint
npm run typecheck
npm run build
```

---

## Troubleshooting

### Common Issues

**Module not found**
```bash
# Ensure module is in addons path
docker compose exec odoo ls /mnt/extra-addons/ipai/

# Update module list
docker compose exec odoo odoo -d odoo_dev -u base
```

**Database connection issues**
```bash
# Check PostgreSQL status
docker compose ps postgres
docker compose logs postgres
```

**Permission errors (SCSS compilation failures)**
```bash
# Symptom: "Style compilation failed" errors in Odoo
# Root cause: Addons owned by wrong user

# Auto-fix permissions (recommended)
./scripts/verify-addon-permissions.sh
```

---

## Enabled Skills

Agent capabilities enforced via repo-level skill contracts:

| Skill | Purpose | Contract |
|-------|---------|----------|
| Web Session Command Bridge | Ensures all changes produce CLI-ready commands for Claude Web/CI/Docker | [skills/web-session-command-bridge/skill.md](skills/web-session-command-bridge/skill.md) |

### Skill Enforcement

Skills are enforced via CI workflow `.github/workflows/skill-enforce.yml`.

```bash
./scripts/skill_web_session_bridge.sh
```

---

*Last updated: 2026-03-16*
