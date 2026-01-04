# Odoo Addons Path Configuration Guide

**Version:** 1.0.0
**Last Updated:** 2025-01-04
**Purpose:** Guide for configuring and managing Odoo CE addons paths for module discovery and installation

---

## Overview

Odoo apps (modules) are discovered based on the **addons paths** (`addons_path`) configuration. If an app shows up in the Apps list, its module folder exists in one of the directories specified in `addons_path` (official core, OCA repos, or custom `ipai_*` modules).

**Key Insight:** You don't "point to a domain" for apps. You point to **filesystem paths** via `addons_path` (mounted directories or baked into the image). Module installs/upgrades happen by:
1. Ensuring module code is present in `addons_path`
2. Running `odoo -u <module>` (or via UI "Upgrade")

---

## 1. Identify Current Addons Path Configuration

### Check odoo.conf and Environment Variables

Run this inside the Odoo container to print the effective addons paths:

```bash
docker exec -it odoo-erp-prod bash -lc '
  set -e
  echo "=== odoo.conf ==="
  grep -nE "^(addons_path|data_dir|db_|proxy_mode|server_wide_modules)" /etc/odoo/odoo.conf || true
  echo
  echo "=== env ==="
  env | grep -E "ODOO|ADDONS|PATH" || true
'
```

### Check Module Locations

Verify whether specific modules exist on disk:

```bash
docker exec -it odoo-erp-prod bash -lc '
  set -e
  for m in timesheet_grid planning helpdesk sign sale_subscription; do
    echo "=== $m ==="
    python3 - <<PY
import glob
paths = []
# Common addon roots (adjust if yours differ)
roots = [
  "/usr/lib/python3/dist-packages/odoo/addons",
  "/opt/odoo/addons",
  "/mnt/extra-addons",
  "/mnt/oca",
  "/mnt/ipai",
]
for r in roots:
  paths += glob.glob(r + "/" + "'"$m"'" + "/__manifest__.py")
print("\\n".join(paths) if paths else "NOT FOUND")
PY
  done
'
```

If modules are found, that's the exact directory/repo currently providing them.

---

## 2. Canonical Addons Path Configuration

### Recommended Mount Layout

| Path | Purpose |
|------|---------|
| `/opt/odoo/odoo/addons` | Odoo CE core addons |
| `/mnt/oca/<repo>` | OCA repos |
| `/mnt/ipai` | Custom `ipai_*` addons |

### Example odoo.conf

```ini
[options]
addons_path = /opt/odoo/odoo/addons,/mnt/oca,/mnt/ipai
data_dir = /var/lib/odoo
proxy_mode = True
```

### Example docker-compose.yml Service

```yaml
services:
  odoo:
    image: ghcr.io/jgtolentino/odoo-ce:18.0
    volumes:
      - ./odoo.conf:/etc/odoo/odoo.conf:ro
      - ./addons/ipai:/mnt/ipai:ro
      - ./addons/oca:/mnt/oca:ro
      - odoo_data:/var/lib/odoo
    environment:
      - ODOO_RC=/etc/odoo/odoo.conf
```

> **Note:** For install/upgrade capability in prod without rebuilding images, remove `:ro` for addon mounts. For immutable/prod-safe deployments, keep `:ro` and rebuild images for upgrades.

---

## 3. Git-Pinned OCA Repository Management

### Recommended Repo Layout

```text
odoo-ce/
  docker/
  odoo.conf
  addons/
    ipai/                 # custom modules
      ipai_workos_core/
      ipai_month_end/
      ...
    oca/                  # OCA repos as git submodules
      OCA/web/
      OCA/server-tools/
      OCA/account-financial-tools/
      ...
  scripts/
    upgrade_modules.sh
```

### Pin OCA Repos as Git Submodules

```bash
# Add OCA repos as submodules
git submodule add https://github.com/OCA/web.git addons/oca/OCA/web
git submodule add https://github.com/OCA/server-tools.git addons/oca/OCA/server-tools
git submodule add https://github.com/OCA/account-financial-tools.git addons/oca/OCA/account-financial-tools

# Initialize submodules
git submodule update --init --recursive
```

### Deterministic Upgrade Flow

1. Pull repo + update submodules
2. Rebuild image (if immutable) or restart container (if bind mounts)
3. Run Odoo module updates (`-u`) against the DB
4. Verify logs + module states

---

## 4. Module Installation & Upgrade Commands

### Install or Upgrade Single Module

```bash
docker exec -it odoo-erp-prod bash -lc '
  set -e
  odoo -c /etc/odoo/odoo.conf -d YOUR_DB -u ipai_workos_core --stop-after-init
'
```

### Batch Upgrade IPAI Modules

```bash
docker exec -it odoo-erp-prod bash -lc '
  set -e
  MODS=$(psql "$PGURI" -Atc "select name from ir_module_module where name like '\''ipai_%'\'' and state in ('\''installed'\'','\''to upgrade'\'');" | paste -sd, -)
  echo "Updating: $MODS"
  [ -n "$MODS" ] && odoo -c /etc/odoo/odoo.conf -d YOUR_DB -u "$MODS" --stop-after-init || echo "No ipai_* modules to update"
'
```

### Verify Module States

```bash
docker exec -it odoo-erp-prod bash -lc '
  set -e
  psql "$PGURI" -c "
    select name, state, latest_version
    from ir_module_module
    where name in (
      '\''ipai_workos_affine'\'','\''ipai_workos_core'\'','\''ipai_finance_ppm'\'','\''ipai_month_end'\''
    )
    order by name;"
'
```

### Common Module States

| State | Description |
|-------|-------------|
| `installed` | Module is installed and running |
| `uninstalled` | Module available but not installed |
| `to upgrade` | Module marked for upgrade |
| `to install` | Module marked for installation |
| `to remove` | Module marked for removal |

---

## 5. Current Production Configuration

As captured in `docs/runtime/ADDONS_PATH.prod.txt`:

```ini
addons_path = /usr/lib/python3/dist-packages/odoo/addons,/mnt/addons/ipai,/mnt/addons/oca
```

This configuration provides:
- **CE Core:** `/usr/lib/python3/dist-packages/odoo/addons`
- **IPAI Custom:** `/mnt/addons/ipai`
- **OCA Modules:** `/mnt/addons/oca`

---

## 6. Troubleshooting

### Module Not Found in Apps List

**Cause:** Module not in any `addons_path` directory

**Solution:**
1. Verify module exists: `ls -la /mnt/ipai/<module_name>/__manifest__.py`
2. Check `addons_path` includes the parent directory
3. Restart Odoo after path changes
4. Click "Update Apps List" in Odoo UI

### Enterprise Module in CE Instance

**Cause:** Module depends on Enterprise-only features

**Solution:**
1. Check manifest: `grep -r "OEEL" /mnt/ipai/<module_name>`
2. Find CE/OCA alternative (see `docs/ODOO18_ENTERPRISE_TO_CE_OCA_MAPPING.md`)
3. Remove Enterprise dependencies

### Addons Path Not Taking Effect

**Cause:** Container using cached config or wrong config file

**Solution:**
1. Verify `ODOO_RC` env var points to correct config
2. Check volume mount is correct in docker-compose
3. Restart container (not just reload)

---

## 7. Best Practices

1. **Use explicit addons paths** - Don't rely on auto-discovery
2. **Pin OCA repos** - Use git submodules for reproducibility
3. **Mount read-only in prod** - Use `:ro` for immutable deployments
4. **Document your paths** - Keep `docs/runtime/ADDONS_PATH.prod.txt` updated
5. **Separate concerns** - Core, OCA, and custom in different paths
6. **Version lock** - Specify OCA repo branches matching Odoo version (18.0)

---

## Related Documentation

- **Module Deployment:** `docs/ODOO_MODULE_DEPLOYMENT.md`
- **Enterprise to CE Mapping:** `docs/ODOO18_ENTERPRISE_TO_CE_OCA_MAPPING.md`
- **OCA Migration:** `docs/OCA_MIGRATION.md`
- **Runtime Addons Path:** `docs/runtime/ADDONS_PATH.prod.txt`
- **Image Specification:** `docs/ODOO_IMAGE_SPEC.md`

---

**Document Version:** 1.0.0
**Last Review:** 2025-01-04
**Next Review:** Quarterly
