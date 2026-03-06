# Odoo CE 19 + OCA + IPAI Enterprise Bridge - Consumer Guide

> **Image**: `ghcr.io/jgtolentino/odoo-ce:19.0-ee-parity`
> **License**: LGPL-3.0 (100% open source)
> **NO** proprietary Odoo EE code is used.

## Quick Start

### 1. Pull the Image

```bash
# Production tag
docker pull ghcr.io/jgtolentino/odoo-ce:19.0-ee-parity

# Edge/development tag
docker pull ghcr.io/jgtolentino/odoo-ce:edge-19-ee-parity
```

### 2. Run with Docker Compose (Recommended)

```bash
# From repo root
docker compose -f docker/docker-compose.ce19.yml up -d
```

### 3. Run with Docker CLI

```bash
# Create network
docker network create odoo-ce19-ee-net || true

# Start PostgreSQL
docker run -d --name odoo_ce19_db \
  --network odoo-ce19-ee-net \
  -e POSTGRES_DB=odoo_ce19 \
  -e POSTGRES_USER=odoo \
  -e POSTGRES_PASSWORD=odoo \
  -v odoo_ce19_pgdata:/var/lib/postgresql/data \
  postgres:16

# Start Odoo CE 19 EE Parity
docker run -d --name odoo_ce19_ee_parity \
  --network odoo-ce19-ee-net \
  -p 8069:8069 \
  -e HOST=odoo_ce19_db \
  -e PORT=5432 \
  -e USER=odoo \
  -e PASSWORD=odoo \
  ghcr.io/jgtolentino/odoo-ce:19.0-ee-parity
```

### 4. Verify

```bash
# Check container status
docker ps --filter name=odoo_ce19

# View logs
docker logs -f odoo_ce19_ee_parity

# HTTP health check
curl -I http://localhost:8069/web/health

# Module install test
docker exec -it odoo_ce19_ee_parity \
  odoo -d odoo_ce19 --stop-after-init -i base,ipai_enterprise_bridge
```

## Available Tags

| Tag | Use Case | Stability |
|-----|----------|-----------|
| `19.0-ee-parity` | Production | Stable, updated on releases |
| `edge-19-ee-parity` | Development | Updated on every main push |
| `19.0-ee-parity-sha-<sha>` | Pinned deployment | Immutable, CI-generated |
| `<version>-ee-parity` | Versioned release | Immutable (e.g., `19.0.1-ee-parity`) |

**For production, always use immutable tags (SHA or versioned).**

## Image Contents

### Base
- `odoo:19.0` - Official Odoo CE 19.0 image

### OCA Modules (22 repos, flattened to `/mnt/addons/oca`)
- `account-financial-reporting` - Financial reports
- `account-financial-tools` - Asset management, budgets
- `account-reconcile` - Bank reconciliation (EE parity)
- `server-auth` - SSO/OAuth (auth_oidc, auth_oauth)
- `server-tools` - Utilities (module_auto_update, etc.)
- `server-ux` - Approvals (base_tier_validation)
- `web` - UX enhancements (web_responsive)
- `project` - Project timeline, templates
- `hr`, `timesheet` - HR planning, timesheet grid
- `helpdesk` - Helpdesk management
- `dms`, `knowledge` - Document/knowledge management
- See `vendor/oca.lock.ce19.json` for full list

### IPAI Enterprise Bridge (`/mnt/addons/ipai`)
- `ipai_enterprise_bridge` - Thin EE-style glue layer
- `ipai_finance_ppm` - Finance/PPM features
- `ipai_hr_payroll_ph` - Philippines payroll (100% EE parity)
- `ipai_helpdesk` - Enhanced helpdesk
- `ipai_approvals` - Approval workflows
- `ipai_expense_ocr` - Expense OCR
- 30+ IPAI modules total

### Addons Path
```
/usr/lib/python3/dist-packages/odoo/addons  # CE core
/mnt/addons/ipai                            # IPAI enterprise bridge
/mnt/addons/oca                             # OCA modules (flattened)
```

## EE Parity Coverage

| Priority | Feature Area | Parity % | Key Module |
|----------|--------------|----------|------------|
| P0 | Bank Reconciliation | 95% | `account_reconcile_oca` |
| P0 | Financial Reports | 90% | `account_financial_report` |
| P0 | Asset Management | 90% | `account_asset_management` |
| P0 | Philippines Payroll | 100% | `ipai_hr_payroll_ph` |
| P0 | BIR Tax Compliance | 100% | `ipai_finance_bir_compliance` |
| P1 | Helpdesk | 90% | `helpdesk_mgmt` + `ipai_helpdesk` |
| P1 | Planning | 85% | `project_timeline` |
| P1 | Timesheet Grid | 85% | `hr_timesheet_sheet` |
| P2 | Documents/DMS | 80% | `dms` + `ipai_documents_ai` |
| P2 | Knowledge Base | 75% | `knowledge` |

**Weighted parity score: ~88%** (Target: ≥80%)

See `docs/ee_parity_map.md` for complete mapping.

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST` | `db` | PostgreSQL host |
| `PORT` | `5432` | PostgreSQL port |
| `USER` | `odoo` | PostgreSQL user |
| `PASSWORD` | `odoo` | PostgreSQL password |
| `DB` | `odoo` | Default database name |
| `ODOO_RC` | `/etc/odoo/odoo.conf` | Config file path |

## Upgrade Process

### Standard Upgrade (Tag to Tag)

```bash
# Pull new image
docker pull ghcr.io/jgtolentino/odoo-ce:19.0-ee-parity

# Stop and remove old container
docker stop odoo_ce19_ee_parity
docker rm odoo_ce19_ee_parity

# Start with new image
docker run -d --name odoo_ce19_ee_parity \
  --network odoo-ce19-ee-net \
  -p 8069:8069 \
  -e HOST=odoo_ce19_db \
  -e PORT=5432 \
  -e USER=odoo \
  -e PASSWORD=odoo \
  ghcr.io/jgtolentino/odoo-ce:19.0-ee-parity

# Update modules
docker exec -it odoo_ce19_ee_parity \
  odoo -d odoo_ce19 --stop-after-init -u all
```

### Pinned Upgrade (SHA to SHA)

```bash
# Pull specific SHA
docker pull ghcr.io/jgtolentino/odoo-ce:19.0-ee-parity-sha-abc1234

# Deploy with exact tag
docker run -d --name odoo_ce19_ee_parity \
  ... \
  ghcr.io/jgtolentino/odoo-ce:19.0-ee-parity-sha-abc1234
```

## Rollback

### Quick Rollback

```bash
# Tag current as "prev" before upgrading
docker tag ghcr.io/jgtolentino/odoo-ce:19.0-ee-parity \
           ghcr.io/jgtolentino/odoo-ce:19.0-ee-parity-prev

# If upgrade fails, rollback:
docker rm -f odoo_ce19_ee_parity

docker run -d --name odoo_ce19_ee_parity \
  --network odoo-ce19-ee-net \
  -p 8069:8069 \
  -e HOST=odoo_ce19_db \
  ... \
  ghcr.io/jgtolentino/odoo-ce:19.0-ee-parity-prev
```

### DB Snapshot Rollback

```bash
# Before upgrade, backup DB
docker exec odoo_ce19_db pg_dump -U odoo odoo_ce19 > backup.sql

# If rollback needed:
docker exec -i odoo_ce19_db psql -U odoo odoo_ce19 < backup.sql
```

## Build Scripts

| Script | Purpose |
|--------|---------|
| `docker/build-ce19.sh` | Build image locally |
| `docker/test-ce19.sh` | Run smoke tests |
| `docker/push-ce19.sh` | Push to registry |
| `docker/run-local-ce19.sh` | Run locally (dev) |

## CI/CD

GitHub Actions workflow: `.github/workflows/build-odoo-ce19-ee-parity.yml`

**Triggers:**
- Push to `main` branch (edge build)
- Git tags `v19.*.*` (release build)
- Manual dispatch

**Gates:**
1. Verify OCA lockfile
2. Build image
3. Smoke test (--stop-after-init)
4. Security audit (SBOM + vulnerabilities)
5. Push to GHCR

## Troubleshooting

### Container won't start

```bash
# Check logs
docker logs odoo_ce19_ee_parity

# Common issues:
# - DB connection failed: check HOST/PORT/PASSWORD
# - Module import error: check OCA module compatibility
```

### Module install fails

```bash
# Install with verbose logging
docker exec -it odoo_ce19_ee_parity \
  odoo -d odoo_ce19 --stop-after-init -i <module> --log-level=debug
```

### OCA module conflict

```bash
# Check for duplicate modules
docker exec -it odoo_ce19_ee_parity ls /mnt/addons/oca/

# Verify OCA lockfile
cat vendor/oca.lock.ce19.json | jq '.repos[].modules[]' | sort | uniq -d
```

## Files Reference

| File | Purpose |
|------|---------|
| `docker/Dockerfile.ce19` | Image definition |
| `vendor/oca.lock.ce19.json` | OCA dependency lock |
| `docs/ee_parity_map.md` | EE feature mapping |
| `addons/ipai/ipai_enterprise_bridge/` | Bridge module source |

## Support

- Issues: https://github.com/jgtolentino/odoo-ce/issues
- Documentation: `docs/` directory
- EE Parity Strategy: `docs/ee_parity_map.md`

---

*Image Version: 19.0.1.0.0*
*Last Updated: 2026-01-28*
