# Odoo Runtime Identifiers - Canonical Reference

**Generated**: 2026-01-10T17:25:00Z
**Source**: Production runtime introspection (178.128.112.214)
**Purpose**: Single source of truth for all deployment/debugging commands

---

## Quick Copy-Paste Targets

### Docker Container Names

```bash
# Primary Odoo container
ODOO_CONTAINER="odoo-prod"

# Supporting services
NGINX_CONTAINER="nginx-prod-v2"
N8N_CONTAINER="c95d05274029_n8n-prod"
SUPERSET_CONTAINER="8ce7c585a4e2_superset-prod"
OCR_CONTAINER="ocr-prod"
AUTH_CONTAINER="auth-prod"
MCP_CONTAINER="mcp-prod"
```

### Database Identifiers

```bash
# PostgreSQL (External - DigitalOcean Managed)
DB_HOST="private-odoo-db-sgp1-do-user-27714628-0.g.db.ondigitalocean.com"
DB_PORT="25060"
DB_USER="doadmin"
DB_NAME="odoo"
DB_FILTER="^odoo$"

# No local PostgreSQL container - all DB operations go through external host
```

### File System Paths

```bash
# Host paths
REPO_ROOT="/opt/odoo-ce/repo"
ADDONS_HOST="/opt/odoo-ce/repo/addons"
ODOO_CONF_HOST="/opt/odoo-ce/repo/deploy/odoo.conf"

# Container paths
ADDONS_CONTAINER="/mnt/extra-addons"
ODOO_CONF_CONTAINER="/etc/odoo/odoo.conf"
ODOO_DATA_CONTAINER="/var/lib/odoo"
```

### Addon Namespaces

```bash
# Main ipai namespace (85 modules)
IPAI_MODULES_DIR="/mnt/extra-addons/ipai"

# OCA vendor repositories (14 repos, empty)
OCA_REPOS_DIR="/mnt/extra-addons/OCA"

# Standalone modules (deployed at root level)
# Examples: ipai_theme_tbwa, ipai_ask_ai, ipai_bir_tax_compliance
STANDALONE_DIR="/mnt/extra-addons"

# Core Odoo addons
CORE_ADDONS="/usr/lib/python3/dist-packages/odoo/addons"
```

### System Users

```bash
# Container runtime user
ODOO_USER="odoo"
ODOO_UID=100
ODOO_GID=101

# Host repository owner
HOST_USER="root"
HOST_UID=0
```

### URLs & Endpoints

```bash
# Public access
PUBLIC_URL="https://erp.insightpulseai.com"
LOGIN_URL="https://erp.insightpulseai.com/web/login"

# Direct IP access (behind nginx)
DIRECT_URL="http://178.128.112.214:8069"
LONGPOLLING_URL="http://178.128.112.214:8072"

# Health checks
# Note: version_info requires authentication, use login endpoint for health
curl -sI https://erp.insightpulseai.com/web/login
```

---

## Common Operations

### Connect to Container

```bash
ssh root@178.128.112.214
docker exec -it odoo-prod bash
```

### Check Odoo Version

```bash
docker exec odoo-prod odoo --version
# Output: Odoo Server 18.0-20251222
```

### List Installed Modules

```bash
docker exec odoo-prod bash -lc "PGPASSWORD=\$(grep db_password /etc/odoo/odoo.conf | cut -d= -f2 | xargs) psql -h private-odoo-db-sgp1-do-user-27714628-0.g.db.ondigitalocean.com -p 25060 -U doadmin -d odoo -t -c \"SELECT name FROM ir_module_module WHERE state = 'installed' ORDER BY name;\""
```

### Upgrade Module

```bash
docker exec odoo-prod odoo -d odoo -u <module_name> --workers=0 --stop-after-init
```

### Restart Odoo

```bash
docker restart odoo-prod
```

### Check Permissions

```bash
# Run permission verification script
./scripts/verify-addon-permissions.sh

# Manual check
ssh root@178.128.112.214
ls -la /opt/odoo-ce/repo/addons/ipai_theme_*
# Should show: drwxr-xr-x odoo odoo (or dhcpcd messagebus on host, same UID 100:101)
```

### Deploy Modules

```bash
# Using deployment script (auto-sets permissions)
./scripts/deploy-odoo-modules.sh <module_name>

# Manual rsync (discouraged, no permission fix)
rsync -avz addons/ipai_module/ root@178.128.112.214:/opt/odoo-ce/repo/addons/ipai_module/
```

---

## Addon Path Resolution Order

Odoo searches for modules in this order:

1. `/usr/lib/python3/dist-packages/odoo/addons` (Core Odoo)
2. `/var/lib/odoo/addons/18.0` (User-installed from Apps menu)
3. `/mnt/extra-addons` (Custom addons mount)
   - `/mnt/extra-addons/ipai/` (Main ipai namespace - 85 modules)
   - `/mnt/extra-addons/OCA/` (OCA repositories - empty)
   - `/mnt/extra-addons/ipai_*` (Standalone modules - 31 modules)

**Conflict Resolution**: Earlier paths win. If `ipai_expense` exists in both `ipai/` and standalone, the first found is used.

---

## Database Connection

### Connection String Format

```bash
postgresql://doadmin:<PASSWORD>@private-odoo-db-sgp1-do-user-27714628-0.g.db.ondigitalocean.com:25060/odoo?sslmode=require
```

### Extract Password from Config

```bash
docker exec odoo-prod bash -lc 'grep db_password /etc/odoo/odoo.conf | cut -d= -f2 | xargs'
```

### Connect via psql

```bash
# From within container
docker exec -it odoo-prod bash
PGPASSWORD=$(grep db_password /etc/odoo/odoo.conf | cut -d= -f2 | xargs)
psql -h private-odoo-db-sgp1-do-user-27714628-0.g.db.ondigitalocean.com -p 25060 -U doadmin -d odoo

# Or one-liner from host
ssh root@178.128.112.214 "docker exec odoo-prod bash -lc 'PGPASSWORD=\$(grep db_password /etc/odoo/odoo.conf | cut -d= -f2 | xargs) psql -h private-odoo-db-sgp1-do-user-27714628-0.g.db.ondigitalocean.com -p 25060 -U doadmin -d odoo'"
```

---

## Known Pitfalls

### 1. Wrong Database Name

**Symptom**: Commands reference `odoo_core` but actual DB is `odoo`
**Fix**: Always use `DB_NAME="odoo"` (verified via `dbfilter = ^odoo$`)

### 2. Permission Errors on SCSS Assets

**Symptom**: "Style compilation failed" in Odoo logs
**Root Cause**: Files owned by wrong user (not UID 100:101)
**Fix**: Run `./scripts/verify-addon-permissions.sh` or manual `chown -R 100:101`

### 3. Module Not Found After Deployment

**Symptom**: Module appears in file system but Odoo can't find it
**Causes**:
- Missing `__manifest__.py`
- Wrong permissions (not readable by odoo user)
- Not in `addons_path` (verify `/mnt/extra-addons` is listed)
- Odoo needs restart after new module addition

**Fix**:
```bash
# Verify manifest exists
docker exec odoo-prod ls -la /mnt/extra-addons/ipai/<module>/__manifest__.py

# Verify permissions
docker exec odoo-prod ls -ld /mnt/extra-addons/ipai/<module>

# Restart Odoo
docker restart odoo-prod

# Update apps list in Odoo UI: Apps → Update Apps List
```

### 4. Multiple Module Copies (Namespace Pollution)

**Symptom**: Same module exists in both `ipai/` and root level
**Example**: `ipai/ipai_theme_tbwa` AND `ipai_theme_tbwa` (standalone)

**Detection**:
```bash
docker exec odoo-prod find /mnt/extra-addons -name "ipai_theme_tbwa" -type d
```

**Fix**: Remove duplicate from standalone, keep only in `ipai/` namespace

### 5. OCA Modules Not Available

**Current State**: OCA repo directories exist but are empty
**Consequence**: No OCA modules available despite directory structure
**Fix**: If OCA modules needed, populate repos via git submodule or manual install

---

## Installed Modules (Confirmed)

Current production installation includes only 4 IPAI modules:

1. `ipai_ask_ai_chatter` - AI chat integration
2. `ipai_platform_theme` - Platform theme base
3. `ipai_theme_tbwa_backend` - TBWA backend theme
4. `ipai_web_theme_chatgpt` - ChatGPT-style theme

**Note**: 85 modules available in `ipai/` namespace, but only 4 installed. Most modules are uninstalled/available for deployment.

---

## Deployment Workflow

### Standard Deployment

1. Develop module locally in `addons/ipai/<module>/`
2. Test locally via docker-compose
3. Deploy to production:
   ```bash
   ./scripts/deploy-odoo-modules.sh <module_name>
   ```
4. Script automatically:
   - Validates module locally
   - Rsyncs to production
   - **Fixes permissions** (chown 100:101, chmod 755)
   - Restarts Odoo container
5. Install/upgrade via Odoo UI or CLI

### Emergency Permission Fix

If SCSS assets fail to compile:
```bash
./scripts/verify-addon-permissions.sh
```

This script:
- Scans for incorrect ownership
- Fixes permissions automatically
- Verifies fix completion

---

## Version Information

- **Odoo Version**: 18.0-20251222
- **OS**: Ubuntu 24.04 LTS (Kernel 6.8.0-71-generic)
- **Docker Engine**: Active
- **PostgreSQL**: DigitalOcean Managed PostgreSQL 15
- **Python**: 3.x (bundled with odoo:18.0 image)
- **Nginx**: 1.29.4 (nginx-prod-v2)

---

## Maintenance Schedules

### No Scheduled Jobs Detected

No cron jobs or systemd timers found that modify addon filesystem ownership.

**Implication**: Permission fixes are persistent until next manual deployment.

---

## References

- **JSON Schema**: `docs/architecture/runtime_identifiers.json`
- **Raw Probe Log**: `docs/architecture/odoo_runtime_probe.log`
- **Production Snapshot**: `docs/architecture/PROD_RUNTIME_SNAPSHOT.md`
- **Deployment Scripts**: `scripts/deploy-odoo-modules.sh`, `scripts/verify-addon-permissions.sh`

---

*Last Updated: 2026-01-10T17:25:00Z*
*Generated by: Odoo Ecosystem Introspector*
