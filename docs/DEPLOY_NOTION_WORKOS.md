# Deploy Notion/Work OS Modules

This document describes how to deploy the IPAI Work OS (Notion Clone) module suite to production.

## Module List

The Work OS suite consists of the following modules:

| Module | Description |
|--------|-------------|
| `ipai_platform_permissions` | Scope-based permission management |
| `ipai_platform_audit` | Activity logging and audit trail |
| `ipai_workos_core` | Workspace, space, and page hierarchy |
| `ipai_workos_blocks` | Block editor with 14 block types |
| `ipai_workos_db` | Database with typed properties |
| `ipai_workos_views` | Table, kanban, calendar views |
| `ipai_workos_templates` | Page and database templates |
| `ipai_workos_collab` | Comments and @mentions |
| `ipai_workos_search` | Global and scoped search |
| `ipai_workos_canvas` | Edgeless canvas (AFFiNE-style) |
| `ipai_workos_affine` | Umbrella module (installs all) |

## Prerequisites

- Odoo CE 18.0 running
- PostgreSQL 15+
- Docker Compose (for containerized deployments)

## Deployment Steps

### 1. Pull Latest Changes

```bash
cd /opt/odoo-ce
git fetch origin main
git checkout main
git pull origin main
```

### 2. Update Addons Path

Ensure `deploy/odoo.conf` includes the addons directory:

```ini
[options]
addons_path = /opt/odoo-ce/addons,/opt/odoo-ce/addons/oca,/opt/odoo/addons
```

### 3. Install/Update Modules

**Option A: Install umbrella module (recommended)**

```bash
docker compose run --rm odoo-web \
  odoo --stop-after-init \
  -d $ODOO_DB \
  -i ipai_workos_affine
```

**Option B: Install individual modules**

```bash
docker compose run --rm odoo-web \
  odoo --stop-after-init \
  -d $ODOO_DB \
  -i ipai_workos_core,ipai_workos_blocks,ipai_workos_db
```

**Option C: Update existing modules**

```bash
docker compose run --rm odoo-web \
  odoo --stop-after-init \
  -d $ODOO_DB \
  -u ipai_workos_affine
```

### 4. Restart Services

```bash
docker compose down
docker compose up -d
```

### 5. Verify Installation

```bash
# Check health
curl -s http://localhost:8069/web/health | jq .

# Check logs
docker compose logs -f --tail=100 odoo-web
```

## Rollback Procedure

If issues are encountered:

### 1. Revert Code Changes

```bash
cd /opt/odoo-ce
git log --oneline -5  # Find the previous commit
git revert HEAD       # Or: git checkout <previous-commit>
```

### 2. Uninstall Modules (if needed)

```bash
docker compose run --rm odoo-web \
  odoo --stop-after-init \
  -d $ODOO_DB \
  --uninstall ipai_workos_affine
```

### 3. Restart Services

```bash
docker compose restart
```

## Production Deployment for erp.insightpulseai.net

### Full Deploy Command Sequence

```bash
# 1. SSH into production server
ssh deploy@erp.insightpulseai.net

# 2. Navigate to Odoo directory
cd /opt/odoo-ce

# 3. Pull latest changes
git fetch origin main
git checkout main
git pull origin main

# 4. Stop services gracefully
docker compose down

# 5. Install/update Work OS modules
docker compose run --rm odoo-web \
  odoo --stop-after-init \
  -d odoo_prod \
  -u ipai_workos_affine

# 6. Start services
docker compose up -d

# 7. Verify health
sleep 10
curl -s https://erp.insightpulseai.net/web/health

# 8. Monitor logs
docker compose logs -f --tail=100 odoo-web
```

### Health Checks

- **Web UI**: https://erp.insightpulseai.net/web
- **Health endpoint**: https://erp.insightpulseai.net/web/health
- **Metrics**: Check `docker stats` for resource usage

## Troubleshooting

### Module Not Found

```bash
# Check if module exists
ls -la addons/ipai_workos_*

# Verify addons_path in config
grep addons_path deploy/odoo.conf
```

### Database Migration Errors

```bash
# Check Odoo logs
docker compose logs odoo-web | grep -i error

# Connect to database
docker compose exec db psql -U odoo -d odoo_prod
```

### Permission Issues

```bash
# Fix file permissions
sudo chown -R 1000:1000 addons/
```

## Parity Audit

Run parity audit after deployment to verify module state:

```bash
python3 tools/parity/parity_audit.py
```

Expected output shows P0 capabilities at scaffold level (score based on module existence).

## Repository Structure

This deployment uses the **flat structure** (canonical):

```
addons/
├── ipai_workos_core/
├── ipai_workos_blocks/
├── ipai_workos_db/
├── ipai_workos_views/
├── ipai_workos_templates/
├── ipai_workos_collab/
├── ipai_workos_search/
├── ipai_workos_canvas/
├── ipai_workos_affine/
├── ipai_platform_permissions/
├── ipai_platform_audit/
└── oca/
```

Do **NOT** restructure repository (forbidden layouts include paths like `src/apps/odoo/addons/`).
