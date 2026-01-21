# OCA Installation Guide (Canonical)

**Repository**: `odoo-ce` (jgtolentino/odoo-ce)
**Odoo Series**: 18.0
**Last Updated**: 2026-01-20
**Status**: Canonical guide for OCA module management

---

## TL;DR

**Do NOT install "all OCA" in one Odoo instance.** OCA is a large, multi-repo ecosystem; pulling everything creates dependency conflicts, overlapping features, and maintenance risk.

**Correct pattern**: Odoo CE core + **curated OCA 18.0 baseline layer** + domain-specific repos as needed.

---

## 1. Philosophy: Curated, Not Comprehensive

### Why NOT to Install All OCA

| Risk | Impact |
|------|--------|
| **Dependency conflicts** | Multiple OCA modules may provide overlapping functionality |
| **Upgrade friction** | More modules = more migration work per Odoo version |
| **Module conflicts** | Some OCA modules aren't compatible with each other |
| **Maintenance overhead** | Each module needs testing, security updates, compatibility checks |
| **Performance impact** | Unused modules still consume resources during module list scanning |

### Recommended Approach

```text
Config → OCA → Delta (ipai_*)

1. Config: Use Odoo's built-in configuration first
2. OCA: Use vetted OCA community modules second (curated list)
3. Delta: Only create ipai_* modules for truly custom needs
```

---

## 2. Curated OCA Repository Stack

This repository uses a **tiered approach** defined in `oca.lock.json`. Install by tier, starting from Tier 0 (Foundation).

### Tier Overview

| Tier | Name | Install Order | Repositories |
|------|------|---------------|--------------|
| 0 | Foundation | 1 | server-tools, server-ux, server-backend |
| 1 | Platform UX | 2 | web |
| 2 | Background Processing | 3 | queue |
| 3 | Calendar | 4 | calendar |
| 4 | Reporting & BI | 5 | reporting-engine, mis-builder, account-financial-reporting, account-financial-tools |
| 5 | Spreadsheet | 6 | spreadsheet |
| 6 | Documents | 7 | knowledge, dms |
| 7 | API Layer | 8 | rest-framework |
| 8 | Mail & Audit | 9 | social |
| 9 | Workflows | 10 | account-reconcile, purchase-workflow, sale-workflow, hr-expense, project, contract, timesheet |
| 10 | Connectors | 11 | connector, storage |
| 11 | AI/ML | 12 | ai |
| 12 | Localization | 13 | l10n-philippines |

### Essential Stack for Base + Sales + Accounting

**Minimum recommended** for most deployments:

```text
Foundation (Tier 0):
├── server-tools    → base_exception, auditlog, module_auto_update
├── server-ux       → date_range, base_tier_validation
└── server-backend  → base_user_role

Platform UX (Tier 1):
└── web             → web_responsive, web_dialog_size

Background Jobs (Tier 2):
└── queue           → queue_job, queue_job_cron

Sales (Tier 9):
└── sale-workflow   → sale_order_type, sale_order_line_sequence

Accounting (Tier 4 + 9):
├── account-financial-tools     → account_lock_date, account_fiscal_year
├── account-financial-reporting → account_financial_report
└── account-reconcile           → account_reconcile_oca
```

---

## 3. Repository Configuration

### Option A: Git Submodules (Recommended for CI/Production)

Add OCA repos as pinned submodules to `external-src/` directory:

```bash
set -euo pipefail

mkdir -p external-src && cd external-src

# Foundation (Tier 0)
git submodule add -f -b 18.0 https://github.com/OCA/server-tools.git server-tools
git submodule add -f -b 18.0 https://github.com/OCA/server-ux.git server-ux
git submodule add -f -b 18.0 https://github.com/OCA/server-backend.git server-backend

# Platform UX (Tier 1)
git submodule add -f -b 18.0 https://github.com/OCA/web.git web

# Background Jobs (Tier 2)
git submodule add -f -b 18.0 https://github.com/OCA/queue.git queue

# Sales (Tier 9)
git submodule add -f -b 18.0 https://github.com/OCA/sale-workflow.git sale-workflow

# Accounting (Tier 4)
git submodule add -f -b 18.0 https://github.com/OCA/account-financial-tools.git account-financial-tools
git submodule add -f -b 18.0 https://github.com/OCA/account-financial-reporting.git account-financial-reporting

# Accounting Reconcile (Tier 9)
git submodule add -f -b 18.0 https://github.com/OCA/account-reconcile.git account-reconcile

cd ..
git add .gitmodules external-src
git commit -m "chore(oca): add curated OCA 18.0 repos (base/sales/accounting)"
```

### Option B: Shallow Clone (Development/Quick Setup)

For local development without tracking submodules:

```bash
set -euo pipefail

mkdir -p external-src && cd external-src

# Clone with depth=1 for fast downloads
git clone -b 18.0 --depth=1 https://github.com/OCA/server-tools.git
git clone -b 18.0 --depth=1 https://github.com/OCA/server-ux.git
git clone -b 18.0 --depth=1 https://github.com/OCA/server-backend.git
git clone -b 18.0 --depth=1 https://github.com/OCA/web.git
git clone -b 18.0 --depth=1 https://github.com/OCA/queue.git
git clone -b 18.0 --depth=1 https://github.com/OCA/sale-workflow.git
git clone -b 18.0 --depth=1 https://github.com/OCA/account-financial-tools.git
git clone -b 18.0 --depth=1 https://github.com/OCA/account-financial-reporting.git
git clone -b 18.0 --depth=1 https://github.com/OCA/account-reconcile.git
```

---

## 4. Addons Path Configuration

### Production Configuration

Update `odoo.conf` to include OCA repos:

```ini
[options]
; Core Odoo addons (first)
; Custom IPAI addons (second)
; OCA addons (third)
addons_path =
    /usr/lib/python3/dist-packages/odoo/addons,
    /mnt/extra-addons/ipai,
    /mnt/extra-addons/oca/server-tools,
    /mnt/extra-addons/oca/server-ux,
    /mnt/extra-addons/oca/server-backend,
    /mnt/extra-addons/oca/web,
    /mnt/extra-addons/oca/queue,
    /mnt/extra-addons/oca/sale-workflow,
    /mnt/extra-addons/oca/account-financial-tools,
    /mnt/extra-addons/oca/account-financial-reporting,
    /mnt/extra-addons/oca/account-reconcile
```

### Docker Compose Configuration

Mount OCA repos into container:

```yaml
# docker-compose.yml
services:
  odoo-core:
    image: odoo:18
    volumes:
      - ./addons/ipai:/mnt/extra-addons/ipai:ro
      - ./external-src/server-tools:/mnt/extra-addons/oca/server-tools:ro
      - ./external-src/server-ux:/mnt/extra-addons/oca/server-ux:ro
      - ./external-src/server-backend:/mnt/extra-addons/oca/server-backend:ro
      - ./external-src/web:/mnt/extra-addons/oca/web:ro
      - ./external-src/queue:/mnt/extra-addons/oca/queue:ro
      - ./external-src/sale-workflow:/mnt/extra-addons/oca/sale-workflow:ro
      - ./external-src/account-financial-tools:/mnt/extra-addons/oca/account-financial-tools:ro
      - ./external-src/account-financial-reporting:/mnt/extra-addons/oca/account-financial-reporting:ro
      - ./external-src/account-reconcile:/mnt/extra-addons/oca/account-reconcile:ro
```

---

## 5. Module Installation

### Verification: Odoo Detects Modules

Before installing, verify Odoo can see the modules:

```bash
# Check module discovery (container)
docker exec -it odoo-core odoo --version

# List available OCA modules in database
docker exec -it postgres psql -U odoo -d odoo_core -c "
  SELECT name, state
  FROM ir_module_module
  WHERE name IN (
    'queue_job',
    'server_environment',
    'base_exception',
    'date_range',
    'base_user_role',
    'web_responsive',
    'account_financial_report',
    'account_reconcile_oca'
  )
  ORDER BY name;
"
```

### Foundation Install (Tier 0-2)

Install in dependency order:

```bash
# Tier 0: Foundation
docker exec -it odoo-core odoo -d odoo_core \
  -i base_exception,base_technical_user,auditlog \
  --stop-after-init

docker exec -it odoo-core odoo -d odoo_core \
  -i date_range,base_tier_validation \
  --stop-after-init

docker exec -it odoo-core odoo -d odoo_core \
  -i base_user_role \
  --stop-after-init

# Tier 1: Platform UX
docker exec -it odoo-core odoo -d odoo_core \
  -i web_responsive,web_dialog_size \
  --stop-after-init

# Tier 2: Background Jobs
docker exec -it odoo-core odoo -d odoo_core \
  -i queue_job,queue_job_cron \
  --stop-after-init
```

### Accounting Stack Install (Tier 4 + 9)

```bash
# Tier 4: Financial Tools
docker exec -it odoo-core odoo -d odoo_core \
  -i account_lock_date,account_fiscal_year,account_move_name_sequence \
  --stop-after-init

# Tier 4: Financial Reporting
docker exec -it odoo-core odoo -d odoo_core \
  -i account_financial_report \
  --stop-after-init

# Tier 9: Reconciliation
docker exec -it odoo-core odoo -d odoo_core \
  -i account_reconcile_oca \
  --stop-after-init
```

### Sales Stack Install (Tier 9)

```bash
# Tier 9: Sales Workflow
docker exec -it odoo-core odoo -d odoo_core \
  -i sale_order_type,sale_order_line_sequence \
  --stop-after-init
```

---

## 6. Verification Commands

### Post-Installation Verification

```bash
# Verify all target modules installed
docker exec -it postgres psql -U odoo -d odoo_core -c "
  SELECT name, state, latest_version
  FROM ir_module_module
  WHERE name IN (
    'base_exception',
    'date_range',
    'base_user_role',
    'web_responsive',
    'queue_job',
    'account_lock_date',
    'account_financial_report',
    'sale_order_type'
  )
  ORDER BY name;
"

# Expected: All modules should show state = 'installed'
```

### Health Check

```bash
# Verify Odoo is running
curl -s -o /dev/null -w "%{http_code}" http://localhost:8069/web/health

# Expected: 200

# Check for startup errors
docker logs odoo-core --tail=50 | grep -i error
```

---

## 7. Deployment Workflow

### Deploy Pattern (Safe)

```bash
# 1. Update submodules to pinned revisions
git submodule sync --recursive
git submodule update --init --recursive

# 2. Restart Odoo (compose)
docker compose up -d --force-recreate odoo-core

# 3. Run headless update if needed
docker exec -it odoo-core odoo -d odoo_core \
  -u base_exception,queue_job \
  --stop-after-init

# 4. Verify health
curl -s -o /dev/null -w "%{http_code}" http://localhost:8069/web/login
```

### Rollback Pattern

```bash
# 1. Roll back code to last known good commit (including submodule SHAs)
git reset --hard <GOOD_COMMIT_SHA>
git submodule update --init --recursive

# 2. Restore DB snapshot (recommended) or uninstall specific modules
docker exec -it postgres pg_dump -U odoo odoo_core > backup_before_rollback.sql

# 3. Restart
docker compose restart odoo-core

# 4. If needed, uninstall problematic module
docker exec -it odoo-core odoo -d odoo_core \
  --uninstall=<module_name> \
  --stop-after-init
```

---

## 8. Module Selection Reference

### OCA Repository to Module Mapping

| Repository | Key Modules | Purpose |
|------------|-------------|---------|
| `server-tools` | `base_exception`, `auditlog`, `module_auto_update` | Admin utilities |
| `server-ux` | `date_range`, `base_tier_validation` | UX + approval workflows |
| `server-backend` | `base_user_role` | Role-based access control |
| `web` | `web_responsive`, `web_dialog_size`, `web_m2x_options` | UI enhancements |
| `queue` | `queue_job`, `queue_job_cron` | Async job processing |
| `sale-workflow` | `sale_order_type`, `sale_order_line_sequence` | Sales enhancements |
| `account-financial-tools` | `account_lock_date`, `account_fiscal_year` | Accounting utilities |
| `account-financial-reporting` | `account_financial_report` | Trial balance, aging reports |
| `account-reconcile` | `account_reconcile_oca` | Bank reconciliation |
| `mis-builder` | `mis_builder`, `mis_builder_budget` | KPI matrix reports |
| `reporting-engine` | `report_xlsx`, `bi_sql_editor` | Reporting tools |
| `rest-framework` | `base_rest`, `base_rest_pydantic` | REST API layer |
| `dms` | `dms`, `dms_field` | Document management |
| `knowledge` | `document_page`, `document_page_approval` | Wiki/knowledge base |

### This Repo's oca.lock.json

The full curated list with all repositories and modules is maintained in:

- **Root lock file**: `/oca.lock.json`
- **OCA manifest**: `/addons/oca/manifest.yaml`

---

## 9. Risks and Notes

| Risk | Mitigation |
|------|------------|
| "Install all OCA" creates conflicts | Only install from curated list in `oca.lock.json` |
| Floating `git pull` breaks production | Pin to submodule SHAs or specific commits |
| Enterprise replacement gaps | Use `addons/oca/manifest.yaml` for parity mapping |
| Module conflicts on upgrade | Test each tier in staging before production |
| Missing dependencies on install | Follow tier installation order (0 → 12) |

---

## 10. Quick Reference

```bash
# View curated OCA repos
cat oca.lock.json | jq '.repositories | keys'

# Check installed OCA modules
docker exec -it postgres psql -U odoo -d odoo_core -c "
  SELECT name, state FROM ir_module_module
  WHERE author ILIKE '%OCA%' AND state = 'installed'
  ORDER BY name;
"

# Install single OCA module
docker exec -it odoo-core odoo -d odoo_core -i <module_name> --stop-after-init

# Update OCA module
docker exec -it odoo-core odoo -d odoo_core -u <module_name> --stop-after-init

# Sync submodules
git submodule sync --recursive && git submodule update --init --recursive

# Health check
curl -s -o /dev/null -w "%{http_code}" http://localhost:8069/web/health
```

---

## 11. Related Documentation

| Document | Path | Purpose |
|----------|------|---------|
| OCA Style Contract | `/docs/OCA_STYLE_CONTRACT.md` | Module naming, layout conventions |
| Finance PPM OCA Guide | `/docs/finance-ppm/OCA_INSTALLATION_GUIDE.md` | Finance-specific OCA modules |
| CE/OCA Project Stack | `/docs/CE_OCA_PROJECT_STACK.md` | Full stack architecture |
| Enterprise Parity | `/docs/ODOO_18_EE_TO_CE_OCA_PARITY.md` | Enterprise to CE/OCA mapping |
| OCA Chore Scope | `/docs/OCA_CHORE_SCOPE.md` | Commit scope conventions |

---

**Version**: 1.0.0
**Last Updated**: 2026-01-20
**Branch**: 18.0
