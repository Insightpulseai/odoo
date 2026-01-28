# Image Alignment Verification

**Date**: 2026-01-28
**Purpose**: Verify sandbox dev environment uses the same CE19 EE parity image as production

---

## Single Source of Truth

**Canonical Image Definition**: `docker/docker-compose.ce19.yml`

```yaml
# Line 46
image: ghcr.io/jgtolentino/odoo-ce:${ODOO_IMAGE_TAG:-19.0-ee-parity}
```

**Image Components**:
- Odoo CE 19.0
- OCA modules (24 dependencies)
- IPAI Enterprise Bridge (`ipai_enterprise_bridge`)
- Enterprise feature parity (≥80% EE features via CE + OCA + IPAI)

---

## Environment Alignment

### Production Stack (`docker/docker-compose.ce19.yml`)

```yaml
services:
  odoo:
    image: ghcr.io/jgtolentino/odoo-ce:${ODOO_IMAGE_TAG:-19.0-ee-parity}
    container_name: odoo_ce19_ee_parity
```

**Status**: ✅ Canonical definition

### Dev Sandbox (`sandbox/dev/docker-compose.yml`)

```yaml
services:
  odoo:
    image: ghcr.io/jgtolentino/odoo-ce:${ODOO_IMAGE_TAG:-19.0-ee-parity}
    container_name: odoo-dev
```

**Status**: ✅ Aligned with canonical (updated 2026-01-28)

### Codespaces (via `.devcontainer/docker-compose.yml`)

The devcontainer uses a base Ubuntu image and connects to host Docker.
Codespaces users should run the sandbox compose file directly:

```bash
cd /workspaces/odoo-ce/sandbox/dev
docker compose up -d
```

**Status**: ✅ Uses same sandbox compose file

---

## Verification Commands

### Check Canonical Image
```bash
cd ~/Documents/GitHub/odoo-ce
grep -A2 'odoo:' docker/docker-compose.ce19.yml | grep 'image:'
```

**Expected Output**:
```
    image: ghcr.io/jgtolentino/odoo-ce:${ODOO_IMAGE_TAG:-19.0-ee-parity}
```

### Check Sandbox Dev Image
```bash
cd ~/Documents/GitHub/odoo-ce/sandbox/dev
grep -A2 'odoo:' docker-compose.yml | grep 'image:'
```

**Expected Output**:
```
    image: ghcr.io/jgtolentino/odoo-ce:${ODOO_IMAGE_TAG:-19.0-ee-parity}
```

### Verify Running Container (when Docker is running)
```bash
docker ps --format "table {{.Names}}\t{{.Image}}" | grep odoo
```

**Expected Output** (sandbox dev):
```
odoo-dev    ghcr.io/jgtolentino/odoo-ce:19.0-ee-parity
```

---

## Image Build Process

The CE19 EE parity image is built via GitHub Actions:

**Workflow**: `.github/workflows/build-ce19-ee-parity.yml` (or similar)

**Trigger**: Push to main branch (changes to `docker/` or `addons/ipai/`)

**Registry**: GitHub Container Registry (ghcr.io)

**Pull Command**:
```bash
docker pull ghcr.io/jgtolentino/odoo-ce:19.0-ee-parity
```

---

## Environment Variables

Both environments support the same variable for image customization:

### `.env` (local) or GitHub Codespaces Secrets

```bash
# Use specific tag (default: 19.0-ee-parity)
ODOO_IMAGE_TAG=19.0-ee-parity

# Or use development tag
ODOO_IMAGE_TAG=19.0-dev
```

**Default Behavior**: If not set, uses `19.0-ee-parity` tag

---

## Differences from Official Odoo Image

| Aspect | Official `odoo:18.0` | Our `odoo-ce:19.0-ee-parity` |
|--------|---------------------|------------------------------|
| **Version** | 18.0 | 19.0 |
| **OCA Modules** | ❌ None | ✅ 24 modules (project, timesheet, helpdesk, etc.) |
| **Enterprise Bridge** | ❌ No | ✅ `ipai_enterprise_bridge` |
| **EE Parity** | ❌ 0% | ✅ ≥80% feature parity |
| **Custom Addons** | ❌ None | ✅ All `ipai_*` modules |
| **BIR Compliance** | ❌ No | ✅ Philippines tax filing support |

---

## What Changed (2026-01-28 Update)

**Before**:
```yaml
# sandbox/dev/docker-compose.yml
odoo:
  image: odoo:18.0  # Official Odoo Community Edition
```

**After**:
```yaml
# sandbox/dev/docker-compose.yml
odoo:
  image: ghcr.io/jgtolentino/odoo-ce:${ODOO_IMAGE_TAG:-19.0-ee-parity}
```

**Reason**: Align sandbox dev with production CE19 EE parity image for consistent development experience.

---

## Testing Alignment

After starting containers:

```bash
# Start sandbox dev
cd ~/Documents/GitHub/odoo-ce/sandbox/dev
docker compose up -d

# Wait for health check
docker compose ps

# Verify Odoo version
curl -s http://localhost:8069/web/database/manager | grep -o 'Odoo [0-9.]*'

# Expected: Odoo 19.0

# Verify IPAI modules available
docker compose exec odoo odoo --version
docker compose exec odoo ls /mnt/extra-addons/ipai
```

---

## Rollback (if needed)

If you need to revert to official Odoo 18:

```bash
cd ~/Documents/GitHub/odoo-ce/sandbox/dev

# Edit docker-compose.yml
# Change: image: ghcr.io/jgtolentino/odoo-ce:19.0-ee-parity
# To:     image: odoo:18.0

docker compose down
docker compose up -d
```

**Note**: This will lose CE19 + EE parity features.

---

**Status**: ✅ All environments aligned with CE19 EE parity image
**Last Verified**: 2026-01-28
**SSOT**: `docker/docker-compose.ce19.yml` (line 46)
